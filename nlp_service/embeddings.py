import json
import logging
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name="distilbert-base-nli-stsb-mean-tokens"):
        self.model = SentenceTransformer(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        logger.info(json.dumps({"event": "embedding_service_initialized", "model": model_name, "device": self.device.type}))

    def generate_embeddings(self, text):
        """Generate embeddings for a single text"""
        try:
            if not text or len(text.strip()) == 0:
                logger.warning(json.dumps({"event": "empty_text_for_embedding"}))
                # Return zero vector of appropriate size
                return np.zeros(Config.EMBEDDING_DIMENSION)
            
            embedding = self.model.encode(text)
            return embedding
            
        except Exception as e:
            logger.error(json.dumps({"event": "embedding_error", "error": str(e)}))
            # Return zero vector in case of error
            return np.zeros(Config.EMBEDDING_DIMENSION)
    
    def generate_batch_embeddings(self, texts, batch_size=32):
        """Generate embeddings for a batch of texts"""
        try:
            embeddings = self.model.encode(texts, batch_size=batch_size)
            return embeddings
            
        except Exception as e:
            logger.error(json.dumps({"event": "batch_embedding_error", "error": str(e)}))
            # Return zero vectors in case of error
            return np.zeros((len(texts), Config.EMBEDDING_DIMENSION))

# Example usage
if __name__ == "__main__":
    service = EmbeddingService("distilbert-base-nli-stsb-mean-tokens")
    sample_text = "This is a sample text for generating embeddings."
    embeddings = service.generate_embeddings(sample_text)
    print(embeddings)