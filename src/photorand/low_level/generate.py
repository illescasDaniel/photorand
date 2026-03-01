from typing import Callable

import numpy as np

from .hash import hash_entropy_pool
from .ingest import ingest_raw_image
from .sample import sample_entropy_grid


def generate_true_random_number(
	image_path: str,
	ingest_fn: Callable[[str], np.ndarray] = ingest_raw_image,
	sample_fn: Callable[[np.ndarray], bytes] = sample_entropy_grid,
	hash_fn: Callable[[bytes], bytes] = hash_entropy_pool,
) -> bytes:
	"""
	The master pipeline. Extracts physical entropy and returns pure, raw bytes.

	Args:
		image_path (str): Path to the RAW image file used as the entropy source.
		ingest_fn (Callable[[str], np.ndarray]): Function that reads the RAW file and
			returns a 2D array of raw sensor values. Defaults to ingest_raw_image.
		sample_fn (Callable[[np.ndarray], bytes]): Function that samples the sensor
			array and returns a byte stream of raw entropy. Defaults to sample_entropy_grid.
		hash_fn (Callable[[bytes], bytes]): Function that hashes the entropy pool
			into a fixed-length, uniformly distributed byte string. Defaults to hash_entropy_pool.

	Returns:
		bytes: A fixed-length byte string of cryptographically secure entropy.
	"""
	raw_image_data = ingest_fn(image_path)
	entropy_pool = sample_fn(raw_image_data)
	secure_hash_bytes = hash_fn(entropy_pool)

	return secure_hash_bytes
