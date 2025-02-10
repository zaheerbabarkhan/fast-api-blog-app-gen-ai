from typing import List
from langchain_postgres import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.core.config.llm.embeddings import EmbeddingService
from app.exceptions.exceptions import VectorStoreInitException, VectorStoreOpException
import logging

logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self, connection_string: str, embedding_service: EmbeddingService, collection_name: str = "blog_posts"):
        try:
            self.connection_string = connection_string
            self.embedding_service = embedding_service
            self.collection_name = collection_name    
            self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)

            self.vector_store = PGVector(
                collection_name=self.collection_name,
                connection=self.connection_string,
                embeddings=self.embedding_service,
                use_jsonb=True
            )
        except Exception as e:
            logger.exception(f"Failed to initialize VectorStoreService: {str(e)}")
            raise VectorStoreInitException("VectorStoreService initialization failed") from e

    def store_blog_post(self, blog_post_id: str, content: str):
        """Adds a blog post's content to PGVector only if the blog_post_id doesn't already exist."""
        try:
            # Check if any document already exists for this blog_post_id
            existing_docs = self.vector_store.similarity_search(
                query="",  # Empty query to just check existence
                k=1,
                filter={"blog_post_id": blog_post_id}
            )
            
            if existing_docs:
                return

            texts = self.text_splitter.split_text(content)
            documents_to_add = [
                Document(page_content=text, metadata={"blog_post_id": str(blog_post_id), "chunk_index": i})
                for i, text in enumerate(texts)
            ]
            self.vector_store.add_documents(documents=documents_to_add)
        except Exception as e:
            logger.exception(f"Failed to store blog post {blog_post_id}: {str(e)}")
            raise VectorStoreOpException("Failed to store blog post") from e

    def get_retriever(self, blog_post_id: int):
        """Returns a retriever that filters results to a specific blog post."""
        try:
            return self.vector_store.as_retriever(
                search_kwargs={ "k": 5 ,"filter": {"blog_post_id": str(blog_post_id)}}
            )
        except Exception as e:
            logger.exception(f"Failed to get retriever for blog post {blog_post_id}: {str(e)}")
            raise VectorStoreOpException("Failed to get retriever") from e

    def query_blog_post(self, blog_post_id: str, query: str):
        """Fetches relevant chunks from a specific blog post using semantic search."""
        try:
            retriever = self.get_retriever(blog_post_id)
            return retriever.invoke(query)
        except Exception as e:
            logger.exception(f"Failed to query blog post {blog_post_id}: {str(e)}")
            raise VectorStoreOpException("Failed to query blog post") from e