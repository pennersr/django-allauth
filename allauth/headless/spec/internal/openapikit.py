import dataclasses
import datetime
from typing import Any, Dict, Tuple, Union, get_args, get_origin

from django import forms

from allauth.account.fields import EmailField


FIELD_MAPPING = {
    forms.CharField: {"type": "string"},
    forms.IntegerField: {"type": "integer"},
    forms.FloatField: {"type": "number"},
    forms.BooleanField: {"type": "boolean"},
    forms.DateField: {"type": "string", "format": "date"},
    forms.DateTimeField: {"type": "string", "format": "date-time"},
    forms.EmailField: {"type": "string", "format": "email"},
    EmailField: {"type": "string", "format": "email"},
    forms.URLField: {"type": "string", "format": "uri"},
    forms.DecimalField: {
        "type": "string",
        "format": "decimal",
        "pattern": r"^\d+(\.\d+)?$",
    },
}


def spec_for_field(field: forms.Field) -> Dict[str, Any]:
    field_spec: Dict[str, Any] = FIELD_MAPPING.get(type(field), {"type": "string"})
    field_spec = dict(field_spec)
    if hasattr(field, "max_length") and field.max_length:
        field_spec["maxLength"] = field.max_length
    if hasattr(field, "min_length") and field.min_length:
        field_spec["minLength"] = field.min_length
    if hasattr(field, "help_text") and field.help_text:
        field_spec["description"] = field.help_text
    return field_spec


def unwrap_optional_type(typ):
    if get_origin(typ) is not Union:
        return typ, True
    args = get_args(typ)
    if len(args) != 2 or type(None) not in args:
        return typ, True
    return args[0], False


def spec_for_dataclass(dc) -> Tuple[dict, dict]:
    example = {}
    props = {}
    required = []
    for field_id, field in dc.__dataclass_fields__.items():
        descriptor = {}
        if description := field.metadata.get("description"):
            descriptor["description"] = description
        if exa := field.metadata.get("example"):
            descriptor["example"] = exa
            example[field_id] = exa
        field_type, req = unwrap_optional_type(field.type)
        if req:
            required.append(field_id)
        if field_type is str:
            descriptor.update({"type": "string"})
        elif field_type is int:
            descriptor.update({"type": "integer"})
        elif field_type is float:
            descriptor.update({"type": "number", "format": "float"})
        elif field_type is bool:
            descriptor.update({"type": "boolean"})
        elif field_type is datetime.datetime:
            descriptor.update({"type": "string", "format": "date-time"})
        elif field_type is datetime.date:
            descriptor.update({"type": "string", "format": "date"})
        elif field_type is list:
            descriptor.update({"type": "array"})
        elif field_type is dict:
            descriptor.update({"type": "object"})
        elif dataclasses.is_dataclass(field_type):
            nested_schema, nested_exmple = spec_for_dataclass(field_type)
            descriptor.update(nested_schema)
            descriptor["example"] = nested_exmple
        else:
            descriptor.update({"type": "string"})
        props[field_id] = descriptor
    schema = {"type": "object", "properties": props, "required": required}
    return schema, example
