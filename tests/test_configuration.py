"""
Phase 4.1 Configuration Validation Tests (`tests/test_configuration.py`).

Verifies default configurations, custom configurations, missing optional fields,
invalid schemas, malformed JSON, unknown keys, and backward compatibility.
"""

import json
import pytest

from crypto.ca.mapping import (
    ALLOWED_CONFIG_KEYS,
    CURRENT_SCHEMA_VERSION,
    export_rule_configuration,
    load_rule_configuration,
    serialize_rule_sequence,
    deserialize_rule_sequence,
    validate_rule_sequence,
    validate_rule,
)


class TestConfigurationValidation:
    """Tests for CA and engine configuration validation and schema enforcement."""

    def test_default_configuration_export_and_load(self) -> None:
        """Verify default configuration dictionary export and loading."""
        rules = [30, 45, 105, 150]
        config = export_rule_configuration(rules, default_rule=rules[0], active_rule=rules[0])

        assert config["version"] == CURRENT_SCHEMA_VERSION
        assert config["rules"] == rules
        assert config["default_rule"] == rules[0]

        loaded = load_rule_configuration(config)
        assert loaded["rules"] == rules
        assert loaded["version"] == CURRENT_SCHEMA_VERSION
        assert loaded["default_rule"] == rules[0]
        assert loaded["active_rule"] == rules[0]

    def test_custom_configuration_with_metadata(self) -> None:
        """Verify loading custom configuration with extra metadata."""
        custom_config = {
            "version": 1,
            "rules": [30, 90, 150],
            "default_rule": 30,
            "active_rule": 90,
            "metadata": {
                "author": "Chintan",
                "description": "Custom rule configuration for testing",
            },
        }

        loaded = load_rule_configuration(custom_config)
        assert loaded["rules"] == [30, 90, 150]
        assert loaded["metadata"]["author"] == "Chintan"

    def test_missing_optional_fields(self) -> None:
        """Verify configuration validation works when optional fields are omitted."""
        partial_config = {
            "version": 1,
            "rules": [30, 45, 60],
        }

        loaded = load_rule_configuration(partial_config)
        assert loaded["rules"] == [30, 45, 60]
        assert loaded["default_rule"] is None
        assert loaded["active_rule"] is None
        assert loaded["metadata"] == {}

    def test_json_serialization_deserialization_roundtrip(self) -> None:
        """Verify JSON serialization and deserialization of rule configurations."""
        rules = [30, 60, 90, 120]
        json_str = serialize_rule_sequence(rules)

        assert isinstance(json_str, str)
        deserialized = deserialize_rule_sequence(json_str)

        assert deserialized["version"] == CURRENT_SCHEMA_VERSION
        assert deserialized["rules"] == rules

    def test_invalid_type_raises_type_error(self) -> None:
        """Verify non-dictionary input raises TypeError."""
        with pytest.raises(TypeError):
            load_rule_configuration("not a dict")

    def test_unknown_keys_raises_value_error(self) -> None:
        """Verify extra unexpected keys raise ValueError."""
        invalid_config = {
            "version": 1,
            "rules": [30],
            "unknown_feature_flag": True,
        }
        with pytest.raises(ValueError, match="Unknown configuration key"):
            load_rule_configuration(invalid_config)

    def test_missing_version_raises_value_error(self) -> None:
        """Verify missing 'version' key raises ValueError."""
        invalid_config = {
            "rules": [30],
        }
        with pytest.raises(ValueError, match="missing required 'version' key"):
            load_rule_configuration(invalid_config)

    def test_unsupported_version_raises_value_error(self) -> None:
        """Verify unsupported schema version raises ValueError."""
        invalid_config = {
            "version": 99,
            "rules": [30],
        }
        with pytest.raises(ValueError, match="Unsupported configuration schema version"):
            load_rule_configuration(invalid_config)

    def test_missing_rules_raises_value_error(self) -> None:
        """Verify missing 'rules' key raises ValueError."""
        invalid_config = {
            "version": 1,
        }
        with pytest.raises(ValueError, match="missing required 'rules' key"):
            load_rule_configuration(invalid_config)

    def test_invalid_rule_value_raises_value_error(self) -> None:
        """Verify out-of-range rule index (e.g. 256) raises ValueError."""
        invalid_config = {
            "version": 1,
            "rules": [30, 999],
        }
        with pytest.raises(ValueError):
            load_rule_configuration(invalid_config)

    def test_malformed_json_deserialization(self) -> None:
        """Verify malformed JSON raises ValueError during deserialization."""
        with pytest.raises(ValueError, match="Invalid JSON string"):
            deserialize_rule_sequence("{ malformed json }")
