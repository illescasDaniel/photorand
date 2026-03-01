import time
from pathlib import Path

from photorand.high_level.engine import PhotoRandEngine
from photorand.high_level.seed import PhotoRandSeed


# Determine the path to the test data
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TEST_IMAGE = str(DATA_DIR / "DSC02111.ARW")


class TestPhotoRandEngine:
	"""Tests for the PhotoRandEngine (CSPRNG) class."""

	def test_init_with_path(self):
		"""Verify initialization directly from an image path string."""
		engine = PhotoRandEngine(TEST_IMAGE)
		assert isinstance(engine.seed, PhotoRandSeed)
		assert len(engine.seed.to_bytes()) == 64

	def test_init_with_seed_object(self):
		"""Verify initialization from an existing PhotoRandSeed object."""
		seed = PhotoRandSeed(TEST_IMAGE)
		engine = PhotoRandEngine(seed)
		assert engine.seed is seed

	def test_salting_uniqueness(self):
		"""
		Verify that two engines initialized with the SAME seed produce DIFFERENT streams.
		This confirms the salting logic (Time + PID) is working.
		"""
		seed = PhotoRandSeed(TEST_IMAGE)
		engine1 = PhotoRandEngine(seed)

		# Ensure a tiny time difference if the resolution is coarse
		time.sleep(0.001)
		engine2 = PhotoRandEngine(seed)

		bytes1 = engine1.next_bytes(32)
		bytes2 = engine2.next_bytes(32)

		assert bytes1 != bytes2, "Engines with same seed must produce unique streams due to salting."

	def test_next_bytes(self):
		"""Verify raw byte generation."""
		engine = PhotoRandEngine(TEST_IMAGE)
		b = engine.next_bytes(10)
		assert len(b) == 10
		assert isinstance(b, bytes)

	def test_next_int(self):
		"""Verify integer generation with specific byte lengths."""
		engine = PhotoRandEngine(TEST_IMAGE)

		# 4-byte int (32-bit)
		val = engine.next_int(length=4)
		assert 0 <= val < (1 << 32)

		# 8-byte int (64-bit)
		val64 = engine.next_int(length=8)
		assert 0 <= val64 < (1 << 64)

	def test_next_int_range(self):
		"""Verify range-bounded integer generation with rejection sampling."""
		engine = PhotoRandEngine(TEST_IMAGE)

		# Small range
		for _ in range(50):
			val = engine.next_int_range(1, 6)
			assert 1 <= val <= 6

		# Large range spanning multiple bytes
		large_val = engine.next_int_range(10**12, 10**13)
		assert 10**12 <= large_val <= 10**13

	def test_next_string(self):
		"""Verify random string generation with various charsets."""
		engine = PhotoRandEngine(TEST_IMAGE)

		# Numeric
		s_num = engine.next_string(length=12, charset='numeric')
		assert len(s_num) == 12
		assert s_num.isdigit()

		# Hex
		s_hex = engine.next_string(length=16, charset='hex')
		assert len(s_hex) == 16
		assert all(c in "0123456789abcdef" for c in s_hex)

		# Alphanumeric
		s_alpha = engine.next_string(length=20, charset='alphanumeric')
		assert len(s_alpha) == 20
		assert s_alpha.isalnum()

		# Custom charset
		custom = "ABC"
		s_custom = engine.next_string(length=50, charset=custom)
		assert all(c in custom for c in s_custom)

	def test_next_bool(self):
		"""Verify boolean generation."""
		engine = PhotoRandEngine(TEST_IMAGE)
		# Probability of 100 same booleans in a row is 2^-100
		results = set(engine.next_bool() for _ in range(100))
		assert {True, False} == results

	def test_generate_batch(self):
		"""Verify the batch helper method."""
		engine = PhotoRandEngine(TEST_IMAGE)

		# Batch of strings
		batch = engine.generate_batch(engine.next_string, 10, length=5, charset='hex')
		assert len(batch) == 10
		assert all(len(s) == 5 for s in batch)

		# Batch of integers in range
		batch_ints = engine.generate_batch(engine.next_int_range, 20, min_val=0, max_val=1)
		assert len(batch_ints) == 20
		assert all(x in [0, 1] for x in batch_ints)
