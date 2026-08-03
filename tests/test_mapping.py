"""Unit tests for Dynamic Rule Mapping Subsystem (crypto/ca/mapping.py)."""

import json
import pytest

import crypto.ca as ca
from crypto.ca.mapping import (
    CURRENT_SCHEMA_VERSION,
    Rule,
    RuleSequence,
    RuleLookup,
    RuleMapping,
    validate_rule_sequence,
    build_rule_lookup,
    get_rule,
    generate_rule_sequence,
    map_rules,
    invert_rule_mapping,
    load_rule_configuration,
    export_rule_configuration,
    serialize_rule_sequence,
    deserialize_rule_sequence,
    compare_rule_sequences,
    merge_rule_sequences,
    unique_rules,
    rule_exists,
    rule_index,
    rotate_rule_sequence,
    cycle_rule,
)


class TestRuleSequenceValidation:
    """Tests for validate_rule_sequence."""

    def test_valid_rule_sequences(self):
        """Verify valid integer rule sequences are accepted."""
        assert validate_rule_sequence([0, 30, 90, 110, 255]) == [0, 30, 90, 110, 255]
        assert validate_rule_sequence((30, 90)) == [30, 90]

    def test_empty_rule_sequence(self):
        """Verify empty sequence raises ValueError."""
        with pytest.raises(ValueError, match="Rule sequence cannot be empty"):
            validate_rule_sequence([])

    @pytest.mark.parametrize("invalid_seq", [123, "30", None, 30.0])
    def test_invalid_sequence_types(self, invalid_seq):
        """Verify non-list/tuple types raise TypeError."""
        with pytest.raises(TypeError, match="must be a list or tuple"):
            validate_rule_sequence(invalid_seq)

    def test_invalid_rule_elements(self):
        """Verify invalid rule values raise appropriate exceptions."""
        with pytest.raises(ValueError, match="Rule must be between 0 and 255"):
            validate_rule_sequence([30, 256])
        with pytest.raises(TypeError, match="Rule must be an integer"):
            validate_rule_sequence([30, "90"])
        with pytest.raises(TypeError, match="Rule must be an integer"):
            validate_rule_sequence([30, True])

    def test_forbidden_duplicates(self):
        """Verify duplicate rules raise ValueError when allow_duplicates=False."""
        assert validate_rule_sequence([30, 90, 30], allow_duplicates=True) == [30, 90, 30]
        with pytest.raises(ValueError, match="contains duplicate rules"):
            validate_rule_sequence([30, 90, 30], allow_duplicates=False)


class TestRuleLookup:
    """Tests for build_rule_lookup and get_rule."""

    def test_build_rule_lookup(self):
        """Verify building lookup dictionary."""
        lookup = build_rule_lookup([30, 90, 110])
        assert lookup == {0: 30, 1: 90, 2: 110}

    def test_get_rule(self):
        """Verify retrieving rule by index."""
        lookup = build_rule_lookup([30, 90, 110])
        assert get_rule(0, lookup) == 30
        assert get_rule(1, lookup) == 90
        assert get_rule(2, lookup) == 110

    def test_get_rule_out_of_bounds(self):
        """Verify index out of bounds raises IndexError."""
        lookup = build_rule_lookup([30, 90])
        with pytest.raises(IndexError, match="out of bounds"):
            get_rule(2, lookup)
        with pytest.raises(IndexError, match="out of bounds"):
            get_rule(-1, lookup)

    def test_get_rule_invalid_types(self):
        """Verify invalid lookup or index types raise TypeError."""
        lookup = build_rule_lookup([30, 90])
        with pytest.raises(TypeError, match="must be a dictionary"):
            get_rule(0, "not_a_dict")
        with pytest.raises(TypeError, match="must be an integer"):
            get_rule(1.5, lookup)
        with pytest.raises(TypeError, match="must be an integer"):
            get_rule(True, lookup)


