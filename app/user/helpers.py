import secrets


def generate_activation_code():
    return secrets.token_hex(12)
