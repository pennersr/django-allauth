from dataclasses import dataclass, field

from allauth.headless.spec.internal.openapikit import spec_for_dataclass


@dataclass
class NestedDataClass:
    string: str
    integer: int = field(
        metadata={
            "description": "Some nested int",
            "example": 42,
        }
    )


@dataclass
class ExampleDataclass:
    optional_integer: int | None
    integer: int
    optional_string: str | None
    string: str
    number: float = field(
        metadata={
            "description": "Some float",
            "example": "3.14",
        }
    )
    nested: NestedDataClass | None


def test_spec_for_dataclass():
    spec = spec_for_dataclass(ExampleDataclass)
    assert spec == (
        {
            "properties": {
                "integer": {
                    "type": "integer",
                },
                "number": {
                    "description": "Some float",
                    "example": "3.14",
                    "format": "float",
                    "type": "number",
                },
                "optional_integer": {
                    "type": "integer",
                },
                "optional_string": {
                    "type": "string",
                },
                "string": {
                    "type": "string",
                },
                "nested": {
                    "example": {"integer": 42},
                    "properties": {
                        "string": {
                            "type": "string",
                        },
                        "integer": {
                            "description": "Some nested int",
                            "example": 42,
                            "type": "integer",
                        },
                    },
                    "required": [
                        "string",
                        "integer",
                    ],
                    "type": "object",
                },
            },
            "required": [
                "integer",
                "string",
                "number",
            ],
            "type": "object",
        },
        {
            "number": "3.14",
        },
    )