class TestRuleSequenceGeneration:
    """Tests for generate_rule_sequence."""

    def test_generate_rule_sequence_defaults(self):
        """Verify generating rule sequence with default step 1."""
        seq = generate_rule_sequence(30, count=4)
        assert seq == [30, 31, 32, 33]

    def test_generate_rule_sequence_step_and_wrap(self):
        """Verify stepping and wrapping around 255."""
        seq = generate_rule_sequence(250, count=3, step=5)
        # 250, 255, (260 % 256 = 4)
        assert seq == [250, 255, 4]

    def test_generate_rule_sequence_invalid_inputs(self):
        """Verify invalid parameters raise ValueError or TypeError."""
        with pytest.raises(ValueError, match="Rule must be between 0 and 255"):
            generate_rule_sequence(256, count=5)
        with pytest.raises(ValueError, match="Count must be positive"):
            generate_rule_sequence(30, count=0)
        with pytest.raises(TypeError):
            generate_rule_sequence(30, count=1.5)
        with pytest.raises(TypeError):
            generate_rule_sequence(30, count=5, step="1")


class TestRuleMappingAndInversion:
    """Tests for map_rules and invert_rule_mapping."""

    def test_map_rules_valid(self):
        """Verify generating valid rule mapping."""
        source = [30, 90, 110]
        target = [150, 180, 200]
        mapping = map_rules(source, target)
        assert mapping == {30: 150, 90: 180, 110: 200}

    def test_map_rules_unequal_lengths(self):
        """Verify map_rules raises ValueError for unequal sequence lengths."""
        with pytest.raises(ValueError, match="equal length"):
            map_rules([30, 90], [150])

    def test_map_rules_duplicate_source(self):
        """Verify duplicate source rules raise ValueError."""
        with pytest.raises(ValueError, match="Source rules must be unique"):
            map_rules([30, 30], [90, 110])

    def test_map_rules_bijective(self):
        """Verify bijective constraint enforcement."""
        # Non-unique target when bijective=True
        with pytest.raises(ValueError, match="Target rules must be unique"):
            map_rules([30, 90], [150, 150], bijective=True)

    def test_invert_rule_mapping_valid(self):
        """Verify inverting a 1-to-1 rule mapping."""
        mapping = {30: 150, 90: 180}
        inverted = invert_rule_mapping(mapping)
        assert inverted == {150: 30, 180: 90}

    def test_invert_rule_mapping_duplicate_targets(self):
        """Verify inverting mapping with duplicate targets raises ValueError."""
        mapping = {30: 150, 90: 150}
        with pytest.raises(ValueError, match="duplicate target rule"):
            invert_rule_mapping(mapping)

    def test_invert_rule_mapping_invalid_inputs(self):
        """Verify invalid mapping types or empty dict raise errors."""
        with pytest.raises(TypeError):
            invert_rule_mapping("invalid")
        with pytest.raises(ValueError, match="cannot be empty"):
            invert_rule_mapping({})


class TestConfigurationSupport:
    """Tests for load_rule_configuration and export_rule_configuration."""

    def test_load_and_export_rule_configuration(self):
        """Verify valid configuration import and export."""
        config = export_rule_configuration(
            rules=[30, 90, 110],
            default_rule=30,
            active_rule=90,
            metadata={"author": "IEEE Test"},
        )
        assert config["version"] == CURRENT_SCHEMA_VERSION
        assert config["rules"] == [30, 90, 110]
        assert config["default_rule"] == 30
        assert config["active_rule"] == 90
        assert config["metadata"] == {"author": "IEEE Test"}

        loaded = load_rule_configuration(config)
        assert loaded == config

    def test_load_configuration_validation_errors(self):
        """Verify configuration schema and value validation errors."""
        with pytest.raises(TypeError):
            load_rule_configuration("not_a_dict")

        # Unknown key
        with pytest.raises(ValueError, match="Unknown configuration key"):
            load_rule_configuration({"version": 1, "rules": [30], "unknown": 123})

        # Missing version
        with pytest.raises(ValueError, match="missing required 'version' key"):
            load_rule_configuration({"rules": [30]})

        # Version invalid type
        with pytest.raises(TypeError, match="Version must be an integer"):
            load_rule_configuration({"version": "1", "rules": [30]})

        # Missing rules
        with pytest.raises(ValueError, match="missing required 'rules' key"):
            load_rule_configuration({"version": 1})

        # Invalid version
        with pytest.raises(ValueError, match="Unsupported configuration schema version"):
            load_rule_configuration({"version": 999, "rules": [30]})

        # Default rule not in rules list
        with pytest.raises(ValueError, match="Default rule 150 must be present"):
            load_rule_configuration({"version": 1, "rules": [30, 90], "default_rule": 150})

        # Active rule not in rules list
        with pytest.raises(ValueError, match="Active rule 150 must be present"):
            load_rule_configuration({"version": 1, "rules": [30, 90], "active_rule": 150})

        # Invalid metadata type
        with pytest.raises(TypeError, match="Metadata must be a dictionary"):
            load_rule_configuration({"version": 1, "rules": [30], "metadata": "invalid"})


