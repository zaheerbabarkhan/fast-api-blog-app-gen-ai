import logging

from langchain_groq import ChatGroq

from app.core.config.config import settings
from app.exceptions.exceptions import LLMInitException

logger = logging.getLogger(__name__)
class LLMService:
    def __init__(self, temperature: float = 0):
        try:
            self.llm = ChatGroq(
                model=settings.GROQ_MODEL_NAME,
                temperature=temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=settings.GROQ_API_KEY,
            )
        except Exception as e:
            logger.exception("Failed to initialize ChatGroq: %s", e)
            raise LLMInitException("Failed to initialize ChatGroq") from e

    def greet(self):
        if (self.llm is None):
            return "LLM service is not available."

        try:
            return self.llm.invoke("Say Hi to the user and ask how can you help them")
        except Exception as e:
            # Handle any other exceptions
            print(f"Failed to invoke ChatGroq: {e}")
            return "Failed to generate a response."
