from collections.abc import Sequence
from typing import Annotated
from typing import Literal
from typing import Optional
from unittest import TestCase

from pydantic import Field

from tests.test_definitions import TEST_ISSUE
from tests.test_definitions import TEST_STATE_CUSTOM_FIELD
from youtrack_sdk import Client
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


class TestModelToFieldNames(TestCase):
    def test_simple_model(self) -> None:
        self.assertEqual(
            "$type,id,shortName",
            model_to_field_names(SimpleModel),
        )

    def test_nested_model(self) -> None:
        self.assertEqual(
            "$type,value($type,id,shortName)",
            model_to_field_names(NestedModel),
        )

    def test_nested_union_model(self) -> None:
        self.assertEqual(
            "$type,items($type,value($type,id,shortName),id,shortName),entry($type,value($type,id,shortName),id,shortName)",
            model_to_field_names(NestedUnionModel),
        )

    def test_union_type(self) -> None:
        self.assertEqual(
            "$type,id,shortName,value($type,id,shortName)",
            model_to_field_names(SimpleModel | NestedModel),
        )
        self.assertEqual(
            "$type,id,shortName,value($type,id,shortName)",
            model_to_field_names(SimpleModel | NestedModel),
        )
        self.assertEqual(
            "$type,id,shortName,value($type,id,shortName)",
            model_to_field_names(Annotated[SimpleModel | NestedModel, Field(discriminator="type")]),
        )


class TestHelpers(TestCase):
    def setUp(self) -> None:
        self.client = Client(base_url="https://server", token="test")  # noqa: S106

    def test_get_issue_custom_field(self) -> None:
        self.assertEqual(
            get_issue_custom_field(issue=TEST_ISSUE, field_name="State"),
            TEST_STATE_CUSTOM_FIELD,
        )
        self.assertRaises(
            NonSingleValueError,
            get_issue_custom_field,
            issue=TEST_ISSUE,
            field_name="Unknown",
        )
