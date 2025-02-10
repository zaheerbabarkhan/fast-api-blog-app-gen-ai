from typing import List
from langchain_community.embeddings import (
    HuggingFaceInferenceAPIEmbeddings,
)

from app.exceptions.exceptions import EmbedDocException, EmbeddingInitException

class EmbeddingService:
    def __init__(self, model: str, api_key: str):
        try:
            self.embedding_model = HuggingFaceInferenceAPIEmbeddings(
                model_name=model,
                api_key=api_key,
                )         
        except Exception as e:
            raise EmbeddingInitException("Failed to initialize Embedding Service") from e
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        try:
            embeddings = self.embedding_model.embed_documents(texts)
            return embeddings
        except Exception as e:
            raise EmbedDocException("Failed to embed documents") from e

    def embed_query(self, query: str) -> list[float]:
        """Generates an embedding for a query with proper flattening"""
        try:
            embedding = self.embedding_model.embed_query(query)
            return embedding
        except Exception as e:
            raise EmbedDocException("Failed to embed query") from e
    


