import hashlib

from ..logger import logger


def hash_entropy_pool(entropy_pool: bytes) -> bytes:
	"""
	Takes a raw byte stream of physical entropy and compresses it
	into 64 uniformly distributed bytes using SHA3-512.

	Args:
		entropy_pool (bytes): The raw entropy byte stream produced by the sampler.

	Returns:
		bytes: A 64-byte (512-bit) SHA3-512 digest of the input entropy.
	"""
	logger.info("[hash] Compressing entropy pool with SHA3-512...")

	# Run the blender directly on the NumPy byte dump
	secure_bytes = hashlib.sha3_512(entropy_pool).digest()

	logger.info(f"[hash] Generated {len(secure_bytes)} bytes of secure entropy.")
	return secure_bytes