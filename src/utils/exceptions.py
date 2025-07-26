
class BaseChatbotException(Exception):

    def __init__(self, message: str = "An Unexpected error occurred in the chatbot system ", details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details if details is not None else {}

    def __str__(self):
        if self.details:
            return f"{self.message} Details: {self.details}"
        return self.message

class DataProcessingException(BaseChatbotException):
    def __init__(self, message: str = "Error during data processing.", details: dict | None = None):
        super().__init__(f"DataProcessingError: {message}", details)

class EmbeddingException(BaseChatbotException):

    def __init__(self, message: str = "Error during embedding generation.", details: dict | None = None):
        super.__init__(f"EmbeddingError: {message}", details)

class VectorDBException(BaseChatbotException):
    def __init__(self, message: str = "Error interacting with vector database.", details: dict | None = None):
        super().__init__(f"VectorDBError: {message}", details)

class ChatbotException(BaseChatbotException):
    def __init__(self, message: str = "Error in chatbot response generation.", details: dict | None = None):
        super().__init__(f"ChatbotError: {message}", details)

class APIException(BaseChatbotException):
    def __init__(self, message: str = "API processing error.", details: dict | None = None):
        super().__init__(f"APIError: {message}", details)
