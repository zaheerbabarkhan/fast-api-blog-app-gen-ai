from fastapi import status

class AppBaseException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return self.message

class ResourceNotFoundException(AppBaseException):
    def __init__(self, message: str = 'Resource not found'):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)
    
class ResourceAlreadyExistsException(AppBaseException):
    def __init__(self, message: str = 'Resource already exists'):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)

class InvalidInputException(AppBaseException):
    def __init__(self, message: str = 'Invalid input'):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)

class UnauthorizedException(AppBaseException):
    def __init__(self, message: str = 'Unauthorized'):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)

class ForbiddenException(AppBaseException):
    def __init__(self, message: str = 'Forbidden'):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)

class DatabaseExeption(AppBaseException):
    def __init__(self, message: str = 'Internal server error'):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LLMServiceInvokeException(AppBaseException):
    def __init__(self, message: str = 'LLM service is not available'):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

class SummarizationException(AppBaseException):
    def __init__(self, message: str = 'Summarization service is not available'):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

class SentimentAnalysisInitException(AppBaseException):
    def __init__(self, message: str = 'Sentiment analysis service is not available'):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

class LLMInitException(AppBaseException):
    def __init__(self, message: str = 'Failed to initialize ChatGroq'):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SentimentInvokeException(AppBaseException):
    def __init__(self, message: str = 'Failed to invoke ChatGroq for sentiment analysis'):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SummarizationInvokeException(AppBaseException):
    def __init__(self, message: str = 'Failed to invoke ChatGroq for summarization'):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SuggestionServiceInitException(AppBaseException):
    def __init__(self, message: str = 'Suggestion service is not available'):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

class SuggestionInvokeException(AppBaseException):
    def __init__(self, message: str = 'Failed to invoke ChatGroq for suggestions'):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SummarizationInitException(AppBaseException):
    def __init__(self, message: str = 'Failed to initialize ChatGroq for summarization'):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmbeddingInitException(AppBaseException):
    def __init__(self, message: str = 'Embedding service is not available'):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

class EmbedDocException(AppBaseException):
    def __init__(self, message: str = 'Failed to embed documents'):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VectorStoreInitException(AppBaseException):
    def __init__(self, message: str = 'Vector store service is not available'):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    

class VectorStoreOpException(AppBaseException):
    def __init__(self, message: str = 'Failed to perform operation on vector store'):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QAInitException(AppBaseException):
    def __init__(self, message: str = 'Question-answering service is not available'):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

class QAInvokeException(AppBaseException):
    def __init__(self, message: str = 'Failed to invoke QuestionAnswerService'):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)