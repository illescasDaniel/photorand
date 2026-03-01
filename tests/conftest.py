from pathlib import Path

import numpy as np
import pytest


# Provide absolute path to the realistic test image
@pytest.fixture
def example_image_path() -> str:
	base_dir = Path(__file__).resolve().parent
	return str(base_dir / "data" / "DSC02111.ARW")

@pytest.fixture
def mock_image_data() -> np.ndarray:
	"""Returns a fake 100x100 grid of sequential integers representing pixels."""
	return np.arange(10000).reshape((100, 100)).astype(np.uint16)

@pytest.fixture
def mock_entropy_bytes() -> bytes:
	"""Returns exactly 32 bytes of deterministic pseudorandom data."""
	return bytes(range(32))
