def trng_format_hex(entropy: bytes) -> str:
	"""
	Converts raw TRNG bytes to a readable hexadecimal string.
	"""
	return entropy.hex()


def trng_format_int(entropy: bytes) -> int:
	"""
	Converts raw TRNG bytes into a single massive integer.
	"""
	return int.from_bytes(entropy, byteorder="big")


def trng_format_range(entropy: bytes, lower_bound: int, upper_bound: int) -> int:
	"""
	Consumes raw entropy bytes and uses mathematical Rejection Sampling
	to return a perfectly unbiased integer within the specified bounds.
	"""
	if lower_bound >= upper_bound:
		raise ValueError("Lower bound must be strictly less than upper bound.")

	range_size = upper_bound - lower_bound + 1
	num_bytes = max(1, ((range_size - 1).bit_length() + 7) // 8)
	max_possible_value = 256**num_bytes
	cutoff = max_possible_value - (max_possible_value % range_size)

	for i in range(0, len(entropy) - num_bytes + 1, num_bytes):
		chunk = entropy[i : i + num_bytes]
		candidate = int.from_bytes(chunk, byteorder="big", signed=False)
		if candidate < cutoff:
			return lower_bound + (candidate % range_size)

	raise RuntimeError(
		"Entropy exhausted! Rejection sampler threw away all chunks. Snap another photo."
	)


def csprng_format_bytes(csprng_stream: bytes, count: int, length: int | None) -> list[str]:
	"""
	Format raw CSPRNG bytes as a list of hex strings.
	"""
	chunk = length if length else 32
	results = []
	for i in range(count):
		block = csprng_stream[i * chunk : (i + 1) * chunk]
		results.append(block.hex())
	return results


def csprng_format_int(csprng_stream: bytes, count: int, length: int | None) -> list[str]:
	"""
	Format raw CSPRNG bytes as a list of decimal integer strings.
	"""
	chunk = length if length else 8
	results = []
	for i in range(count):
		block = csprng_stream[i * chunk : (i + 1) * chunk]
		results.append(str(int.from_bytes(block, "big")))
	return results


def csprng_format_string(
	csprng_stream: bytes, count: int, length: int | None, charset_name: str
) -> list[str]:
	"""
	Format raw CSPRNG bytes as a list of strings using a specific character set.
	"""
	charsets = {
		"ascii": "".join(chr(c) for c in range(32, 127)),
		"hex": "0123456789abcdef",
		"alpha": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
		"all": "".join(chr(c) for c in range(32, 127)),
	}
	charset = charsets.get(charset_name, charsets["all"])
	char_len = length if length else 16
	results = []
	for i in range(count):
		chars = []
		for j in range(char_len):
			byte_idx = i * char_len * 2 + j * 2
			if byte_idx + 1 >= len(csprng_stream):
				break
			val = int.from_bytes(csprng_stream[byte_idx : byte_idx + 2], "big")
			chars.append(charset[val % len(charset)])
		results.append("".join(chars))
	return results


def csprng_format_range(
	csprng_stream: bytes, count: int, min_val: int, max_val: int
) -> list[str]:
	"""
	Format raw CSPRNG bytes as a list of integers within a specific range.
	"""
	chunk = 8
	results = []
	for i in range(count):
		block = csprng_stream[i * chunk : (i + 1) * chunk]
		results.append(str(trng_format_range(block, min_val, max_val)))
	return results


def trng_format_bool(entropy: bytes) -> bool:
	"""
	Converts raw TRNG bytes to a single boolean value.
	"""
	return (entropy[0] & 1) == 1


def trng_format_float(entropy: bytes) -> float:
	"""
	Converts raw TRNG bytes to a floating point number between 0.0 and 1.0 (inclusive).
	"""
	# Use 53 bits for Python float precision
	val = int.from_bytes(entropy[:7], byteorder="big") & 0x1FFFFFFFFFFFFF
	return val / 0x1FFFFFFFFFFFFF


def csprng_format_bool(csprng_stream: bytes, count: int) -> list[str]:
	"""
	Format raw CSPRNG bytes as a list of boolean strings.
	"""
	results = []
	for i in range(count):
		results.append(str((csprng_stream[i] & 1) == 1))
	return results


def csprng_format_float(csprng_stream: bytes, count: int) -> list[str]:
	"""
	Format raw CSPRNG bytes as a list of float strings (0.0 to 1.0 inclusive).
	"""
	chunk = 7
	results = []
	for i in range(count):
		block = csprng_stream[i * chunk : (i + 1) * chunk]
		# Fallback if stream is too short, though it should be sized correctly by engine
		if len(block) < chunk:
			block = block.ljust(chunk, b'\x00')
		val = int.from_bytes(block, "big") & 0x1FFFFFFFFFFFFF
		results.append(str(val / 0x1FFFFFFFFFFFFF))
	return results