class TestSerialization:
    """Tests for serialize_rule_sequence and deserialize_rule_sequence."""

    def test_serialize_deserialize_roundtrip(self):
        """Verify JSON serialization and deserialization roundtrip."""
        rules = [30, 90, 110]
        json_str = serialize_rule_sequence(
            rules, default_rule=30, active_rule=90, metadata={"tag": "v1"}
        )
        assert isinstance(json_str, str)

        deserialized = deserialize_rule_sequence(json_str)
        assert deserialized["version"] == CURRENT_SCHEMA_VERSION
        assert deserialized["rules"] == rules
        assert deserialized["default_rule"] == 30
        assert deserialized["active_rule"] == 90
        assert deserialized["metadata"] == {"tag": "v1"}

    def test_deserialize_malformed_json(self):
        """Verify deserializing invalid JSON raises ValueError."""
        with pytest.raises(ValueError, match="Invalid JSON string"):
            deserialize_rule_sequence("{malformed json")

    def test_deserialize_invalid_type(self):
        """Verify deserializing non-string data raises TypeError."""
        with pytest.raises(TypeError, match="must be a string"):
            deserialize_rule_sequence(12345)


class TestMappingUtilities:
    """Tests for sequence comparison, merging, uniqueness, checking, rotation, and cycling."""

    def test_compare_rule_sequences(self):
        """Verify compare_rule_sequences helper."""
        assert compare_rule_sequences([30, 90], (30, 90)) is True
        assert compare_rule_sequences([30, 90], [30, 110]) is False
        assert compare_rule_sequences([30, 90], "invalid") is False

    def test_merge_rule_sequences(self):
        """Verify merging rule sequences."""
        a = [30, 90]
        b = [90, 110]
        assert merge_rule_sequences(a, b, unique_only=False) == [30, 90, 90, 110]
        assert merge_rule_sequences(a, b, unique_only=True) == [30, 90, 110]

    def test_unique_rules(self):
        """Verify ordering preservation when getting unique rules."""
        seq = [30, 90, 30, 110, 90, 150]
        assert unique_rules(seq) == [30, 90, 110, 150]

    def test_rule_exists_and_index(self):
        """Verify rule_exists and rule_index helpers."""
        seq = [30, 90, 110]
        assert rule_exists(90, seq) is True
        assert rule_exists(150, seq) is False

        assert rule_index(90, seq) == 1
        with pytest.raises(ValueError, match="not found in rule sequence"):
            rule_index(150, seq)

    def test_rotate_rule_sequence(self):
        """Verify sequence left rotation."""
        seq = [30, 90, 110, 150]
        assert rotate_rule_sequence(seq, shift=1) == [90, 110, 150, 30]
        assert rotate_rule_sequence(seq, shift=4) == [30, 90, 110, 150]
        assert rotate_rule_sequence(seq, shift=5) == [90, 110, 150, 30]
        assert rotate_rule_sequence(seq, shift=-1) == [150, 30, 90, 110]

        with pytest.raises(TypeError):
            rotate_rule_sequence(seq, shift=1.5)

    def test_cycle_rule(self):
        """Verify modular cyclic access to rules."""
        seq = [30, 90, 110]
        assert cycle_rule(seq, 0) == 30
        assert cycle_rule(seq, 1) == 90
        assert cycle_rule(seq, 2) == 110
        assert cycle_rule(seq, 3) == 30
        assert cycle_rule(seq, 5) == 110

        with pytest.raises(TypeError):
            cycle_rule(seq, "0")

    def test_package_imports(self):
        """Verify importing mapping symbols directly from package root crypto.ca."""
        assert hasattr(ca, "map_rules")
        assert hasattr(ca, "serialize_rule_sequence")
        assert hasattr(ca, "CURRENT_SCHEMA_VERSION")
        assert ca.serialize_rule_sequence([30]) is not None
