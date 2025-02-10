import importlib
import os
from unittest import mock

import pytest

from python_project import config


def test_populate_yaml_with_existing_var(monkeypatch):
    """Test replacement of an existing environment variable."""
    monkeypatch.setenv("EXISTING_VAR", "existing_value")
    yaml_str = "app: ${EXISTING_VAR}"
    result = config.populate_yaml_with_env_variables(yaml_str)
    assert result == "app: existing_value"


def test_populate_yaml_with_default_value():
    """Test replacement with a default value."""
    yaml_str = "app: ${NON_EXISTING_VAR|default_value}"
    result = config.populate_yaml_with_env_variables(yaml_str)
    assert result == "app: default_value"


def test_populate_yaml_without_default_raises_error():
    """Test that missing environment variable without a default raises an error."""
    yaml_str = "app: ${NON_EXISTING_VAR}"
    with pytest.raises(KeyError, match="Environment variable 'NON_EXISTING_VAR' not found and no default provided."):
        config.populate_yaml_with_env_variables(yaml_str)


@mock.patch.dict(os.environ, {"PROFILE": "config_test", "TEST_VAL": "test_value", "CONFIGS_LOCATION": "tests/data"})
def test_config_load():
    importlib.reload(config)
    from python_project.config import Config

    assert Config.app.profile == "config_test"
    assert Config.test.var == "test_value"
    assert Config.test.var_def == "default"
