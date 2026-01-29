from collections.abc import Sequence
from typing import Annotated
from typing import Final
from typing import Literal
from typing import Optional

import pytest
from pydantic import Field

from tests.test_definitions import TEST_ISSUE
from tests.test_definitions import TEST_STATE_CUSTOM_FIELD
from youtrack_sdk.entities import BaseModel
from youtrack_sdk.exceptions import NonSingleValueError
from youtrack_sdk.helpers import get_issue_custom_field
from youtrack_sdk.helpers import model_to_field_names


class SimpleModel(BaseModel):
    type: Literal["SimpleModel"] = Field(alias="$type", default="SimpleModel")
    id: Optional[int] = None
    short_name: Optional[str] = Field(alias="shortName", default=None)


class NestedModel(BaseModel):
    type: Literal["NestedModel"] = Field(alias="$type", default="NestedModel")
    value: Optional[SimpleModel] = None


class NestedUnionModel(BaseModel):
    type: Literal["NestedUnionModel"] = Field(alias="$type", default="NestedUnionModel")
    items: Optional[Sequence[NestedModel | SimpleModel | int]] = None
    entry: Optional[NestedModel | SimpleModel | int] = None


def test_model_to_field_names_simple_model() -> None:
    assert model_to_field_names(SimpleModel) == "$type,id,shortName"


def test_model_to_field_names_nested_model() -> None:
    assert model_to_field_names(NestedModel) == "$type,value($type,id,shortName)"


def test_model_to_field_names_nested_union_model() -> None:
    expected: Final = (
        "$type,items($type,value($type,id,shortName),id,shortName),entry($type,value($type,id,shortName),id,shortName)"
    )
    assert model_to_field_names(NestedUnionModel) == expected


def test_model_to_field_names_union_type() -> None:
    assert model_to_field_names(SimpleModel | NestedModel) == "$type,id,shortName,value($type,id,shortName)"
    assert model_to_field_names(SimpleModel | NestedModel) == "$type,id,shortName,value($type,id,shortName)"
    assert (
        model_to_field_names(Annotated[SimpleModel | NestedModel, Field(discriminator="type")])
        == "$type,id,shortName,value($type,id,shortName)"
    )


def test_get_issue_custom_field() -> None:
    assert get_issue_custom_field(issue=TEST_ISSUE, field_name="State") == TEST_STATE_CUSTOM_FIELD

    with pytest.raises(NonSingleValueError):
        get_issue_custom_field(issue=TEST_ISSUE, field_name="Unknown")
