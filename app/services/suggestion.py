from app.core.config.llm.llm import LLMService
from app.core.config.llm.prompt_templates import suggestion_prompt_template
from app.schemas.llm_responses_parsers import suggestions_res_parser


class SuggestionService:
    def __init__(self):
        self.llm_service = LLMService(temperature=0.7)
        self.prompt_template = suggestion_prompt_template()
        self.chain = self.prompt_template | self.llm_service.llm | suggestions_res_parser

    
    def suggest(self, content: str):
        try:
            response = self.chain.invoke({"content": content}, reasoning_format="hidden")
            return response
        except Exception as e:
            # Log the exception if needed
            return None