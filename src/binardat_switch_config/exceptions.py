"""Custom exceptions for binardat-switch-config."""


class BinardatSwitchConfigError(Exception):
    """Base exception for all binardat-switch-config errors."""

    pass


class NetmikoConnectionError(BinardatSwitchConfigError):
    """Raised when SSH connection to switch fails."""

    pass


class ConfigRetrievalError(BinardatSwitchConfigError):
    """Raised when configuration retrieval fails."""

    pass


class GitOperationError(BinardatSwitchConfigError):
    """Raised when git operation fails."""

    pass


class RollbackError(BinardatSwitchConfigError):
    """Raised when rollback operation fails."""

    pass


class InventoryError(BinardatSwitchConfigError):
    """Raised when inventory configuration is invalid."""

    pass


class StorageError(BinardatSwitchConfigError):
    """Raised when filesystem storage operation fails."""

    pass


class ChangeDetectionError(BinardatSwitchConfigError):
    """Raised when change detection fails."""

    pass
