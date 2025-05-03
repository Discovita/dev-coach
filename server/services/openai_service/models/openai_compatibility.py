"""
OpenAI compatibility types.

This module provides compatible replacement types that were previously imported
from private OpenAI modules (_types and _streaming). This allows our code to work
without depending on private OpenAI implementation details.
"""

from typing import TypeVar, Generic, Any, Iterator, ContextManager, TypeAlias


import logging

log = logging.getLogger(__name__)


class NotGiven:
    """
    A sentinel class used to distinguish between None and omitted parameters.
    This replaces the private openai._types.NotGiven class.
    """

    def __bool__(self) -> bool:
        """Always returns False to act like a falsy value."""
        return False

    def __repr__(self) -> str:
        """String representation for debugging."""
        return "NOT_GIVEN"


NOT_GIVEN = NotGiven()


T = TypeVar("T")


class Stream(Generic[T], ContextManager["Stream[T]"]):
    """
    A compatible replacement for openai._streaming.Stream.

    This class provides a minimal implementation of the Stream interface
    used in the OpenAI client library, focused on the features we actually use.
    """

    def __init__(self, iterator: Iterator[Any]):
        """
        Initialize a Stream with an iterator.

        Parameters
        ----------
        iterator : Iterator[Any]
            The iterator that produces stream events
        """
        self._iterator = iterator
        self._final_completion = None

    def __iter__(self) -> Iterator[Any]:
        """Return the stream iterator."""
        return self._iterator

    def __enter__(self) -> "Stream[T]":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        pass

    def get_final_completion(self) -> T:
        """
        Return the final completion from the stream.

        Returns
        -------
        T
            The final completion object

        Raises
        ------
        ValueError
            If no final completion is available
        """
        if self._final_completion is None:
            raise ValueError("No final completion available")
        return self._final_completion


StreamType: TypeAlias = Stream
