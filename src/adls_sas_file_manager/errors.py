"""Typed exceptions for the ADLS SAS File Manager library.

None of these exception messages should ever include a SAS token, Key Vault
secret name, or secret value (see constitution: Secure by Default).
"""

from __future__ import annotations


class AdlsSasFileManagerError(Exception):
    """Base class for all errors raised by this library."""


class ConfigurationError(AdlsSasFileManagerError):
    """Raised when required configuration is missing or invalid."""


class SecretRetrievalError(AdlsSasFileManagerError):
    """Raised when a secret (e.g. the SAS token) could not be retrieved from Key Vault."""


class AuthorizationError(AdlsSasFileManagerError):
    """Raised when the SAS token is rejected or lacks permissions for an operation."""


class PathNotFoundError(AdlsSasFileManagerError):
    """Raised when a directory or file path does not exist for an operation that requires it."""


class StorageOperationError(AdlsSasFileManagerError):
    """Raised for other storage-service failures not covered by the more specific errors above."""
