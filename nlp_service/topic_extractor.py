import logging
import json
import pickle
import os
import numpy as np
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TopicExtractor:
    def __init__(self):
        self.model = self._load_or_create_model()
        self.sentence_transformer = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
        logger.info(json.dumps({"event": "topic_extractor_initialized"}))

    def _load_or_create_model(self):
        model_path = os.path.join(Config.MODEL_PATH, "bertopic_model.pkl")
        try:
            if os.path.exists(model_path):
                logger.info(json.dumps({"event": "loading_existing_model", "path": model_path}))
                with open(model_path, "rb") as f:
                    return pickle.load(f)
            else:
                logger.info(json.dumps({"event": "creating_new_model"}))
                # Initialize a new BERTopic model with default parameters
                vectorizer = CountVectorizer(stop_words="english")
                model = BERTopic(vectorizer_model=vectorizer, min_topic_size=Config.TOPIC_THRESHOLD)
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                
                # Save the model
                with open(model_path, "wb") as f:
                    pickle.dump(model, f)
                
                return model
                
        except Exception as e:
            logger.error(json.dumps({"event": "model_loading_error", "error": str(e)}))
            # Fall back to creating a new model
            return BERTopic(min_topic_size=Config.TOPIC_THRESHOLD)
    
    def extract_topic(self, text, embedding=None):
        """Extract topic from a single text"""
        try:
            if embedding is None:
                embedding = self.sentence_transformer.encode([text])[0]
            
            # Get topic prediction
            topic_id, prob = self.model.transform([text], [embedding])
            topic_id = topic_id[0]
            confidence = float(max(prob[0]) if prob[0].size > 0 else 0.0)
            
            # Get topic information
            if topic_id != -1:  # -1 is the outlier topic
                topic_info = self.model.get_topic(topic_id)
                topic_words = [word for word, _ in topic_info[:5]]  # Get top 5 words
                topic_label = " ".join(topic_words[:3])  # Use top 3 words as label
            else:
                topic_words = []
                topic_label = "misc"
            
            return topic_id, topic_label, confidence, topic_words
            
        except Exception as e:
            logger.error(json.dumps({"event": "topic_extraction_error", "error": str(e)}))
            return -1, "error", 0.0, []
    
    def update_model(self, texts):
        """Update the topic model with new texts"""
        try:
            logger.info(json.dumps({"event": "updating_topic_model", "num_texts": len(texts)}))
            
            # Generate embeddings
            embeddings = self.sentence_transformer.encode(texts)
            
            # Update model
            self.model.update_topics(texts, embeddings)
            
            # Save updated model
            model_path = os.path.join(Config.MODEL_PATH, "bertopic_model.pkl")
            with open(model_path, "wb") as f:
                pickle.dump(self.model, f)
                
            logger.info(json.dumps({"event": "topic_model_updated"}))
            return True
            
        except Exception as e:
            logger.error(json.dumps({"event": "update_model_error", "error": str(e)}))
            return False

if __name__ == "__main__":
    extractor = TopicExtractor()
    sample_text = "The stock market is experiencing significant volatility."
    topic_id, topic_label, confidence, topic_words = extractor.extract_topic(sample_text)
    print("Topic ID:", topic_id)
    print("Topic Label:", topic_label)
    print("Confidence:", confidence)
    print("Topic Words:", topic_words)