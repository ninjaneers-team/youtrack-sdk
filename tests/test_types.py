from datetime import UTC
from datetime import datetime
from typing import Final

import pytest

from youtrack_sdk.types import validate_youtrack_datetime


def test_validate_youtrack_datetime_without_project_custom_field() -> None:
    """Test that validate_youtrack_datetime raises RuntimeError when project_custom_field is missing."""

    # Create a mock ValidationInfo without project_custom_field
    class MockValidationInfo:
        data = {}

    info: Final = MockValidationInfo()

    with pytest.raises(
        RuntimeError,
        match="validate_youtrack_datetime can only be used with models having project_custom_field",
    ):
        validate_youtrack_datetime(123456789, info)  # type: ignore[arg-type]


def test_validate_youtrack_datetime_with_none_project_custom_field() -> None:
    """Test that validate_youtrack_datetime returns value when project_custom_field is None."""

    class MockValidationInfo:
        data = {"project_custom_field": None}

    info: Final = MockValidationInfo()
    value: Final = 12345

    result: Final = validate_youtrack_datetime(value, info)  # type: ignore[arg-type]
    assert result == value


def test_validate_youtrack_datetime_with_wrong_field_type() -> None:
    """Test that validate_youtrack_datetime returns value when field type is not 'date and time'."""

    class MockFieldType:
        id = "string"

    class MockField:
        field_type = MockFieldType()

    class MockProjectCustomField:
        field = MockField()

    class MockValidationInfo:
        data = {"project_custom_field": MockProjectCustomField()}

    info: Final = MockValidationInfo()
    value: Final = 12345

    result: Final = validate_youtrack_datetime(value, info)  # type: ignore[arg-type]
    assert result == value


def test_validate_youtrack_datetime_with_datetime_value() -> None:
    """Test that validate_youtrack_datetime returns datetime when value is already datetime."""

    class MockFieldType:
        id = "date and time"

    class MockField:
        field_type = MockFieldType()

    class MockProjectCustomField:
        field = MockField()

    class MockValidationInfo:
        data = {"project_custom_field": MockProjectCustomField()}

    info: Final = MockValidationInfo()
    value: Final = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

    result: Final = validate_youtrack_datetime(value, info)  # type: ignore[arg-type]
    assert result == value


def test_validate_youtrack_datetime_with_invalid_type() -> None:
    """Test that validate_youtrack_datetime raises ValueError when value is not int or datetime."""

    class MockFieldType:
        id = "date and time"

    class MockField:
        field_type = MockFieldType()

    class MockProjectCustomField:
        field = MockField()

    class MockValidationInfo:
        data = {"project_custom_field": MockProjectCustomField()}

    info: Final = MockValidationInfo()
    value: Final = "not an int"

    with pytest.raises(ValueError, match="'date and time' field must be an integer"):
        validate_youtrack_datetime(value, info)  # type: ignore[arg-type]


def test_validate_youtrack_datetime_with_timestamp() -> None:
    """Test that validate_youtrack_datetime converts timestamp to datetime."""

    class MockFieldType:
        id = "date and time"

    class MockField:
        field_type = MockFieldType()

    class MockProjectCustomField:
        field = MockField()

    class MockValidationInfo:
        data = {"project_custom_field": MockProjectCustomField()}

    info: Final = MockValidationInfo()
    # Timestamp for 2024-01-01 00:00:00 UTC in milliseconds
    value: Final = 1704067200000

    result: Final = validate_youtrack_datetime(value, info)  # type: ignore[arg-type]
    assert isinstance(result, datetime)
    assert result == datetime.fromtimestamp(1704067200000 / 1000, UTC)


def test_validate_youtrack_datetime_with_none_value() -> None:
    """Test that validate_youtrack_datetime returns None when value is None."""

    class MockFieldType:
        id = "date and time"

    class MockField:
        field_type = MockFieldType()

    class MockProjectCustomField:
        field = MockField()

    class MockValidationInfo:
        data = {"project_custom_field": MockProjectCustomField()}

    info: Final = MockValidationInfo()
    value: Final = None

    result: Final = validate_youtrack_datetime(value, info)  # type: ignore[arg-type]
    assert result is None
