import re


def slugify(value: str):
    return re.sub(r'[^a-zA-Z0-9]+', '_', value).lower()
