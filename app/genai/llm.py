from langchain_groq import ChatGroq

from app.core.config import settings


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
    
    def generate_summary(self, prompt: str):
        return self.llm.invoke(prompt, reasoning_format="hidden")
