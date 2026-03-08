import string
from typing import Callable, List, Union

from ..low_level.csprng import generate_chacha20_encryptor
from .seed import PhotoRandSeed


class PhotoRandEngine:
	"""
	Cryptographically Secure Pseudo-Random Number Generator (CSPRNG).

	This class uses a PhotoRandSeed as its absolute source of entropy, combined with
	environmental salting (nanosecond timestamp and process ID), to fuel a continuous
	ChaCha20 stream cipher. It provides a stateful stream of secure random values.
	"""

	def __init__(self, source: Union[PhotoRandSeed, str], salt: bool = True):
		"""
		Initialize the CSPRNG using a PhotoRandSeed or an image path.

		Args:
			source (Union[PhotoRandSeed, str]): A PhotoRandSeed object or path to a RAW image.
			salt (bool): When True (default), it appends environmental entropy (timestamp, PID)
				to ensure a unique sequence for every execution. When False, it uses the
				seed exactly as provided for a deterministic, reproducible sequence.
		"""
		if isinstance(source, str):
			self.seed = PhotoRandSeed(source)
		else:
			self.seed = source

		raw_seed = self.seed.to_bytes()


		self._encryptor = generate_chacha20_encryptor(raw_seed, salt=salt)

	def _get_bytes(self, n: int) -> bytes:
		"""
		Pushes n null bytes through the ChaCha20 encryptor and returns the keystream.

		Args:
			n (int): Number of bytes to generate.

		Returns:
			bytes: n secret random bytes.
		"""
		null_payload = b"\x00" * n
		return self._encryptor.update(null_payload)

	def next_bytes(self, length: int) -> bytes:
		"""
		Generates a sequence of n random bytes.

		Args:
			length (int): Number of bytes to generate.

		Returns:
			bytes: Random bytes.
		"""
		return self._get_bytes(length)

	def next_int(self, length: int = 8) -> int:
		"""
		Generates an integer with the specified number of bytes length.

		Args:
			length (int): Number of bytes (not digits) to use for the integer. Defaults to 8 (64 bits).

		Returns:
			int: A random integer.
		"""
		raw_bytes = self._get_bytes(length)
		return int.from_bytes(raw_bytes, byteorder="big")

	def next_int_digits(self, digits: int) -> int:
		"""
		Generates a random integer with exactly the specified number of decimal digits.

		Args:
			digits (int): The number of decimal digits for the generated integer.

		Returns:
			int: A random integer with the specified number of digits.
		"""
		if digits <= 0:
			raise ValueError("digits must be greater than 0")
		min_val = 10 ** (digits - 1) if digits > 1 else 0
		max_val = (10 ** digits) - 1
		return self.next_int_range(min_val, max_val)

	def next_int_range(self, min_val: int, max_val: int) -> int:
		"""
		Generates a random integer within the range [min_val, max_val] (inclusive).

		Args:
			min_val (int): The lower bound of the range.
			max_val (int): The upper bound of the range.

		Returns:
			int: A random integer.
		"""
		range_size = max_val - min_val + 1
		if range_size <= 0:
			raise ValueError("max_val must be greater than or equal to min_val")

		# The exact number of bits needed to represent the range
		num_bits = range_size.bit_length()
		num_bytes = (num_bits + 7) // 8

		while True:
			raw_bytes = self._get_bytes(num_bytes)
			val = int.from_bytes(raw_bytes, byteorder="big")

			# Mask the value to the exact bit length needed
			# e.g., if we need 5 bits, mask with 0b11111 (31)
			val &= (1 << num_bits) - 1

			if val < range_size:
				return min_val + val

	def next_string(self, length: int = 16, charset: str = "all") -> str:
		"""
		Generates a random string using the specified character set.

		Args:
			length (int): Length of the string.
			charset (str): 'all', 'alphanumeric', 'numeric', 'hex', or a custom string of characters.

		Returns:
			str: Random string.
		"""
		if charset == "all":
			chars = string.ascii_letters + string.digits + string.punctuation
		elif charset == "alphanumeric":
			chars = string.ascii_letters + string.digits
		elif charset == "numeric":
			chars = string.digits
		elif charset == "hex":
			chars = "0123456789abcdef"
		else:
			chars = charset

		result = []
		for _ in range(length):
			idx = self.next_int_range(0, len(chars) - 1)
			result.append(chars[idx])
		return "".join(result)

	def next_bool(self) -> bool:
		"""
		Generates a random boolean value.

		Returns:
			bool: True or False.
		"""
		# We can extract 1 bit, or just check if one byte is odd
		return (self._get_bytes(1)[0] & 1) == 1

	def next_float(self) -> float:
		"""
		Generates a random float between 0.0 (inclusive) and 1.0 (exclusive).

		Returns:
			float: A random float in [0.0, 1.0).
		"""
		# Pull 7 bytes (56 bits), shift right by 3 to get exactly 53 bits
		raw_bytes = self._get_bytes(7)
		val = int.from_bytes(raw_bytes, byteorder="big") >> 3

		# Divide by 2^53. This is exact and introduces zero rounding error.
		return val * (2.0 ** -53)

	def next_float_range(self, min_val: float, max_val: float) -> float:
		"""
		Generates a random float within the range [min_val, max_val) (half-open).

		Args:
			min_val (float): The lower bound of the range (inclusive).
			max_val (float): The upper bound of the range (exclusive).

		Returns:
			float: A random float in [min_val, max_val).
		"""
		if max_val < min_val:
			raise ValueError("max_val must be greater than or equal to min_val")

		factor = self.next_float()
		return min_val + (factor * (max_val - min_val))

	def generate_batch(self, type_func: Callable, n: int, **kwargs) -> List:
		"""
		Generates a list of n items using one of the generation methods.

		Args:
			type_func (Callable): The method to call (e.g., self.next_int_range).
			n (int): Number of items to generate.
			**kwargs: Arguments for the type_func.

		Returns:
			List: A list of generated items.
		"""
		return [type_func(**kwargs) for _ in range(n)]
