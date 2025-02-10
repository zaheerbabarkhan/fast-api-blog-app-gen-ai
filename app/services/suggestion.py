import logging
from langchain_core.exceptions import OutputParserException

from app.core.config.llm.llm import LLMService
from app.core.config.llm.prompt_templates import suggestion_prompt_template
from app.schemas.llm_responses_parsers import suggestions_res_parser
from app.core.config.llm.token_usage import TokenUsageHandler
from app.exceptions.exceptions import LLMInitException, SuggestionServiceInitException, SuggestionInvokeException

logger = logging.getLogger(__name__)

class SuggestionService:
    """
    A service class for generating suggestions using a language model.

    Attributes:
        llm_service (LLMService): An instance of the LLMService class with a specified temperature.
        prompt_template (function): A function that returns the prompt template for suggestions.
        chain (Chain): A chain of operations combining the prompt template, language model, and result parser.
    """
    
    def __init__(self):
        """
        Initializes the SuggestionService with an LLMService instance, a prompt template, and a chain of operations.
        """
        try:
            self.llm_service = LLMService(temperature=0.7)
            self.prompt_template = suggestion_prompt_template()
            self.chain = self.prompt_template | self.llm_service.llm | suggestions_res_parser

        except LLMInitException as e:
            logger.exception(f"Failed to initialize ChatGroq: {str(e)}")
            raise SuggestionServiceInitException("Suggestion service is not available") from e

    def suggest(self, content: str) -> dict:
        """
        Generates suggestions based on the given content and returns the response.

        Args:
            content (str): The content to generate suggestions for.

        Returns:
            dict: The response from the suggestion generation. If an error occurs, returns None.

        Raises:
            SuggestionInvokeException: If the suggestion service fails to generate suggestions.
        """
        try:
            token_handler = TokenUsageHandler()
            response = self.chain.invoke(
                {"content": content}, 
                config={"callbacks": [token_handler]}
            )
            token_handler.log_token_usage(logger)
            return response
        
        except OutputParserException as e:
            logger.exception(f"Failed to parse the response: {str(e)}")
            raise SuggestionInvokeException("Failed to generate suggestions") from e

        except Exception as e:
            logger.exception(f"Failed to generate suggestions: {str(e)}")
            raise SuggestionInvokeException("Failed to generate suggestions") from e