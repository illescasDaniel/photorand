import pytest

from photorand.low_level.formatters import trng_format_hex, trng_format_int, trng_format_range


def test_format_hex():
	entropy = b"\xde\xad\xbe\xef"
	assert trng_format_hex(entropy) == "deadbeef"


def test_format_int():
	# 'big' endian: \x00\x01 -> 1
	entropy = b"\x00\x01"
	assert trng_format_int(entropy) == 1

	# \x01\x00 -> 256
	entropy = b"\x01\x00"
	assert trng_format_int(entropy) == 256


def test_format_range_basic():
	# If entropy is exactly 1 byte equal to 10
	entropy = b"\x0a"
	result = trng_format_range(entropy, 0, 100)
	assert result == 10


def test_format_range_bounds():
	entropy = b"\x14\x15"  # Has enough entropy to be rolled

	with pytest.raises(ValueError):
		trng_format_range(entropy, 10, 5)  # lower > upper

	with pytest.raises(ValueError):
		trng_format_range(entropy, 10, 10)  # lower == upper


def test_format_range_exhaustion():
	# Provide a very restricted amount of entropy where all chunks are above the cutoff
	# Example: range [1, 2], so size = 2, requires 1 byte.
	# Cutoff = 256 - (256 % 2) = 256.
	# Actually for size 2, everything is accepted (256 is divisible by 2).
	#
	# Example 2: range [1, 100], size=100. Cutoff = 256 - 56 = 200.
	# If we provide a single byte >= 200, it should reject and exhaust since no more bytes.
	entropy = b"\xc8"  # 200
	with pytest.raises(RuntimeError):
		trng_format_range(entropy, 1, 100)
