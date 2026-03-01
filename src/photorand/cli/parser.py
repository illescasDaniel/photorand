import argparse
from typing import Tuple


def create_parser() -> Tuple[argparse.ArgumentParser, argparse.ArgumentParser, argparse.ArgumentParser]:
	"""Create and return the ArgumentParser for the photorand CLI."""
	parser = argparse.ArgumentParser(
		description="photorand: True Random & Cryptographically Secure number generation from RAW images.",
	)

	subparsers = parser.add_subparsers(dest="command", required=True)

	# ------------------------------------------------------------------
	# 'extract' subcommand
	# ------------------------------------------------------------------
	extract_parser = subparsers.add_parser(
		"extract",
		help="Extract 64 bytes of true physical entropy from a RAW image.",
	)
	extract_parser.add_argument(
		"image_path",
		help="Path to the RAW image file (e.g., .ARW, .CR2).",
	)
	extract_parser.add_argument(
		"--format",
		choices=["hex", "int", "range"],
		default="hex",
		help="Output format: hex (default), int, or range.",
	)
	extract_parser.add_argument(
		"--min",
		type=int,
		help="Lower bound (required when --format is 'range').",
	)
	extract_parser.add_argument(
		"--max",
		type=int,
		help="Upper bound (required when --format is 'range').",
	)
	extract_parser.add_argument(
		"--out",
		help="File path to save output. Omit to print to stdout.",
	)
	extract_parser.add_argument(
		"--binary",
		action="store_true",
		help="Write raw binary bytes when saving to a file (requires --out).",
	)
	extract_parser.add_argument(
		"-v", "--verbose",
		action="store_true",
		help="Enable verbose logging.",
	)

	# ------------------------------------------------------------------
	# 'generate' subcommand
	# ------------------------------------------------------------------
	generate_parser = subparsers.add_parser(
		"generate",
		help="Generate arbitrary amounts of CSPRNG data seeded by a RAW image.",
	)
	generate_parser.add_argument(
		"image_path",
		help="Path to the RAW image file (e.g., .ARW, .CR2).",
	)
	generate_parser.add_argument(
		"--type",
		choices=["bytes", "int", "string", "range"],
		required=True,
		help="Type of data to generate.",
	)
	generate_parser.add_argument(
		"-n", "--count",
		type=int,
		default=1,
		help="Number of items to generate (default: 1).",
	)
	generate_parser.add_argument(
		"-l", "--length",
		type=int,
		help="Size of each item (bytes, digits, or characters depending on --type).",
	)
	generate_parser.add_argument(
		"--min",
		type=int,
		help="Lower bound (required when --type is 'range').",
	)
	generate_parser.add_argument(
		"--max",
		type=int,
		help="Upper bound (required when --type is 'range').",
	)
	generate_parser.add_argument(
		"--charset",
		choices=["ascii", "hex", "alpha", "all"],
		default="all",
		help="Character set to use when --type is 'string' (default: all).",
	)
	generate_parser.add_argument(
		"-o", "--out",
		help="File path to save output. Omit to print to stdout.",
	)
	generate_parser.add_argument(
		"--deterministic",
		action="store_true",
		help="Produce a reproducible sequence by skipping environmental salting.",
	)
	generate_parser.add_argument(
		"-v", "--verbose",
		action="store_true",
		help="Enable verbose logging.",
	)

	return parser, extract_parser, generate_parser
