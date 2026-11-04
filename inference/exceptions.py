"""
Custom exceptions for the LLM MemoryGrid inference adapter.
Used by worker handlers and backend services to distinguish failure modes.
"""

class InferenceError(Exception):
    """Base exception for all inference pipeline failures."""
    pass

class ModelNotReadyError(InferenceError):
    """Raised when the model weights or runtime are uninitialized or missing."""
    pass

class InferenceTimeoutError(InferenceError):
    """Raised when generation exceeds the agreed operational timeout budget."""
    pass

class InvalidPromptError(InferenceError):
    """Raised when the input prompt violates contract bounds (empty or wrong type)."""
    pass
