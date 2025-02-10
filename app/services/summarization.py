from app.core.config.llm.llm import LLMService
from app.core.config.llm.prompt_templates import summary_prompt_template
from app.schemas.llm_responses_parsers import summary_res_parser

class SummarizationService:
    def __init__(self):
        self.llm_service = LLMService(temperature=0.3)
        self.prompt_template = summary_prompt_template()
        self.chain = self.prompt_template | self.llm_service.llm | summary_res_parser

    
    def summarize(self, content: str):
        response = self.chain.invoke({"content": content}, reasoning_format="hidden")
        return response
