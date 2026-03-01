from ..logger import setup_logger
from .extract import handle_extract
from .generate import handle_generate
from .parser import create_parser


def main():
	"""Main entry point for the photorand CLI."""
	parser, extract_parser, generate_parser = create_parser()

	args = parser.parse_args()
	setup_logger(args.verbose)

	if args.command == "extract":
		handle_extract(args, extract_parser)
	elif args.command == "generate":
		handle_generate(args, generate_parser)


if __name__ == "__main__":
	main()
