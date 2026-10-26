"""Unit tests for Result, Ok, and Err value objects."""

from __future__ import annotations

import pytest

from heatsense.domain.value_objects.result import Err, Ok, is_ok


def test_ok_properties_and_methods() -> None:
    res = Ok(42)
    assert res.is_ok() is True
    assert res.is_err() is False
    assert is_ok(res) is True
    assert res.unwrap() == 42

    with pytest.raises(ValueError, match="Called unwrap_err on Ok"):
        res.unwrap_err()


def test_err_properties_and_methods() -> None:
    res = Err("something went wrong")
    assert res.is_ok() is False
    assert res.is_err() is True
    assert is_ok(res) is False
    assert res.unwrap_err() == "something went wrong"

    with pytest.raises(ValueError, match="something went wrong"):
        res.unwrap()


def test_result_immutability() -> None:
    ok = Ok(10)
    with pytest.raises(AttributeError):
        ok.value = 20  # type: ignore[misc]

    err = Err("err")
    with pytest.raises(AttributeError):
        err.error = "new"  # type: ignore[misc]
