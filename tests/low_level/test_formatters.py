import pytest

from photorand.low_level.formatters import (
	csprng_format_bool,
	csprng_format_float,
	trng_format_bool,
	trng_format_float,
	trng_format_hex,
	trng_format_int,
	trng_format_range,
)


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


def test_format_bool():
	assert trng_format_bool(b"\x00") is False
	assert trng_format_bool(b"\x01") is True
	assert trng_format_bool(b"\x02") is False


def test_format_float():
	# 7 bytes of \x00 -> 0.0
	assert trng_format_float(b"\x00" * 7) == 0.0
	# Max 53 bits -> \x1f\xff\xff\xff\xff\xff\xff -> 1.0
	assert trng_format_float(b"\x1f" + b"\xff" * 6) == 1.0


def test_csprng_format_bool():
	res = csprng_format_bool(b"\x00\x01\x02", 3)
	assert res == ["False", "True", "False"]


def test_csprng_format_float():
	stream = (b"\x00" * 7) + (b"\xff" * 7)
	res = csprng_format_float(stream, 2)
	assert res == ["0.0", "1.0"]
