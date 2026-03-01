import numpy as np

from ..logger import logger


def sample_entropy_grid(raw_sensor_data: np.ndarray, grid_spacing: int = 64) -> bytes:
	"""
	Extracts a deterministic grid of pixels, isolates the noisy
	Least Significant Bits, and dumps them to a byte stream.

	Args:
		raw_sensor_data (np.ndarray): The 2D array from ingest_fn.
		grid_spacing (int): The stride/step size. 64 means we grab
							1 pixel out of every 64x64 block.

	Returns:
		bytes: A 1D list of bytes representing the entropy pool.
	"""
	# 1. Slice the grid (Excellent for reducing spatial correlation)
	sampled_matrix = raw_sensor_data[::grid_spacing, ::grid_spacing]

	# 2. Isolate the bottom 4 bits using a Bitwise AND mask (0x0F is 00001111 in binary)
	# This turns a pixel value like 14,253 into just its bottom 4 noisy bits.
	lsb_matrix = sampled_matrix & 0x0F

	# 3. Cast to an 8-bit unsigned integer.
	# Since our max value is now 15, we don't need 16-bit memory slots.
	compact_matrix = lsb_matrix.astype(np.uint8)

	# 4. Flatten and dump straight to bytes
	entropy_bytes = compact_matrix.flatten().tobytes()

	logger.info(f"[sample] Sampled grid at {grid_spacing}px spacing, harvested {len(entropy_bytes)} bytes of dense entropy.")

	return entropy_bytes