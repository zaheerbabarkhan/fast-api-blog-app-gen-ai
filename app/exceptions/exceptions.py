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

class SummarizationServiceNotAvailableException(AppBaseException):
    def __init__(self, message: str = 'Summarization service is not available'):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

class LLMServiceInitializationException(AppBaseException):
    def __init__(self, message: str = 'Failed to initialize ChatGroq'):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)