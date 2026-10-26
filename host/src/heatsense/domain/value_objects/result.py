"""Result value object providing functional error handling without exceptions.

Responsibility:
    Represent either a successful computation (Ok) or a typed failure (Err).

Contains:
    Ok, Err, Result, is_ok.

MAY import:
    stdlib.

MUST NOT import:
    application, infrastructure, interfaces, simulation, firmware.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True, slots=True)
class Ok[T]:
    """Represents a successful operation carrying value T."""

    value: T

    def is_ok(self) -> bool:
        """Return True indicating success."""
        return True

    def is_err(self) -> bool:
        """Return False indicating not an error."""
        return False

    def unwrap(self) -> T:
        """Return the inner value."""
        return self.value

    def unwrap_err(self) -> None:
        """Raise ValueError when unwrap_err is called on Ok."""
        raise ValueError("Called unwrap_err on Ok")


@dataclass(frozen=True, slots=True)
class Err[E]:
    """Represents an error or rejected operation carrying error E."""

    error: E

    def is_ok(self) -> bool:
        """Return False indicating not success."""
        return False

    def is_err(self) -> bool:
        """Return True indicating an error."""
        return True

    def unwrap(self) -> None:
        """Raise ValueError when unwrap is called on Err."""
        raise ValueError(f"Called unwrap on Err: {self.error}")

    def unwrap_err(self) -> E:
        """Return the inner error."""
        return self.error


type Result[T, E] = Ok[T] | Err[E]


def is_ok[T, E](result: Result[T, E]) -> bool:
    """Return True if result is an Ok instance, False otherwise."""
    return isinstance(result, Ok)
