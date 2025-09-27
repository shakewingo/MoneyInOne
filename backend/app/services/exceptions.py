"""Custom exceptions for service layer."""


class ServiceError(Exception):
    """Base exception for service layer errors."""
    
    def __init__(self, message: str, error_code: str = None):
        """Initialize service error."""
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


class NotFoundError(ServiceError):
    """Exception raised when a requested resource is not found."""
    pass


class ValidationError(ServiceError):
    """Exception raised when data validation fails."""
    pass


class ExternalAPIError(ServiceError):
    """Exception raised when external API calls fail."""
    pass


class CacheError(ServiceError):
    """Exception raised when cache operations fail."""
    pass


class DatabaseError(ServiceError):
    """Exception raised when database operations fail."""
    pass
