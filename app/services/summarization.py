import logging
from langchain_core.exceptions import OutputParserException

from app.core.config.llm.llm import LLMService
from app.core.config.llm.prompt_templates import summary_prompt_template
from app.schemas.llm_responses_parsers import summary_res_parser
from app.core.config.llm.token_usage import TokenUsageHandler
from app.exceptions.exceptions import LLMInitException, SummarizationInitException, SummarizationInvokeException

logger = logging.getLogger(__name__)

class SummarizationService:
    """
    A service class for generating summaries using a language model.

    Attributes:
        llm_service (LLMService): An instance of the LLMService class with a specified temperature.
        prompt_template (function): A function that returns the prompt template for summaries.
        chain (Chain): A chain of operations combining the prompt template, language model, and result parser.
    """
    
    def __init__(self):
        """
        Initializes the SummarizationService with an LLMService instance, a prompt template, and a chain of operations.
        """
        try:
            self.llm_service = LLMService(temperature=0.3)
            self.prompt_template = summary_prompt_template()
            self.chain = self.prompt_template | self.llm_service.llm | summary_res_parser

        except LLMInitException as e:
            logger.exception(f"Failed to initialize ChatGroq: {str(e)}")
            raise SummarizationInitException("Summarization service is not available") from e

    def summarize(self, content: str) -> dict:
        """
        Generates a summary based on the given content and returns the response.

        Args:
            content (str): The content to generate a summary for.

        Returns:
            dict: The response from the summarization generation. If an error occurs, returns None.

        Raises:
            SummarizationInvokeException: If the summarization service fails to generate a summary.
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
            raise SummarizationInvokeException("Failed to generate summary") from e

        except Exception as e:
            logger.exception(f"Failed to generate summary: {str(e)}")
            raise SummarizationInvokeException("Failed to generate summary") from e