import logging


# Central logger for the photorand package.
# Level is NOTSET so that pytest's log_cli_level can control captured records.
# The StreamHandler enforces WARNING by default so the CLI stays quiet,
# unless setup_logger() is called with verbose=True.
logger = logging.getLogger("photorand")

# Console handler (used by the CLI)
_ch = logging.StreamHandler()
_ch.setLevel(logging.WARNING)
_ch.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger.addHandler(_ch)


def setup_logger(verbose: bool):
	"""
	Configures the central logger for CLI use.

	Args:
		verbose (bool): When True, lowers the log level to INFO so that
			progress messages are printed to the console.
	"""
	if verbose:
		logger.setLevel(logging.INFO)
		_ch.setLevel(logging.INFO)
