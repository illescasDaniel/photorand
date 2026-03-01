# The CSPRNG Mechanism: Entropy Expansion

This document explains how the physical seed generated via [`photorand`'s extraction process](entropy-extraction.md) is expanded into a continuous, high-volume stream of cryptographically secure random data.

## The Need for Expansion

While direct physical extraction produces high-quality true randomness, harvesting large volumes (megabytes or gigabytes) directly from a camera sensor is slow and computationally expensive.

To solve this, we use a **CSPRNG** (Cryptographically Secure Pseudo-Random Number Generator). The CSPRNG takes a small, high-entropy "seed" from the photorand and expands it into an effectively infinite stream of bytes that is computationally indistinguishable from true randomness.

## The Expansion Engine: ChaCha20

This project uses the **ChaCha20** stream cipher as its expansion core.

### Why ChaCha20?
*   **Security**: ChaCha20 is a modern, high-security cipher designed by Daniel J. Bernstein. It is widely used in protocols like TLS 1.3 and SSH.
*   **Performance**: It is exceptionally fast in software implementations and does not require specialized hardware acceleration (like AES-NI) to be efficient.
*   **No State Leakage**: Unlike some older PRNGs, a CSPRNG based on a modern stream cipher ensures that even if part of the output is compromised, it is computationally impossible to determine past or future outputs.

## Implementation Details (`low_level/csprng.py`)

1.  **Seeding**: The 64-byte output from the photorand is used to initialize the cipher.
    *   The first **32 bytes** (256 bits) are used as the **Key**.
    *   The next **16 bytes** (128 bits) are used as the **Nonce** (Initialization Vector).
2.  **Keystream Generation**: To generate random bytes, we encrypt a stream of null bytes (`0x00`).
3.  **Result**: The resulting "encrypted" output is a pure keystream of cryptographically secure pseudo-random bytes.

## Usage in the CLI

When you run the `generate` command:
```bash
python -m photorand generate <image_path> [options]
```
The tool first runs the photorand process to get a fresh 64-byte seed and then uses this seed to drive the ChaCha20 expander to provide as much data as requested.

## Security Properties

*   **Prediction Resistance**: Given any amount of output from the generator, an adversary with unlimited time but limited classical computing power cannot predict the next bit better than a coin flip (50/50).
*   **Backtracking Resistance**: If the internal state of the generator is compromised at a certain point, previous outputs remain secure.
