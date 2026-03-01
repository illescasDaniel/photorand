# photorand

[![PyPI version](https://img.shields.io/pypi/v/photorand)](https://pypi.org/project/photorand/)


A True Random Number Generator (TRNG) using raw camera sensor data to extract physical entropy.

![Architecture](https://res.cloudinary.com/dhnsmw569/image/upload/photorand_dtj6xn.webp)

## Project Structure

- `src/photorand/` - Main package source code.
	- `low_level/` - Modular primitives (ingest, sample, hash, csprng).
	- `high_level/` - Clean OO abstractions (`PhotoRandSeed`, `PhotoRandEngine`).
	- `cli/` - Command-line interface logic.
- `docs/` - Technical and scientific documentation detailing the [entropy extraction](docs/entropy-extraction.md) and [entropy expansion](docs/entropy-expansion.md) mechanisms.
- `tests/` - Comprehensive test suite organized by architectural layer.
- `examples/` - Code samples, useful scripts

## Installation

This project is available on PyPI:

```bash
pip install photorand
```

### From Source (Development)

This project uses `pyproject.toml` for managing dependencies.

1. **Create and activate a virtual environment** (recommended):
	```bash
	python -m venv .venv
	source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
	```

2. **Install the project in editable mode**:
	```bash
	pip install -e .
	# or this one for also installing the dev tools
	pip install -e ".[dev]"
	```

Note: you can use `photorand` from the cli using `python -m photorand` instead of just `photorand`

---

### 1. High-Level Classes (Recommended)

The high-level classes provide a stateful and convenient interface for both TRNG and CSPRNG operations.

#### `PhotoRandSeed` (TRNG)
Encapsulates the process of extracting entropy from a RAW image. It is perfect for generating one-off secure seeds, keys, or dice rolls directly from physical noise.

```python
from photorand import PhotoRandSeed

# 1. Extract entropy from a RAW image
seed = PhotoRandSeed("path/to/image.raw")

# 2. Access as bytes, hex, or large integer
print(seed.to_hex_string())
print(seed.to_int())

# 3. Roll a D100 using physical entropy (Rejection Sampling)
luck = seed.to_int_range(1, 100)
```

#### `PhotoRandEngine` (CSPRNG)
An infinite stream generator powered by ChaCha20, seeded by a `PhotoRandSeed`. It handles salting (Time + PID) automatically to ensure that even consecutive runs with the same image produce unique streams.

```python
from photorand import PhotoRandEngine

# 1. Initialize from image or existing Seed object
engine = PhotoRandEngine("path/to/image.raw")

# 2. Pull arbitrary amounts of secure data
key = engine.next_bytes(32)
pin = engine.next_string(length=6, charset='numeric')
dice = engine.next_int_range(1, 20)

# 3. Batch generation
multiple_passwords = engine.generate_batch(engine.next_string, count=5, length=16)
```

#### CLI (Command Line Interface)

The package includes a powerful CLI to use these classes directly from your terminal.

```bash
# Extract 64-byte photorand seed (hex)
photorand extract path/to/raw_image.ARW

# Roll a D20
photorand extract path/to/raw_image.ARW --format range --min 1 --max 20

# Generate 5 random 16-char alphanumeric passwords
photorand generate path/to/raw_image.ARW --type string -n 5 -l 16 --charset alpha
```

*For more details, run:* `photorand --help`

---

### 2. Low-Level Modular Functions

For maximum control or research, you can use the modular primitives directly.

```python
from photorand.low_level import ingest_raw_image
from photorand.low_level import sample_entropy_grid
from photorand.low_level import hash_entropy_pool

# 1. Ingest raw sensor data
raw_data = ingest_raw_image("path/to/image.raw")

# 2. Extract raw LSB bits
entropy_pool = sample_entropy_grid(raw_data)

# 3. Condition entropy into uniform bytes
seed_bytes = hash_entropy_pool(entropy_pool)
```

Alternatively, use the functional pipeline. It accepts custom functions for each part of the algorithm (ingest_fn, sample_fn and hash_fn) although we already provide the values as default parameters:
```python
from photorand.low_level import generate_true_random_number
seed = generate_true_random_number("path/to/image.raw")
```

---

## Development

### Running the Tests
```bash
python -m pytest -v --log-cli-level=INFO
# or just this one to skip logs
pytest
```

### Formatting
```bash
ruff check --fix src tests examples
```

## Resources

- **Blog Post**: [Physical Entropy with PhotoRand](https://www.daniel-ir.eu/blog/photorand)
- **PyPI Package**: [photorand on PyPI](https://pypi.org/project/photorand/)
