from langchain_groq import ChatGroq

from app.core.config.config import settings


class LLMService:
    def __init__(self, temperature: float = 0):
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL_NAME,
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=settings.GROQ_API_KEY,
        )

    def greet(self):
        return self.llm.invoke("Say Hi to the user and ask how can you help them")