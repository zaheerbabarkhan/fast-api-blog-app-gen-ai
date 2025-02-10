import logging


from langchain_core.exceptions import OutputParserException

from app.core.config.llm.llm import LLMService
from app.core.config.llm.prompt_templates import comment_analysis_template
from app.core.config.llm.token_usage import TokenUsageHandler
from app.exceptions.exceptions import LLMInitializationException, SentimentAnalysisInitException, SentimentInvokeException
from app.schemas.llm_responses_parsers import comment_analysis_res_parser

logger = logging.getLogger(__name__)




class CommentAnalysisService:
    """
    A service class for performing sentiment analysis on comments using a language model.

    Attributes:
        llm_service (LLMService): An instance of the LLMService class with a specified temperature.
        prompt_template (function): A function that returns the prompt template for comment analysis.
        chain (Chain): A chain of operations combining the prompt template, language model, and result parser.
    """
        
    def __init__(self):
        """
        Initializes the CommentAnalysisService with an LLMService instance, a prompt template, and a chain of operations.
        """
        try:
            self.llm_service = LLMService(temperature=0.7)
            self.prompt_template = comment_analysis_template()
            self.chain = self.prompt_template | self.llm_service.llm | comment_analysis_res_parser

        except LLMInitializationException as e:
            raise SentimentAnalysisInitException("Sentiment analysis service is not available") from e

    def sentiment_analysis(self, comment: str) -> dict:
        """
        Analyzes the sentiment of the given comment and returns the response.

        Args:
            comment (str): The comment to be analyzed.

        Returns:
            dict: The response from the sentiment analysis. If an error occurs, returns None.

        Raises:
            SentimentAnalysisException: If the sentiment analysis service is not available or fails to analyze the comment.
        """
        try:
            token_handler = TokenUsageHandler()
            response = self.chain.invoke(
                {"content": comment}, 
                config={"callbacks": [token_handler]}
            )
            token_handler.log_token_usage(logger)
            return response
        
        except OutputParserException as e:
            logger.exception(f"Failed to parse the response: {str(e)}")
            raise SentimentInvokeException("Failed to analyze comment") from e

        except Exception as e:
            logger.exception(f"Failed to analyze comment: {str(e)}")
            raise SentimentInvokeException("Failed to analyze comment") from e