import re


def slugify(value: str):
    return re.sub(r'[^a-zA-Z0-9]+', '_', value).lower()

def tokenize(value: str):
    return re.split(r'[^a-zA-Z0-9]+', value)
