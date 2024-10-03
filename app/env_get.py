from dotenv import dotenv_values


def get_env(name: str) -> str:
    """:return: value by name"""
    config = dotenv_values(".env")
    return config[name]
