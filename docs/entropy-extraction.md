# The `photorand` Mechanism: Physical Entropy Extraction

This document outlines the scientific and technical architecture of `photorand`. It details how the system leverages raw camera sensor data to extract physical entropy, functioning as a True Random Number Generator (TRNG).

## Overview

The photorand extracts physical entropy from raw camera sensor data. Unlike typical pseudo-random number generators (PRNGs) that rely on mathematical algorithms starting from a seed, this photorand leverages the inherent physical noise present in digital image sensors.

## Entropy Source: Raw Sensor Noise

Digital image sensors (CMOS/CCD) are subject to various forms of physical noise, even when no light is present or when capturing a static scene. Key sources of this noise include:

*   **Shot Noise**: Random fluctuations in the number of photons hitting the sensor.
*   **Read Noise**: Electronic noise introduced during the digitization of the analog signal.
*   **Thermal Noise (Dark Current)**: Noise caused by the thermal agitation of electrons within the sensor.

By reading the **RAW** data (before any processing like denoising, demosaicing, or compression), we can isolate these tiny, unpredictable fluctuations.

## Implementation Details

### 1. Data Ingestion (`low_level/ingest.py`)
We use the `rawpy` library to access the unprocessed sensor grid. This ensures we are working with the "pure" values captured by the hardware, which contain the most entropy.

### 2. Sampling and Isolation (`low_level/sample.py`)
To extract the most random components and reduce spatial correlation (where neighboring pixels might share similar noise characteristics), we perform two steps:

*   **Grid Sampling**: We sample pixels at a fixed stride (e.g., every 64th pixel). This spreads the sampling across the entire sensor surface.
*   **LSB Extraction**: We isolate the 4 **Least Significant Bits (LSBs)** of each sampled pixel value. The higher-order bits represent the actual image content (which is predictable), while the LSBs are dominated by the physical noise floor.

### 3. Entropy Conditioning (`low_level/hash.py`)
The raw "lsb-pool" extracted from the sensor might still have small statistical biases. To produce a perfectly uniform output, we pass the extracted bytes through a **cryptographic hash function**.

*   **Algorithm**: SHA3-512
*   **Purpose**: SHA3-512 acts as an "entropy blender." It compresses the large pool of harvested noise into a 64-byte (512-bit) digest. The avalanche effect of the hash ensures that any small amount of entropy in the input is distributed uniformly across the entire output block.

## Conclusion

The result is a 64-byte "seed" of true randomness, rooted in the physical reality of the camera sensor's environment. This seed is highly secure and suitable for use in cryptographic applications or as a source for a CSPRNG.
