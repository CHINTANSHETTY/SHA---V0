"""Unit tests for Cellular Automata Utility Module (crypto/ca/utils.py)."""

import random
import pytest

import crypto.ca as ca
from crypto.ca.utils import (
    DEFAULT_PAD_VALUE,
    MIN_STATE_LENGTH,
    VALID_BITS,
    validate_bit,
    validate_state_length,
    validate_width,
    state_from_string,
    state_to_string,
    int_to_state,
    state_to_int,
    zero_state,
    one_state,
    random_state,
    copy_state,
    population_count,
    hamming_distance,
    compare_states,
    invert_state,
    xor_states,
    states_to_matrix,
    matrix_to_states,
    chunk_state,
    flatten_states,
    pad_state,
    trim_state,
)


class TestValidationHelpers:
    """Tests for validate_bit, validate_state_length, and validate_width."""

    @pytest.mark.parametrize("valid_b", [0, 1])
    def test_validate_bit_valid(self, valid_b):
        """Verify 0 and 1 integer bits are valid."""
        assert validate_bit(valid_b) == valid_b

    @pytest.mark.parametrize("invalid_b", [-1, 2, 10])
    def test_validate_bit_out_of_bounds(self, invalid_b):
        """Verify integer values other than 0 or 1 raise ValueError."""
        with pytest.raises(ValueError, match="Bit must be 0 or 1"):
            validate_bit(invalid_b)

    @pytest.mark.parametrize("invalid_t", [True, False, 1.0, "0", None, [0]])
    def test_validate_bit_invalid_types(self, invalid_t):
        """Verify non-integer bit types (including bool) raise TypeError."""
        with pytest.raises(TypeError, match="Bit must be an integer"):
            validate_bit(invalid_t)

    @pytest.mark.parametrize("valid_len", [1, 10, 1000])
    def test_validate_state_length_valid(self, valid_len):
        """Verify state length >= 1 is valid."""
        assert validate_state_length(valid_len) == valid_len

    @pytest.mark.parametrize("invalid_len", [0, -1, -50])
    def test_validate_state_length_invalid(self, invalid_len):
        """Verify state length < 1 raises ValueError."""
        with pytest.raises(ValueError, match="State length must be >="):
            validate_state_length(invalid_len)

    @pytest.mark.parametrize("invalid_t", [True, False, 1.5, "10", None])
    def test_validate_state_length_types(self, invalid_t):
        """Verify non-integer state length types raise TypeError."""
        with pytest.raises(TypeError, match="State length must be an integer"):
            validate_state_length(invalid_t)

    @pytest.mark.parametrize("valid_w", [1, 8, 32, 64])
    def test_validate_width_valid(self, valid_w):
        """Verify width >= 1 is valid."""
        assert validate_width(valid_w) == valid_w

    @pytest.mark.parametrize("invalid_w", [0, -1, -8])
    def test_validate_width_invalid(self, invalid_w):
        """Verify width < 1 raises ValueError."""
        with pytest.raises(ValueError, match="Width must be >="):
            validate_width(invalid_w)

    @pytest.mark.parametrize("invalid_t", [True, False, 4.0, "8", None])
    def test_validate_width_types(self, invalid_t):
        """Verify non-integer width types raise TypeError."""
        with pytest.raises(TypeError, match="Width must be an integer"):
            validate_width(invalid_t)


