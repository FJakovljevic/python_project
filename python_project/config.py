import os
import re

import yaml
from box import Box
from dotenv import load_dotenv


def load_file(file_path: str) -> str:
    """Load file as a string."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def populate_yaml_with_env_variables(yaml_str: str, default_separator: str = "|") -> str:
    """Replace ${VAR_NAME} placeholder with os.environ['VAR_NAME'].

    Placeholder can also specify default value like this ${VAR_NAME|default}.
    If default is not specified and VAR_NAME is not in ENV it will raise an error.
    """
    # Pattern to match ${VAR_NAME|default} in the YAML string
    pattern = re.compile(r"\$\{(\w+(?:\|\w+)?)\}")

    def get_env_val_or_default(matched_placeholder: re.Match) -> str:
        """Extract value for placeholder from ENV if exists."""
        placeholder = matched_placeholder.group(1)
        var_name, _, default = placeholder.partition(default_separator)

        if value := os.environ.get(var_name, default):
            return value

        raise KeyError(f"Environment variable '{var_name}' not found and no default provided.")

    # Replace all occurrences in the yaml_str
    return pattern.sub(get_env_val_or_default, yaml_str)


def load_env_yaml(path: str) -> Box:
    """Load config yaml file and fill it with env variables."""
    yaml_str = load_file(path)
    yaml_populated_str = populate_yaml_with_env_variables(yaml_str)
    return Box(yaml.safe_load(yaml_populated_str))


class ConfigMeta(type):
    def __init__(cls, _name: str, _bases: tuple, _dct: dict):
        # load env variables to environment - for local runs
        load_dotenv()

        # load config file
        profile = os.environ.get("PROFILE", "dev")
        configs_location = os.environ.get("CONFIGS_LOCATION", "configs")
        configs_file = f"{configs_location}/{profile}.yml"
        cls.config = load_env_yaml(configs_file)

    def __getattr__(cls, name: str):
        return cls.config[name]


class Config(metaclass=ConfigMeta):
    """Configuration class to access settings from YAML files and ENV variables.

    Usage:
        import Config

        # Access application settings
        print(Config.app.profile)
        print(Config.app.log_level)
    """
