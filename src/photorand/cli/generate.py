import argparse
import sys

from ..high_level.engine import PhotoRandEngine
from ..logger import logger


def handle_generate(args: argparse.Namespace, parser: argparse.ArgumentParser):
	"""Handle the 'generate' subcommand: expand a TRNG seed via ChaCha20."""
	# Validate range arguments
	if args.type == "range":
		if args.min is None or args.max is None:
			parser.error("--min and --max are required when --type is 'range'")

	try:
		engine = PhotoRandEngine(args.image_path, salt=not args.deterministic)
	except (FileNotFoundError, IsADirectoryError) as e:
		logger.error(str(e))
		sys.exit(1)
	except Exception as e:
		logger.error(f"Error during CSPRNG generation: {e}")
		sys.exit(1)

	# --- Real output formatting logic ---
	logger.info(f"[generate] type={args.type}, count={args.count}, length={args.length}")

	results: list[str] = []

	if args.type == "bytes":
		results = [
			engine.next_bytes(args.length if args.length else 32).hex()
			for _ in range(args.count)
		]

	elif args.type == "int":
		results = [
			str(engine.next_int(args.length if args.length else 8))
			for _ in range(args.count)
		]

	elif args.type == "string":
		results = [
			engine.next_string(args.length if args.length else 16, args.charset)
			for _ in range(args.count)
		]

	elif args.type == "range":
		results = [
			str(engine.next_int_range(args.min, args.max)) for _ in range(args.count)
		]

	output = "\n".join(results)

	if args.out:
		with open(args.out, "w") as f:
			f.write(output + "\n")
		logger.info(f"[generate] Output written to {args.out}")
	else:
		print(output)
