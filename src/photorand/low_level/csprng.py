from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

from ..logger import logger


def expand_entropy_chacha20(trng_seed: bytes, num_bytes_needed: int) -> bytes:
	"""
	Takes a 64-byte photorand seed and uses it to key a ChaCha20 stream cipher,
	generating an arbitrary amount of Cryptographically Secure Pseudo-Random numbers.

	Args:
		trng_seed (bytes): The 64-byte true random output from your hash function.
		num_bytes_needed (int): How many random bytes you want to generate.

	Returns:
		bytes: A highly secure, mathematically random byte string.
	"""
	# 1. Validate the input
	if len(trng_seed) < 48:
		raise ValueError("ChaCha20 requires at least 48 bytes of seed (32 key, 16 nonce).")

	# 2. Split the 64-byte TRNG seed
	# ChaCha20 strictly requires a 256-bit (32-byte) key and a 128-bit (16-byte) nonce.
	# Because your TRNG generated 64 bytes, we have more than enough pure entropy!
	key = trng_seed[:32]
	nonce = trng_seed[32:48]
	# (The remaining 16 bytes of your 64-byte seed are safely ignored/discarded)

	logger.info("[csprng] Initializing ChaCha20 with TRNG Key and Nonce...")

	# 3. Initialize the Cipher
	algorithm = algorithms.ChaCha20(key, nonce)
	cipher = Cipher(algorithm, mode=None, backend=default_backend())
	encryptor = cipher.encryptor()

	# 4. Generate the keystream (Encrypting Zeros)
	# We create a dummy payload of null bytes (0x00) matching the length we need.
	null_payload = b'\x00' * num_bytes_needed

	logger.info(f"[csprng] Expanding physical seed into {num_bytes_needed} bytes...")

	# Passing the zeros through the cipher extracts the pure random keystream
	csprng_stream = encryptor.update(null_payload)

	logger.info("[csprng] Expansion complete.")
	return csprng_stream