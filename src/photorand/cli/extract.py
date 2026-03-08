import argparse
import sys

from ..high_level.seed import PhotoRandSeed
from ..logger import logger


def handle_extract(args: argparse.Namespace, parser: argparse.ArgumentParser):
	"""Handle the 'extract' subcommand: extract 64 bytes of true physical entropy."""

	try:
		seed = PhotoRandSeed(args.image_path)
	except (FileNotFoundError, IsADirectoryError) as e:
		logger.error(str(e))
		sys.exit(1)
	except Exception as e:
		logger.error(f"Error extracting entropy: {e}")
		sys.exit(1)

	# Format the result using high-level methods
	if args.format == "hex":
		result = seed.to_hex_string()
	elif args.format == "int":
		result = seed.to_int()
	elif args.format == "int-range":
		result = seed.to_int_range(args.min, args.max)
	elif args.format == "float-range":
		result = seed.to_float_range(args.min, args.max)
	elif args.format == "bool":
		result = seed.to_bool()
	elif args.format == "float":
		result = seed.to_float()
	else:
		raise ValueError(f"Unknown format: {args.format}")

	# Write to file or stdout
	if args.out:
		if args.binary:
			with open(args.out, "wb") as f:
				f.write(seed.to_bytes())
		else:
			with open(args.out, "w") as f:
				f.write(str(result) + "\n")
	else:
		print(result)
