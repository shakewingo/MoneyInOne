"""Custom exceptions for the services layer."""


class ServiceError(Exception):
    """Base exception for service layer errors."""
    pass

class ValidationError(ServiceError):
    """Raised when data validation fails."""
    pass


class AssetNotFoundError(ServiceError):
    """Raised when an asset is not found."""
    pass


class UserNotFoundError(ServiceError):
    """Raised when a user is not found."""
    pass


class AssetTypeNotFoundError(ServiceError):
    """Raised when an asset type is not found."""
    pass


class ExternalAPIError(ServiceError):
    """Raised when external API calls fail."""
    pass


class CreditNotFoundError(ServiceError):
    """Raised when a credit is not found."""
    pass


class CurrencyConversionError(ServiceError):
    """Raised when currency conversion fails."""
    pass