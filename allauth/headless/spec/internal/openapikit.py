import datetime
from typing import Any, Dict, Tuple

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


def spec_for_dataclass(dc) -> Tuple[dict, dict]:
    example = {}
    props = {}
    for field_id, field in dc.__dataclass_fields__.items():
        example[field_id] = field.metadata["example"]
        descriptor = {
            "description": field.metadata["description"],
            "example": field.metadata["example"],
        }
        if field.type is str:
            descriptor.update({"type": "string"})
        elif field.type is int:
            descriptor.update({"type": "integer"})
        elif field.type is float:
            descriptor.update({"type": "number", "format": "float"})
        elif field.type is bool:
            descriptor.update({"type": "boolean"})
        elif field.type is datetime.datetime:
            descriptor.update({"type": "string", "format": "date-time"})
        elif field.type is datetime.date:
            descriptor.update({"type": "string", "format": "date"})
        elif field.type is list:
            descriptor.update({"type": "array"})
        elif field.type is dict:
            descriptor.update({"type": "object"})
        else:
            descriptor.update({"type": "string"})
        props[field_id] = descriptor
    schema = {"type": "object", "properties": props}
    return schema, example
