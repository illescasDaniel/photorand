import sys
from pathlib import Path

import pytest

from photorand.cli.main import main


# We patch stdout and sys.argv to test the CLI end-to-end with real images
def run_cli_integration(args_list: list[str], capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> str:
	monkeypatch.setattr(sys, 'argv', ['main.py'] + args_list)
	try:
		main()
	except SystemExit:
		pass
	return capsys.readouterr().out.strip()


@pytest.mark.parametrize("image_filename, expected_int, expected_range", [
	("DSC02111.ARW", 5441230399755021634661702627294439837643765743048098986473439861345281873618919255001375917882451696456632001720700828097273286841568547436452202507760768, 20), # noqa: E501
	("IMG_6775.CR2", 1983112000144019161378659574769935184153364571863522866163921903212591155076214460720178892638770579202958750617616524851798091481695319032837458803953969, 20), # noqa: E501
	("DSC03088.ARW", 3295623491421879308436711099041673549102516067157422785057540737909732005548384056302810108111505029508815460346658820938042570895769000942097100592489198, 16), # noqa: E501
	("DSC03089.ARW", 406985617972906688707974285432327461848063680588482669067211356871213446809847124085706365799856761437958785114466726225109296019541509202268552018876523, 16), # noqa: E501
])
def test_extract_integration(image_filename: str, expected_int: int, expected_range: int, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch):
	base_dir = Path(__file__).resolve().parent.parent
	image_file = base_dir / "data" / image_filename

	# Check if the file exists; if not, gracefully skip this specific iteration
	if not image_file.exists():
		pytest.skip(f"Test data file {image_filename} not found. Skipping test.")

	image_path = str(image_file)

	# Test hex format (default)
	out_hex = run_cli_integration(["extract", image_path], capsys, monkeypatch)
	assert len(out_hex) == 128  # 64 bytes * 2 chars/byte

	# Test int format
	out_int = run_cli_integration(["extract", image_path, "--format", "int"], capsys, monkeypatch)
	assert int(out_int) == expected_int

	# Test range format
	out_range = run_cli_integration(["extract", image_path, "--format", "range", "--min", "10", "--max", "20"], capsys, monkeypatch)
	assert int(out_range) == expected_range

	# Test bool format
	out_bool = run_cli_integration(["extract", image_path, "--format", "bool"], capsys, monkeypatch)
	assert out_bool in ["True", "False"]

	# Test float format
	out_float = run_cli_integration(["extract", image_path, "--format", "float"], capsys, monkeypatch)
	f_val = float(out_float)
	assert 0.0 <= f_val <= 1.0


def test_generate_integration(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch):
	"""Test the generate subcommand end-to-end with a real image."""
	base_dir = Path(__file__).resolve().parent.parent
	image_path = str(base_dir / "data" / "DSC02111.ARW")

	# Generate 5 integers
	out = run_cli_integration(["generate", image_path, "--type", "int", "-n", "5"], capsys, monkeypatch)
	lines = out.splitlines()
	assert len(lines) == 5
	for line in lines:
		int(line)  # Valid integer

	# Generate a specific string
	out_str = run_cli_integration(["generate", image_path, "--type", "string", "-n", "1", "-l", "32", "--charset", "hex"], capsys, monkeypatch)
	assert len(out_str) == 32
	assert all(c in "0123456789abcdef" for c in out_str)

	# Generate 3 bools
	out_bools = run_cli_integration(["generate", image_path, "--type", "bool", "-n", "3"], capsys, monkeypatch)
	lines_bool = out_bools.splitlines()
	assert len(lines_bool) == 3
	for line in lines_bool:
		assert line in ["True", "False"]

	# Generate 3 floats
	out_floats = run_cli_integration(["generate", image_path, "--type", "float", "-n", "3"], capsys, monkeypatch)
	lines_float = out_floats.splitlines()
	assert len(lines_float) == 3
	for line in lines_float:
		assert 0.0 <= float(line) <= 1.0


def test_generate_deterministic(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch):
	"""Test that --deterministic produces identical sequences across runs."""
	base_dir = Path(__file__).resolve().parent.parent
	image_path = str(base_dir / "data" / "DSC02111.ARW")

	# Run 1
	out1 = run_cli_integration(["generate", image_path, "--type", "int", "-n", "10", "--deterministic"], capsys, monkeypatch)

	# Run 2
	out2 = run_cli_integration(["generate", image_path, "--type", "int", "-n", "10", "--deterministic"], capsys, monkeypatch)

	assert out1 == out2
	assert len(out1.splitlines()) == 10


def test_generate_nondeterministic(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch):
	"""Test that default (salted) generation produces different sequences."""
	base_dir = Path(__file__).resolve().parent.parent
	image_path = str(base_dir / "data" / "DSC02111.ARW")

	# Run 1
	out1 = run_cli_integration(["generate", image_path, "--type", "int", "-n", "10"], capsys, monkeypatch)

	# Run 2
	out2 = run_cli_integration(["generate", image_path, "--type", "int", "-n", "10"], capsys, monkeypatch)

	# It is statistically impossible (1 in ~2^512) for these to match
	assert out1 != out2
