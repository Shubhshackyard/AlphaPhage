import os
import logging
import json
import uvicorn
from fastapi import FastAPI, HTTPException, Body, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from embeddings import EmbeddingService
from topic_extractor import TopicExtractor
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AlphaPhage NLP Service",
    description="Provides text embedding and topic extraction capabilities",
    version="1.0.0"
)

# Input/Output models
class TextInput(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = None

class BatchTextInput(BaseModel):
    texts: List[TextInput]

class EmbeddingResponse(BaseModel):
    embedding: List[float]
    text_length: int
    metadata: Optional[Dict[str, Any]] = None

class TopicResponse(BaseModel):
    topic_id: int
    topic_label: str
    confidence: float
    keywords: List[str]
    metadata: Optional[Dict[str, Any]] = None

class BatchEmbeddingResponse(BaseModel):
    embeddings: List[EmbeddingResponse]

class BatchTopicResponse(BaseModel):
    topics: List[TopicResponse]

# Load models on startup
embedding_service = None
topic_extractor = None

@app.on_event("startup")
async def startup_event():
    global embedding_service, topic_extractor
    try:
        logger.info(json.dumps({"event": "loading_embedding_model"}))
        embedding_service = EmbeddingService(Config.MODEL_NAME)
        
        logger.info(json.dumps({"event": "loading_topic_model"}))
        topic_extractor = TopicExtractor()
        
        logger.info(json.dumps({"event": "models_loaded_successfully"}))
    except Exception as e:
        logger.error(json.dumps({"event": "model_loading_error", "error": str(e)}))
        raise

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "models_loaded": embedding_service is not None and topic_extractor is not None
    }

@app.post("/embed", response_model=EmbeddingResponse)
async def get_embedding(text_input: TextInput):
    try:
        if not embedding_service:
            raise HTTPException(status_code=503, detail="Embedding model not loaded")
        
        embedding = embedding_service.generate_embeddings(text_input.text)
        
        return EmbeddingResponse(
            embedding=embedding.tolist(),
            text_length=len(text_input.text),
            metadata=text_input.metadata
        )
    except Exception as e:
        logger.error(json.dumps({"event": "embedding_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

@app.post("/embed/batch", response_model=BatchEmbeddingResponse)
async def batch_embed(batch_input: BatchTextInput):
    try:
        if not embedding_service:
            raise HTTPException(status_code=503, detail="Embedding model not loaded")
        
        texts = [item.text for item in batch_input.texts]
        all_embeddings = embedding_service.generate_batch_embeddings(texts, Config.BATCH_SIZE)
        
        results = []
        for i, embedding in enumerate(all_embeddings):
            text_input = batch_input.texts[i]
            results.append(
                EmbeddingResponse(
                    embedding=embedding.tolist(),
                    text_length=len(text_input.text),
                    metadata=text_input.metadata
                )
            )
        
        return BatchEmbeddingResponse(embeddings=results)
    except Exception as e:
        logger.error(json.dumps({"event": "batch_embedding_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail=f"Error generating batch embeddings: {str(e)}")

@app.post("/topic", response_model=TopicResponse)
async def get_topic(text_input: TextInput):
    try:
        if not embedding_service or not topic_extractor:
            raise HTTPException(status_code=503, detail="Models not loaded")
        
        # First generate embedding
        embedding = embedding_service.generate_embeddings(text_input.text)
        
        # Then extract topic
        topic_id, topic_label, confidence, keywords = topic_extractor.extract_topic(text_input.text, embedding)
        
        return TopicResponse(
            topic_id=topic_id,
            topic_label=topic_label,
            confidence=confidence,
            keywords=keywords,
            metadata=text_input.metadata
        )
    except Exception as e:
        logger.error(json.dumps({"event": "topic_extraction_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail=f"Error extracting topic: {str(e)}")

@app.post("/topic/batch", response_model=BatchTopicResponse)
async def batch_extract_topics(batch_input: BatchTextInput):
    try:
        if not embedding_service or not topic_extractor:
            raise HTTPException(status_code=503, detail="Models not loaded")
        
        # Generate all embeddings at once for efficiency
        texts = [item.text for item in batch_input.texts]
        embeddings = embedding_service.generate_batch_embeddings(texts, Config.BATCH_SIZE)
        
        results = []
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            # Extract topic
            topic_id, topic_label, confidence, keywords = topic_extractor.extract_topic(text, embedding)
            
            results.append(
                TopicResponse(
                    topic_id=topic_id,
                    topic_label=topic_label,
                    confidence=confidence,
                    keywords=keywords,
                    metadata=batch_input.texts[i].metadata
                )
            )
        
        return BatchTopicResponse(topics=results)
    except Exception as e:
        logger.error(json.dumps({"event": "batch_topic_extraction_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail=f"Error extracting batch topics: {str(e)}")

@app.post("/update_topic_model")
async def update_topic_model(background_tasks: BackgroundTasks, texts: List[str] = Body(...)):
    """Update the topic model with new texts in the background"""
    try:
        if not topic_extractor:
            raise HTTPException(status_code=503, detail="Topic model not loaded")
        
        # Schedule model update in the background
        background_tasks.add_task(topic_extractor.update_model, texts)
        
        return {"status": "success", "message": "Topic model update scheduled"}
    except Exception as e:
        logger.error(json.dumps({"event": "topic_model_update_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail=f"Error updating topic model: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", Config.API_PORT))
    uvicorn.run("app:app", host=Config.API_HOST, port=port, reload=False)