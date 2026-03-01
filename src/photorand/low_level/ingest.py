import os

import numpy as np
import rawpy

from ..logger import logger


def ingest_raw_image(image_path: str) -> np.ndarray:
	"""
	Reads a RAW image file and extracts the unprocessed, pure sensor data.
	Supports .ARW, .CR2, .NEF, .DNG, and most other RAW formats.

	Args:
		image_path (str): The path to the RAW file.

	Returns:
		np.ndarray: A 2D array representing the raw light values hitting the sensor.
	"""
	logger.info(f"[ingest] Reading raw sensor data from: {image_path}")

	if not os.path.exists(image_path):
		raise FileNotFoundError(f"File not found: {image_path}")
	if not os.path.isfile(image_path):
		raise IsADirectoryError(f"Path is a directory, not a file: {image_path}")

	try:
		# We use a context manager (with) to ensure the file is safely closed after reading
		with rawpy.imread(image_path) as raw:
			# 'raw.raw_image' grabs the 2D array BEFORE any color processing or denoising.
			# We use .copy() so the data persists in memory after the file closes.
			raw_sensor_data = raw.raw_image.copy()
	except Exception as e:
		raise ValueError(f"Not a valid RAW image file or unsupported format: {image_path} ({e})")

	logger.info(f"[ingest] Extracted sensor grid of shape: {raw_sensor_data.shape}")

	return raw_sensor_data