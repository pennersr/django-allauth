from pathlib import Path

from django import forms
from django.urls import resolve, reverse
from django.urls.exceptions import Resolver404

from allauth.account import app_settings as account_settings
from allauth.account.internal.flows.signup import base_signup_form_class
from allauth.headless import app_settings


def get_schema() -> dict:
    import yaml

    path = Path(__file__).parent.parent / "doc/openapi.yaml"
    with open(path, "rb") as f:
        spec = yaml.safe_load(f)

    path = Path(__file__).parent.parent / "doc/description.md"
    with open(path, "rb") as f:
        description = f.read().decode("utf8")

    spec["info"]["description"] = description

    chroot(spec)
    pin_client(spec)
    used_tags = drop_unused_paths(spec)
    drop_unused_tags(spec, used_tags)
    drop_unused_tag_groups(spec, used_tags)
    specify_signup_fields(spec)
    specify_custom_signup_form(spec)
    return spec


def chroot(spec: dict) -> None:
    url = reverse("headless:openapi_yaml")
    root = url.rpartition("/")[0]
    paths = spec["paths"].items()
    spec["paths"] = {}
    for path, path_spec in paths:
        new_path = path.replace("/_allauth", root)
        spec["paths"][new_path] = path_spec


def pin_client(spec: dict) -> None:
    if len(app_settings.CLIENTS) != 1:
        return
    client = app_settings.CLIENTS[0]
    paths = spec["paths"].items()
    spec["paths"] = {}
    for path, path_spec in paths:
        new_path = path.replace("{client}", client)
        spec["paths"][new_path] = path_spec


def drop_unused_paths(spec: dict) -> set:
    paths = spec["paths"]
    used_tags = set()
    for path, path_spec in list(paths.items()):
        found_path = False
        for client in app_settings.CLIENTS:
            try:
                resolve(path.replace("{client}", client))
                found_path = True
                break
            except Resolver404:
                pass
        if found_path:
            for method, method_spec in path_spec.items():
                used_tags.update(method_spec["tags"])
        else:
            paths.pop(path)
    return used_tags


def drop_unused_tags(spec: dict, used_tags: set) -> None:
    tags = spec["tags"]
    spec["tags"] = []
    for tag in tags:
        if tag["name"] not in used_tags:
            continue
        spec["tags"].append(tag)


def drop_unused_tag_groups(spec: dict, used_tags: set) -> None:
    tag_groups = spec["x-tagGroups"]
    spec["x-tagGroups"] = []
    for tag_group in tag_groups:
        if any([t in used_tags for t in tag_group["tags"]]):
            spec["x-tagGroups"].append(tag_group)


def specify_signup_fields(spec: dict) -> None:
    base_signup = spec["components"]["schemas"]["BaseSignup"]
    signup = spec["components"]["schemas"]["Signup"]
    properties = base_signup["properties"]
    required_fields = []
    for field_name in ("email", "phone", "username"):
        field = account_settings.SIGNUP_FIELDS.get(field_name)
        if not field:
            properties.pop(field_name)
        elif field["required"]:
            required_fields.append(field_name)
    base_signup["required"] = required_fields
    password_field = account_settings.SIGNUP_FIELDS.get("password1")
    if not password_field:
        signup["allOf"] = signup["allOf"][:1]
    elif not password_field["required"]:
        signup["allOf"][1]["required"].remove("password")


def specify_custom_signup_form(spec: dict) -> None:
    form_class = base_signup_form_class()
    base_signup = spec["components"]["schemas"]["BaseSignup"]
    field_mapping = {
        forms.CharField: {"type": "string"},
        forms.IntegerField: {"type": "integer"},
        forms.FloatField: {"type": "number"},
        forms.BooleanField: {"type": "boolean"},
        forms.DateField: {"type": "string", "format": "date"},
        forms.DateTimeField: {"type": "string", "format": "date-time"},
        forms.EmailField: {"type": "string", "format": "email"},
        forms.URLField: {"type": "string", "format": "uri"},
        forms.DecimalField: {
            "type": "string",
            "format": "decimal",
            "pattern": r"^\d+(\.\d+)?$",
        },
    }
    for field_name, field in form_class.base_fields.items():
        field_spec = field_mapping.get(type(field), {"type": "string"})
        if not field_spec:
            continue
        field_spec = dict(field_spec)
        if hasattr(field, "max_length") and field.max_length:
            field_spec["maxLength"] = field.max_length
        if hasattr(field, "min_length") and field.min_length:
            field_spec["minLength"] = field.min_length
        if hasattr(field, "required") and field.required:
            base_signup["required"].append(field_name)
        if hasattr(field, "help_text") and field.help_text:
            field_spec["description"] = field.help_text
        base_signup["properties"][field_name] = field_spec
