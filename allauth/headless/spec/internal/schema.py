from pathlib import Path
from typing import Optional

from django.urls import reverse
from django.urls.exceptions import Resolver404

from allauth.account import app_settings as account_settings
from allauth.account.internal.flows.signup import base_signup_form_class
from allauth.core.internal.urlkit import script_aware_resolve
from allauth.headless import app_settings
from allauth.headless.adapter import get_adapter
from allauth.headless.spec.internal.openapikit import spec_for_dataclass, spec_for_field


def get_schema() -> dict:
    import yaml

    path = Path(__file__).parent.parent / "doc/openapi.yaml"
    with open(path, "rb") as f:
        spec = yaml.safe_load(f)

    path = Path(__file__).parent.parent / "doc/description.md"
    with open(path, "rb") as f:
        description = f.read().decode("utf8")

    spec["info"]["description"] = description

    specify_user(spec)
    chroot(spec)
    pin_client(spec)
    drop_unused_client_parameter(spec)
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

    processed_paths = {}
    client_value = app_settings.CLIENTS[0]
    http_methods = [
        "get",
        "post",
        "put",
        "delete",
        "options",
        "head",
        "patch",
        "trace",
    ]

    def remove_client_param(parameters: list) -> Optional[list]:
        filtered = [
            p
            for p in parameters
            if not (
                isinstance(p, dict)
                and p.get("$ref") == "#/components/parameters/Client"
            )
        ]
        return filtered or None

    for path_key, path_item in spec["paths"].items():
        current_path_item = dict(path_item)
        processed_path_key = path_key.replace("{client}", client_value)

        if "parameters" in current_path_item:
            new_params = remove_client_param(current_path_item["parameters"])
            if new_params:
                current_path_item["parameters"] = new_params
            else:
                current_path_item.pop("parameters")

        for method_name in http_methods:
            if method_name in current_path_item:
                operation_item = current_path_item[method_name]
                if isinstance(operation_item, dict) and "parameters" in operation_item:
                    new_params = remove_client_param(operation_item["parameters"])
                    if new_params:
                        operation_item["parameters"] = new_params
                    else:
                        operation_item.pop("parameters")

        processed_paths[processed_path_key] = current_path_item

    spec["paths"] = processed_paths


def drop_unused_client_parameter(spec: dict) -> None:
    if len(app_settings.CLIENTS) != 1:
        return

    if components := spec.get("components"):
        if parameters := components.get("parameters"):
            parameters.pop("Client", None)


def drop_unused_paths(spec: dict) -> set:
    paths = spec["paths"]
    used_tags = set()
    for path, path_spec in list(paths.items()):
        found_path = False
        for client in app_settings.CLIENTS:
            try:
                script_aware_resolve(path.replace("{client}", client))
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
    for field_name, field in form_class.base_fields.items():
        is_required = hasattr(field, "required") and field.required
        field_spec = spec_for_field(field)
        if is_required:
            base_signup["required"].append(field_name)
        base_signup["properties"][field_name] = field_spec


def specify_user(spec: dict) -> None:
    dc = get_adapter().get_user_dataclass()
    schema, example = spec_for_dataclass(dc)
    spec["components"]["schemas"]["User"] = schema
    example_value = spec["components"]["examples"]["User"]["value"]
    example_value.clear()
    example_value.update(example)
