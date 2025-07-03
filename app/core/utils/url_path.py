DEFAULT_URL_PATH = ''

INVALID_URL_PATHS = [
    'null',
    'undefined',
    'none',
    'empty',
    'null',
    'undefined',
    'none',
    'empty',
]


def format_url_path(path: str):
    if not path: return ''
    
    if path.lower() in INVALID_URL_PATHS:
        return DEFAULT_URL_PATH
    
    return path
