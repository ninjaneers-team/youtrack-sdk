import json
from collections.abc import Collection
from copy import deepcopy
from datetime import UTC
from datetime import date
from datetime import datetime
from datetime import time
from itertools import starmap
from typing import Annotated
from typing import Any
from typing import Optional
from typing import get_args
from typing import get_origin

from pydantic import BaseModel

from youtrack_sdk.entities import Issue
from youtrack_sdk.entities import IssueCustomFieldType
from youtrack_sdk.exceptions import NonSingleValueError


def deep_update(dest: dict[Any, Any], *mappings: dict[Any, Any]) -> dict[Any, Any]:
    """Recursively updates `dest` with `mappings`.

    Unlike the standard dict union operator, this supports substructures and checks matching value types.
    """
    result = deepcopy(dest)

    for source in mappings:
        for key, value in source.items():
            if (key in result) and (type(result[key]) is not type(value)):
                raise TypeError(
                    f"Destination type '{type(result[key])}' differs from source type '{type(value)}' for key '{key}'",
                )

            if (key in result) and isinstance(value, dict):
                result[key] = deep_update(result[key], value)  # type: ignore[arg-type]
            elif (key in result) and isinstance(value, list):
                if len(result[key]) != len(value):  # type: ignore[arg-type]
                    err_msg = (
                        f"Destination list length '{len(result[key])}' differs from "
                        + f"source list length '{len(value)}' for key '{key}'"  # type: ignore[arg-type]
                    )
                    raise TypeError(err_msg)
                result[key] = list(starmap(deep_update, zip(result[key], value, strict=True)))  # type: ignore[arg-type]
            else:
                result[key] = value

    return result


def model_to_field_names(model: Any) -> Optional[str]:  # noqa: ANN401
    """Parses model and returns field names as a comma separated string.

    If a field has an alias, it will be used as a field name. If a field accepts different type(s),
    they will be parsed recursively and found field names combined to remove duplicates.
    Field names from a referenced models will be mentioned as a subset of an original field in parentheses::

        id,name,value(id,period(id,minutes,presentation),description)
    """

    def model_to_fields(m: type[BaseModel]) -> dict[str, Any]:
        model_schema = m.model_json_schema(ref_template="{model}")
        definitions = model_schema.get("$defs", {})

        def schema_to_fields(schema: dict[str, Any]) -> dict[str, Any]:
            def type_to_fields(field_type: dict[str, Any]) -> dict[str, Any]:
                if "$ref" in field_type:
                    return schema_to_fields(definitions[field_type["$ref"]])
                elif field_type.get("type") == "array":
                    return type_to_fields(field_type["items"])
                elif sub_types := field_type.get("anyOf", field_type.get("allOf", field_type.get("oneOf"))):
                    return deep_update({}, *map(type_to_fields, sub_types))
                else:
                    return {}

            # Only process if schema has properties (i.e., it's a model schema, not a primitive type)
            if "properties" not in schema:
                return {}
            return {name: type_to_fields(value) for name, value in schema["properties"].items()}

        return schema_to_fields(model_schema)

    def fields_to_csv(fields: dict[str, Any]) -> str:
        return ",".join(
            f"{field_name}({field_value})" if (field_value := fields_to_csv(value)) else field_name
            for field_name, value in fields.items()
        )

    # Extract origin type from annotated type
    if get_origin(model) is Annotated:
        model = get_args(model)[0]

    # `get_args` returns a sequence of the types included in the union type
    # or an empty sequence if the `model` is a base type
    models = get_args(model) or (model,)
    fields_dict = deep_update({}, *map(model_to_fields, models))

    return fields_to_csv(fields_dict) or None


def obj_to_dict(obj: Optional[BaseModel]) -> Optional[dict[str, Any]]:
    """
    Converts pydantic model instance to dictionary including nested fields.
    Unset fields or fields without default values will be omitted.
    """
    # `exclude_none=True` on its own is not sufficient, because it should be possible
    # to set a field to None explicitly (e.g. to unassign a ticket).
    # `exclude_unset=True` on its own is not sufficient, because the default value
    # for $type fields should be used to simplify the creation of request objects.
    return obj and deep_update(
        obj.model_dump(by_alias=True, exclude_unset=True),
        obj.model_dump(by_alias=True, exclude_none=True),
    )


class YouTrackTimestampEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:  # noqa: ANN401
        def to_youtrack_timestamp(dt: datetime) -> int:
            return int(dt.timestamp() * 1000)

        match o:
            case datetime():
                return to_youtrack_timestamp(o)
            case date():
                return to_youtrack_timestamp(datetime.combine(o, time(hour=12, tzinfo=UTC)))
            case _:
                return json.JSONEncoder.default(self, o)


def custom_json_dumps(obj: Any) -> str:  # noqa: ANN401
    return json.dumps(obj, cls=YouTrackTimestampEncoder, allow_nan=False)


def obj_to_json(obj: Optional[BaseModel]) -> str:
    return custom_json_dumps(obj_to_dict(obj))


def get_single_value[T](values: Collection[T]) -> T:
    try:
        (value,) = values
    except ValueError as e:
        raise NonSingleValueError(f"single element expected, found: {values}") from e
    return value


def get_issue_custom_field(issue: Issue, field_name: str) -> IssueCustomFieldType:
    def _filter_func(field: IssueCustomFieldType) -> bool:
        return field.name == field_name

    custom_fields = issue.custom_fields if issue.custom_fields else []  # type: ignore[assignment]
    return get_single_value(tuple(filter(_filter_func, custom_fields)))  # type: ignore[arg-type]