class TestStateConversions:
    """Tests for state string and integer conversions."""

    def test_state_from_string(self):
        """Verify binary string conversion to list of int bits."""
        assert state_from_string("010101") == [0, 1, 0, 1, 0, 1]
        assert state_from_string("1") == [1]

    def test_state_from_string_invalid(self):
        """Verify invalid inputs for state_from_string raise errors."""
        with pytest.raises(TypeError):
            state_from_string([0, 1])
        with pytest.raises(ValueError, match="State cannot be empty"):
            state_from_string("")
        with pytest.raises(ValueError, match="Invalid binary character"):
            state_from_string("01021")

    def test_state_to_string(self):
        """Verify converting bit sequences to binary strings."""
        assert state_to_string([1, 0, 1]) == "101"
        assert state_to_string((0, 1, 1, 0)) == "0110"
        assert state_to_string("110") == "110"

    def test_state_sequence_validation_errors(self):
        """Verify errors on invalid state sequences and types."""
        with pytest.raises(ValueError, match="State cannot be empty"):
            state_to_string([])
        with pytest.raises(TypeError, match="must be an integer bit"):
            state_to_string([True, False])
        with pytest.raises(ValueError, match="must be 0 or 1"):
            state_to_string([0, 2, 1])
        with pytest.raises(TypeError, match="must be a list/tuple of bits or a binary bit string"):
            state_to_string(12345)

    def test_int_to_state_and_back(self):
        """Verify integer to state conversion and round-trip state_to_int."""
        assert int_to_state(13, width=4) == [1, 1, 0, 1]
        assert int_to_state(255, width=8) == [1, 1, 1, 1, 1, 1, 1, 1]
        assert int_to_state(0, width=4) == [0, 0, 0, 0]

        # Roundtrip check
        for val in (0, 1, 13, 42, 255, 1023):
            assert state_to_int(int_to_state(val, width=12)) == val

    def test_int_to_state_overflow_and_errors(self):
        """Verify overflow and invalid parameters in int_to_state."""
        # 17 in binary requires 5 bits (10001), width=4 max is 15
        with pytest.raises(ValueError, match="overflows specified width"):
            int_to_state(17, width=4)

        with pytest.raises(ValueError, match="must be non-negative"):
            int_to_state(-1, width=4)

        with pytest.raises(TypeError):
            int_to_state(13.0, width=4)

        with pytest.raises(TypeError):
            int_to_state(True, width=4)


class TestStateInitialization:
    """Tests for zero_state, one_state, random_state, and copy_state."""

    def test_zero_and_one_state(self):
        """Verify zero_state and one_state generation."""
        assert zero_state(5) == [0, 0, 0, 0, 0]
        assert one_state(4) == [1, 1, 1, 1]

    def test_random_state_reproducibility(self):
        """Verify random_state determinism with seeds."""
        st1 = random_state(50, seed=42)
        st2 = random_state(50, seed=42)
        assert st1 == st2
        assert len(st1) == 50
        assert set(st1).issubset({0, 1})

    def test_random_state_different_seeds(self):
        """Verify different seeds produce different random states."""
        st1 = random_state(50, seed=1)
        st2 = random_state(50, seed=2)
        assert st1 != st2

    def test_random_state_global_random_isolation(self):
        """Verify random_state does not alter global random module state."""
        random.seed(999)
        global_state_before = random.getstate()
        _ = random_state(100, seed=42)
        global_state_after = random.getstate()
        assert global_state_before == global_state_after

    def test_random_state_invalid_seed(self):
        """Verify invalid seed types raise TypeError."""
        with pytest.raises(TypeError, match="Seed must be an integer"):
            random_state(10, seed="invalid_seed")
        with pytest.raises(TypeError, match="Seed must be an integer"):
            random_state(10, seed=1.5)
        with pytest.raises(TypeError, match="Seed must be an integer"):
            random_state(10, seed=True)

    def test_copy_state_isolation(self):
        """Verify copy_state creates an independent deep copy."""
        original = [0, 1, 1, 0]
        copied = copy_state(original)
        assert copied == original
        assert copied is not original

        copied[0] = 1
        assert original[0] == 0


class TestAnalysisUtilities:
    """Tests for population_count, hamming_distance, compare_states, invert_state, xor_states."""

    def test_population_count(self):
        """Verify population count (number of ones)."""
        assert population_count([0, 0, 0]) == 0
        assert population_count([1, 1, 1]) == 3
        assert population_count("101101") == 4

    def test_hamming_distance(self):
        """Verify Hamming distance calculation."""
        assert hamming_distance([1, 0, 1, 0], [1, 0, 1, 0]) == 0
        assert hamming_distance([1, 0, 1, 0], [0, 1, 0, 1]) == 4
        assert hamming_distance("101001", "001101") == 2

    def test_hamming_distance_unequal_lengths(self):
        """Verify Hamming distance raises ValueError for unequal lengths."""
        with pytest.raises(ValueError, match="equal lengths"):
            hamming_distance([1, 0], [1, 0, 0])

    def test_compare_states(self):
        """Verify state comparison helper."""
        assert compare_states([1, 0, 1], (1, 0, 1)) is True
        assert compare_states("101", [1, 0, 1]) is True
        assert compare_states([1, 0, 1], [1, 0, 0]) is False
        assert compare_states([1, 0], None) is False

    def test_invert_state(self):
        """Verify bitwise state inversion."""
        assert invert_state([1, 0, 1, 0]) == [0, 1, 0, 1]
        assert invert_state(invert_state([1, 0, 1])) == [1, 0, 1]

    def test_xor_states(self):
        """Verify bitwise XOR of equal length states."""
        assert xor_states([1, 1, 0, 0], [1, 0, 1, 0]) == [0, 1, 1, 0]
        # XOR with self yields all zeros
        st = [1, 0, 1, 1, 0]
        assert xor_states(st, st) == [0, 0, 0, 0, 0]

    def test_xor_states_unequal_lengths(self):
        """Verify XOR raises ValueError for unequal state lengths."""
        with pytest.raises(ValueError, match="equal lengths"):
            xor_states([1, 0], [1, 0, 1])


