from typing import List
from langchain_community.embeddings import (
    HuggingFaceInferenceAPIEmbeddings,
)

class EmbeddingService:
    def __init__(self, model: str, api_key: str):
        self.embedding_model = HuggingFaceInferenceAPIEmbeddings(
            model_name=model,
            api_key=api_key,
            ) 
        
    def _flatten_embedding(self, embedding: List) -> List[float]:
        """Ensure embeddings are flat lists of floats"""
        if isinstance(embedding[0], list):
            return [float(num) for sublist in embedding for num in sublist]
        return [float(num) for num in embedding]
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.embedding_model.embed_documents(texts)
        return [self._flatten_embedding(embedding) for embedding in embeddings]

    def embed_query(self, query: str) -> list[float]:
        """Generates an embedding for a query with proper flattening"""
        embedding = self.embedding_model.embed_query(query)
        return embedding
        # return self._flatten_embedding(embedding)


