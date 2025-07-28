
class BaseChatbotException(Exception):
    def __init__(self, message: str = "An unexpected error occurred in the chatbot system.", details: dict | None = None):
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

class ScrapingException(DataProcessingException):
    def __init__(self, message: str = "Error during web scraping.", details: dict | None = None):
        super().__init__(f"ScrapingError: {message}", details)

class CleaningException(DataProcessingException):
    def __init__(self, message: str = "Error during data cleaning.", details: dict | None = None):
        super().__init__(f"CleaningError: {message}", details)

class ChunkingException(DataProcessingException):
    def __init__(self, message: str = "Error during text chunking.", details: dict | None = None):
        super().__init__(f"ChunkingError: {message}", details)

class EmbeddingException(BaseChatbotException):
    def __init__(self, message: str = "Error during embedding generation.", details: dict | None = None):
        super().__init__(f"EmbeddingError: {message}", details)

class VectorDBException(BaseChatbotException):
    def __init__(self, message: str = "Error interacting with vector database.", details: dict | None = None):
        super().__init__(f"VectorDBError: {message}", details)

class ChatbotException(BaseChatbotException):
    def __init__(self, message: str = "Error in chatbot response generation.", details: dict | None = None):
        super().__init__(f"ChatbotError: {message}", details)

class APIException(BaseChatbotException):
    def __init__(self, message: str = "API processing error.", details: dict | None = None):
        super().__init__(f"APIError: {message}", details)

class GenerationException(BaseChatbotException):
    def __init__(self, message: str = "Content generation error.", details: dict | None = None):
        super().__init__(f"ContentError: {message}", details)