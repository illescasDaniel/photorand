import hashlib
import os
import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

from ..logger import logger


def generate_chacha20_encryptor(raw_seed: bytes, salt: bool = True):
	"""
	Initializes a ChaCha20 encryptor from a raw seed, optionally applying environmental salting.
	"""
	if salt:
		# Salting Logic: [Camera Seed] + [Time] + [PID]
		timestamp = str(time.time_ns()).encode()
		pid = str(os.getpid()).encode()
		combined = raw_seed + timestamp + pid
		session_hash = hashlib.sha3_512(combined).digest()
		logger.info("[csprng] CSPRNG initialized with salted session key.")
	else:
		# Deterministic Mode: Use the raw 64-byte seed directly
		if len(raw_seed) < 48:
			raise ValueError("ChaCha20 requires at least 48 bytes of seed (32 key, 16 nonce).")
		session_hash = raw_seed
		logger.info("[csprng] CSPRNG initialized in deterministic mode.")

	key = session_hash[:32]
	nonce = session_hash[32:48]

	algorithm = algorithms.ChaCha20(key, nonce)
	cipher = Cipher(algorithm, mode=None, backend=default_backend())
	return cipher.encryptor()

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
	encryptor = generate_chacha20_encryptor(trng_seed, salt=False)

	# 4. Generate the keystream (Encrypting Zeros)
	# We create a dummy payload of null bytes (0x00) matching the length we need.
	null_payload = b'\x00' * num_bytes_needed

	logger.info(f"[csprng] Expanding physical seed into {num_bytes_needed} bytes...")

	# Passing the zeros through the cipher extracts the pure random keystream
	csprng_stream = encryptor.update(null_payload)

	logger.info("[csprng] Expansion complete.")
	return csprng_stream