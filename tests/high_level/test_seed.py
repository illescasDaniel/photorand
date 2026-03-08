from pathlib import Path

from photorand.high_level.seed import PhotoRandSeed


# Determine the path to the test data
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TEST_IMAGE = str(DATA_DIR / "DSC02111.ARW")


class TestPhotoRandSeed:
	"""Tests for the PhotoRandSeed (TRNG) class."""

	def test_init_and_to_bytes(self):
		"""Verify that a seed can be initialized from an image and returns 64 bytes."""
		seed = PhotoRandSeed(TEST_IMAGE)
		raw_bytes = seed.to_bytes()
		assert isinstance(raw_bytes, bytes)
		assert len(raw_bytes) == 64

	def test_to_hex_string(self):
		"""Verify hex string representation."""
		seed = PhotoRandSeed(TEST_IMAGE)
		hex_str = seed.to_hex_string()
		assert len(hex_str) == 128
		assert all(c in "0123456789abcdef" for c in hex_str)
		assert hex_str == seed.to_bytes().hex()

	def test_to_int(self):
		"""Verify large integer conversion."""
		seed = PhotoRandSeed(TEST_IMAGE)
		val = seed.to_int()
		assert isinstance(val, int)
		assert val == int.from_bytes(seed.to_bytes(), byteorder='big')

	def test_to_int_range(self):
		"""Verify bounded range extraction from the seed."""
		seed = PhotoRandSeed(TEST_IMAGE)
		# Test multiple ranges
		for _ in range(10):
			val = seed.to_int_range(100, 200)
			assert 100 <= val <= 200

	def test_to_bool(self):
		"""Verify bool generation."""
		seed = PhotoRandSeed(TEST_IMAGE)
		val_bool = seed.to_bool()
		assert isinstance(val_bool, bool)

	def test_to_float(self):
		"""Verify float generation."""
		seed = PhotoRandSeed(TEST_IMAGE)
		val_float = seed.to_float()
		assert isinstance(val_float, float)
		assert 0.0 <= val_float < 1.0

	def test_to_float_range(self):
		"""Verify float range generation."""
		seed = PhotoRandSeed(TEST_IMAGE)
		val_float = seed.to_float_range(10.0, 20.0)
		assert 10.0 <= val_float < 20.0

		# Test negative range
		val_neg = seed.to_float_range(-2.0, -1.0)
		assert -2.0 <= val_neg < -1.0