class TestMatrixUtilities:
    """Tests for states_to_matrix and matrix_to_states."""

    def test_states_to_matrix_valid(self):
        """Verify converting list of states into a 2D matrix."""
        states = [[1, 0, 1], (0, 1, 0), "111"]
        expected = [[1, 0, 1], [0, 1, 0], [1, 1, 1]]
        matrix = states_to_matrix(states)
        assert matrix == expected
        assert matrix_to_states(states) == expected

    def test_states_to_matrix_invalid(self):
        """Verify errors on empty or non-uniform matrices."""
        with pytest.raises(ValueError, match="cannot be empty"):
            states_to_matrix([])

        # Row length mismatch
        with pytest.raises(ValueError, match="does not match expected width"):
            states_to_matrix([[1, 0, 1], [0, 1]])

        with pytest.raises(TypeError):
            states_to_matrix("invalid")


class TestMiscellaneousUtilities:
    """Tests for chunk_state, flatten_states, pad_state, and trim_state."""

    def test_chunk_state(self):
        """Verify splitting state into fixed-size chunks."""
        assert chunk_state([1, 0, 1, 1, 0], size=2) == [[1, 0], [1, 1], [0]]
        # Chunk size larger than state
        assert chunk_state([1, 0, 1], size=10) == [[1, 0, 1]]

    def test_chunk_state_invalid_size(self):
        """Verify invalid chunk size raises ValueError or TypeError."""
        with pytest.raises(ValueError, match="Chunk size must be >="):
            chunk_state([1, 0, 1], size=0)
        with pytest.raises(ValueError, match="Chunk size must be >="):
            chunk_state([1, 0, 1], size=-2)
        with pytest.raises(TypeError):
            chunk_state([1, 0, 1], size=1.5)

    def test_flatten_states(self):
        """Verify flattening nested state lists."""
        assert flatten_states([[1, 0], [1, 1], [0]]) == [1, 0, 1, 1, 0]
        assert flatten_states([]) == []

    def test_flatten_states_invalid_type(self):
        """Verify non-list/tuple input to flatten_states raises TypeError."""
        with pytest.raises(TypeError, match="Expected a list/tuple of states"):
            flatten_states("invalid")
        with pytest.raises(TypeError, match="Expected a list/tuple of states"):
            flatten_states(123)

    def test_pad_state(self):
        """Verify state padding."""
        assert pad_state([1, 0], length=4, value=0) == [1, 0, 0, 0]
        assert pad_state([1, 0], length=4, value=1) == [1, 0, 1, 1]
        # Target length already satisfied
        assert pad_state([1, 0, 1, 1], length=3, value=0) == [1, 0, 1, 1]

    def test_trim_state(self):
        """Verify state trimming."""
        assert trim_state([1, 0, 1, 1, 0], length=3) == [1, 0, 1]
        # Trim to current length returns copy
        assert trim_state([1, 0, 1], length=3) == [1, 0, 1]

    def test_trim_state_exceeding_length(self):
        """Verify trim raises ValueError if target length exceeds current length."""
        with pytest.raises(ValueError, match="exceeds current state length"):
            trim_state([1, 0, 1], length=5)

    def test_package_exports(self):
        """Verify utility functions can be imported directly from package root crypto.ca."""
        assert hasattr(ca, "state_from_string")
        assert hasattr(ca, "random_state")
        assert hasattr(ca, "hamming_distance")
        assert ca.state_from_string("101") == [1, 0, 1]
