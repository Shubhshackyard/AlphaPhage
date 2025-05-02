from transformers import AutoModel, AutoTokenizer
import torch

class NLPModel:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def generate_embeddings(self, text: str):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()  # Return mean of embeddings

# Example usage
if __name__ == "__main__":
    model_name = "distilbert-base-uncased"
    nlp_model = NLPModel(model_name)
    sample_text = "This is a sample text for generating embeddings."
    embeddings = nlp_model.generate_embeddings(sample_text)
    print(embeddings)