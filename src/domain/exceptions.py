class DomainError(Exception):
    """Base class for expected domain/application errors."""


class NotFoundError(DomainError):
    """A required domain entity could not be found."""


class ValidationError(DomainError):
    """Input or domain data failed validation."""


class ConflictError(DomainError):
    """An operation conflicts with an existing domain state."""


class InvalidStateError(DomainError):
    """The requested operation cannot proceed from the current state."""
