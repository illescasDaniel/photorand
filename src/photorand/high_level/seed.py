from ..logger import logger
from ..low_level.hash import hash_entropy_pool
from ..low_level.ingest import ingest_raw_image
from ..low_level.sample import sample_entropy_grid


class PhotoRandSeed:
	"""
	True Random Number Generator (TRNG) interface.

	This class extracts physical entropy (photon and thermal noise) from a RAW image file
	to create a pure, unbiased 64-byte seed. It serves as the primary source of true
	entropy for cryptographic operations.
	"""

	def __init__(self, image_path: str):
		"""
		Initialize the TRNG by ingesting a RAW image and extracting entropy.

		Args:
			image_path (str): Path to the RAW image file.
		"""
		logger.info(f"[PhotoRandSeed] Extracting TRNG entropy from: {image_path}")

		# Reuse existing lower-level functions
		raw_data = ingest_raw_image(image_path)
		entropy_pool = sample_entropy_grid(raw_data)
		self._raw_seed = hash_entropy_pool(entropy_pool)

		logger.info("[PhotoRandSeed] Successfully generated 64-byte seed.")

	def to_bytes(self) -> bytes:
		"""
		Returns the pure 64-byte seed.

		Returns:
			bytes: The 64-byte TRNG seed.
		"""
		return self._raw_seed

	def to_hex_string(self) -> str:
		"""
		Returns the seed as a hex string.

		Returns:
			str: 128-character hex representation of the seed.
		"""
		return self._raw_seed.hex()

	def to_int(self) -> int:
		"""
		Converts the 64 bytes into a massive integer.

		Returns:
			int: The seed as a large integer.
		"""
		return int.from_bytes(self._raw_seed, byteorder="big")

	def to_int_range(self, min_val: int, max_val: int) -> int:
		"""
		Safely bounds the TRNG entropy using rejection sampling.

		Because this is a pure TRNG with a strict 64-byte (512-bit) entropy limit,
		it cannot "redraw" a number if the initial sample falls into the modulo
		rejection zone. To preserve absolute cryptographic purity, no pseudo-random
		fallbacks are used. Instead, in the astronomically unlikely event of a
		rejection, a RuntimeError is raised.

		The mathematical hard limit for absolute fairness is calculated as:
		Limit = 2^512 - (2^512 mod range_size)

		(Note: 2^512 is approximately 1.34 x 10^154. Rejection only occurs if
		the sampled integer falls within the final incomplete modulo remainder).

		Args:
			min_val (int): The lower bound (inclusive).
			max_val (int): The upper bound (inclusive).

		Returns:
			int: A uniformly distributed random integer within [min_val, max_val].

		Raises:
			ValueError: If max_val is less than min_val.
			RuntimeError: If the physical entropy falls into the rejection zone.
		"""
		range_size = max_val - min_val + 1
		if range_size <= 0:
			raise ValueError("max_val must be greater than or equal to min_val")

		large_int = self.to_int()

		# Calculate the mathematical boundary for a perfectly uniform distribution
		limit = (1 << 512) - ((1 << 512) % range_size)

		if large_int < limit:
			return min_val + (large_int % range_size)
		raise RuntimeError(
			f"TRNG Exhaustion: The physical entropy from the image fell into the "
			f"rejection zone (value >= {limit}). To maintain strict TRNG purity, "
			f"no PRNG fallback was used. Please extract a seed from a new image."
		)

	def to_bool(self) -> bool:
		"""
		Converts the exact pure TRNG seed into a single boolean value.

		Returns:
			bool: True or False.
		"""
		return (self._raw_seed[0] & 1) == 1

	def to_float(self) -> float:
		"""
		Converts the TRNG seed into a floating point number between 0.0 and 1.0 (inclusive).

		Returns:
			float: Random float in [0.0, 1.0].
		"""
		# Use 53 bits for standard IEEE 754 double precision float
		val = int.from_bytes(self._raw_seed[:7], byteorder="big") & 0x1FFFFFFFFFFFFF
		return val / 0x1FFFFFFFFFFFFF
