import json
from collections.abc import Sequence
from datetime import UTC
from datetime import date
from datetime import datetime
from typing import Final
from typing import Literal
from typing import Optional

from pydantic import Field

from youtrack_sdk.entities import BaseModel
from youtrack_sdk.helpers import custom_json_dumps
from youtrack_sdk.helpers import obj_to_dict


class SimpleModel(BaseModel):
    type: Literal["SimpleModel"] = Field(alias="$type", default="SimpleModel")
    flag: Optional[bool] = None
    short_name: Optional[str] = Field(alias="shortName", default=None)
    value: Optional[int] = None


class NestedModel(BaseModel):
    type: Literal["NestedModel"] = Field(alias="$type", default="NestedModel")
    source: Optional[SimpleModel] = None
    dest: Optional[SimpleModel] = None


class NestedSequenceModel(BaseModel):
    type: Literal["NestedSequenceModel"] = Field(alias="$type", default="NestedSequenceModel")
    items: Optional[Sequence[NestedModel]] = None
    stocks: Optional[Sequence[NestedModel]] = None


def test_obj_to_dict_none() -> None:
    assert obj_to_dict(None) is None


def test_obj_to_dict_simple_model() -> None:
    result: Final = obj_to_dict(SimpleModel.model_construct(short_name="Demo", value=None))
    assert result == {
        "$type": "SimpleModel",
        "shortName": "Demo",
        "value": None,
    }


def test_obj_to_dict_nested_model() -> None:
    result: Final = obj_to_dict(
        NestedModel.model_construct(
            source=SimpleModel.model_construct(short_name="Demo", value=None),
        ),
    )
    assert result == {
        "$type": "NestedModel",
        "source": {
            "$type": "SimpleModel",
            "shortName": "Demo",
            "value": None,
        },
    }


def test_obj_to_dict_nested_sequence_model() -> None:
    result: Final = obj_to_dict(
        NestedSequenceModel.model_construct(
            items=[
                NestedModel.model_construct(),
                NestedModel.model_construct(
                    source=SimpleModel.model_construct(short_name="Source", value=None),
                    dest=SimpleModel.model_construct(short_name="Dest", value=5),
                ),
            ],
        ),
    )
    assert result == {
        "$type": "NestedSequenceModel",
        "items": [
            {
                "$type": "NestedModel",
            },
            {
                "$type": "NestedModel",
                "source": {"$type": "SimpleModel", "shortName": "Source", "value": None},
                "dest": {"$type": "SimpleModel", "shortName": "Dest", "value": 5},
            },
        ],
    }


def test_custom_json_dumps_flat_dict() -> None:
    assert json.loads(
        custom_json_dumps(
            {
                "some_value": 10,
                "datetime_value": datetime(2021, 2, 9, 14, 3, 11, tzinfo=UTC),
                "date_value": date(2022, 2, 17),
            },
        ),
    ) == {
        "some_value": 10,
        "datetime_value": 1612879391000,
        "date_value": 1645099200000,
    }


def test_custom_json_dumps_nested_dict() -> None:
    assert json.loads(
        custom_json_dumps(
            {
                "str_value": "some text",
                "nested_dict": {
                    "int_value": 12,
                    "datetime_value": datetime(2021, 2, 9, 14, 3, 11, tzinfo=UTC),
                    "enclosed_dict": {
                        "none_value": None,
                        "date_value": date(2022, 2, 17),
                    },
                },
            },
        ),
    ) == {
        "str_value": "some text",
        "nested_dict": {
            "int_value": 12,
            "datetime_value": 1612879391000,
            "enclosed_dict": {
                "none_value": None,
                "date_value": 1645099200000,
            },
        },
    }


def test_custom_json_dumps_nested_sequence_dict() -> None:
    assert json.loads(
        custom_json_dumps(
            {
                "str_value": "some text",
                "list_value": [
                    {
                        "int_value": 12,
                        "datetime_value": datetime(2021, 2, 9, 14, 3, 11, tzinfo=UTC),
                    },
                    {
                        "nested_tuple_value": ({
                            "none_value": None,
                            "date_value": date(2022, 2, 17),
                        }),
                    },
                ],
            },
        ),
    ) == {
        "str_value": "some text",
        "list_value": [
            {
                "int_value": 12,
                "datetime_value": 1612879391000,
            },
            {
                "nested_tuple_value": ({
                    "none_value": None,
                    "date_value": 1645099200000,
                }),
            },
        ],
    }
