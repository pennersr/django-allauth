from pathlib import Path

from django.urls import resolve, reverse
from django.urls.exceptions import Resolver404


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
    used_tags = drop_unused_paths(spec)
    drop_unused_tags(spec, used_tags)
    drop_unused_tag_groups(spec, used_tags)
    return spec


def chroot(spec):
    url = reverse("headless:openapi_yaml")
    root = url.rpartition("/")[0]
    paths = spec["paths"].items()
    spec["paths"] = {}
    for path, path_spec in paths:
        new_path = path.replace("/_allauth", root)
        spec["paths"][new_path] = path_spec


def drop_unused_paths(spec):
    paths = spec["paths"]
    used_tags = set()
    for path, path_spec in list(paths.items()):
        found_path = False
        for client in ["browser", "app"]:
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


def drop_unused_tags(spec, used_tags):
    tags = spec["tags"]
    spec["tags"] = []
    for tag in tags:
        if tag["name"] not in used_tags:
            continue
        spec["tags"].append(tag)


def drop_unused_tag_groups(spec, used_tags):
    tag_groups = spec["x-tagGroups"]
    spec["x-tagGroups"] = []
    for tag_group in tag_groups:
        if any([t in used_tags for t in tag_group["tags"]]):
            spec["x-tagGroups"].append(tag_group)
