import enum
import sys
import typing
from pathlib import Path

import pytest

from trcks_example_cyclopts.user_interface import app

INPUT_TEXT = "Hello, World!"


class ExitCode(enum.IntEnum):
    SUCCESS = 0
    ENCODING_ERROR = 1
    FILE_NOT_FOUND = 2
    PATH_IS_A_DIRECTORY = 3
    NOT_ENOUGH_PERMISSIONS = 4


@pytest.fixture
def input_path(tmp_path: Path) -> Path:
    _input = tmp_path / "input"
    assert not _input.exists()
    return _input


@pytest.fixture
def output_path(tmp_path: Path) -> Path:
    _output = tmp_path / "output"
    assert not _output.exists()
    return _output


@pytest.fixture
def output_path_with_patched_open_method(
    monkeypatch: pytest.MonkeyPatch,
    output_path: Path,
) -> Path:
    original_open = Path.open

    @typing.no_type_check
    def patched_open(self, mode="r", *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if self == output_path and mode == "a":
            msg = "some message"
            raise ValueError(msg)
        return original_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", patched_open)

    return output_path


def test_app_succeeds(
    capsys: pytest.CaptureFixture[str], input_path: Path, output_path: Path
) -> None:
    input_path.write_text(INPUT_TEXT)

    with pytest.raises(SystemExit) as exc_info:
        app([str(input_path), "--output", str(output_path)])
    out, err = capsys.readouterr()

    assert exc_info.value.code == ExitCode.SUCCESS
    assert out == ""
    assert err == ""
    assert input_path.read_text() == INPUT_TEXT
    assert output_path.read_text() == f"Length: {len(INPUT_TEXT)}\n"


def test_app_succeeds_with_multiple_inputs(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, output_path: Path
) -> None:
    input_path_1 = tmp_path / "input_1"
    input_path_2 = tmp_path / "input_2"
    input_text_1 = "Hello"
    input_text_2 = "Hello, World!"
    input_path_1.write_text(input_text_1)
    input_path_2.write_text(input_text_2)

    with pytest.raises(SystemExit) as exc_info:
        app([str(input_path_1), str(input_path_2), "--output", str(output_path)])
    out, err = capsys.readouterr()

    assert exc_info.value.code == ExitCode.SUCCESS
    assert out == ""
    assert err == ""
    assert output_path.read_text() == (
        f"Length: {len(input_text_1)}\nLength: {len(input_text_2)}\n"
    )


def test_app_succeeds_with_no_inputs(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        app([])
    out, err = capsys.readouterr()

    assert exc_info.value.code == ExitCode.SUCCESS
    assert out == ""
    assert err == ""


def test_app_writes_to_stdout_by_default(
    capsys: pytest.CaptureFixture[str], input_path: Path
) -> None:
    input_path.write_text(INPUT_TEXT)

    with pytest.raises(SystemExit) as exc_info:
        app([str(input_path)])
    out, err = capsys.readouterr()

    assert exc_info.value.code == ExitCode.SUCCESS
    assert out == f"Length: {len(INPUT_TEXT)}\n"
    assert err == ""
    assert input_path.read_text() == INPUT_TEXT


def test_app_writes_multiple_results_to_stdout_by_default(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    input_path_1 = tmp_path / "input_1"
    input_path_2 = tmp_path / "input_2"
    input_text_1 = "Hello"
    input_text_2 = "Hello, World!"
    input_path_1.write_text(input_text_1)
    input_path_2.write_text(input_text_2)

    with pytest.raises(SystemExit) as exc_info:
        app([str(input_path_1), str(input_path_2)])
    out, err = capsys.readouterr()

    assert exc_info.value.code == ExitCode.SUCCESS
    assert out == f"Length: {len(input_text_1)}\nLength: {len(input_text_2)}\n"
    assert err == ""


def test_app_fails_on_input_encoding_error(
    capsys: pytest.CaptureFixture[str], input_path: Path, output_path: Path
) -> None:
    input_bytes = b"\x80\x81\x82\x83"  # invalid UTF-8
    input_path.write_bytes(input_bytes)

    with pytest.raises(SystemExit) as exc_info:
        app([str(input_path), "--output", str(output_path)])
    out, err = capsys.readouterr()

    assert exc_info.value.code == ExitCode.ENCODING_ERROR
    assert out == ""
    assert err == f"Error: Encoding error in input file, Path: {input_path}\n"
    assert input_path.read_bytes() == input_bytes
    assert not output_path.exists()


def test_app_fails_on_output_encoding_error(
    capsys: pytest.CaptureFixture[str],
    input_path: Path,
    output_path_with_patched_open_method: Path,
) -> None:
    input_path.write_text(INPUT_TEXT)
    expected_error_message = (
        "Error: Encoding error in output file, "
        f"Path: {output_path_with_patched_open_method}\n"
    )

    with pytest.raises(SystemExit) as exc_info:
        app([str(input_path), "--output", str(output_path_with_patched_open_method)])
    out, err = capsys.readouterr()

    assert exc_info.value.code == ExitCode.ENCODING_ERROR
    assert out == ""
    assert err == expected_error_message
    assert input_path.read_text() == INPUT_TEXT
    assert not output_path_with_patched_open_method.exists()


def test_app_fails_on_non_existent_input_file(
    capsys: pytest.CaptureFixture[str], input_path: Path, output_path: Path
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        app([str(input_path), "--output", str(output_path)])
    out, err = capsys.readouterr()

    assert exc_info.value.code == ExitCode.FILE_NOT_FOUND
    assert out == ""
    assert err == f"Error: Input file not found, Path: {input_path}\n"
    assert not input_path.exists()
    assert not output_path.exists()


def test_app_fails_on_non_existent_output_directory(
    capsys: pytest.CaptureFixture[str], input_path: Path, output_path: Path
) -> None:
    input_path.write_text(INPUT_TEXT)
    output_file = output_path / "file"

    with pytest.raises(SystemExit) as exc_info:
        app([str(input_path), "--output", str(output_file)])
    out, err = capsys.readouterr()

    assert exc_info.value.code == ExitCode.FILE_NOT_FOUND
    assert out == ""
    assert err == f"Error: Output file not found, Path: {output_file}\n"
    assert input_path.read_text() == INPUT_TEXT
    assert not output_path.exists()


def test_app_fails_on_input_directory(
    capsys: pytest.CaptureFixture[str], input_path: Path, output_path: Path
) -> None:
    input_path.mkdir()
    if sys.platform == "win32":
        expected_exit_code = ExitCode.NOT_ENOUGH_PERMISSIONS
        expected_error_message = (
            f"Error: Not enough permissions for input file, Path: {input_path}\n"
        )
    else:
        expected_exit_code = ExitCode.PATH_IS_A_DIRECTORY
        expected_error_message = (
            f"Error: Input path is a directory, Path: {input_path}\n"
        )

    with pytest.raises(SystemExit) as exc_info:
        app([str(input_path), "--output", str(output_path)])
    out, err = capsys.readouterr()

    assert exc_info.value.code == expected_exit_code
    assert out == ""
    assert err == expected_error_message
    assert input_path.is_dir()
    assert not output_path.exists()


def test_app_fails_on_output_directory(
    capsys: pytest.CaptureFixture[str], input_path: Path, output_path: Path
) -> None:
    input_path.write_text(INPUT_TEXT)
    output_path.mkdir()
    if sys.platform == "win32":
        expected_exit_code = ExitCode.NOT_ENOUGH_PERMISSIONS
        expected_error_message = (
            f"Error: Not enough permissions for output file, Path: {output_path}\n"
        )
    else:
        expected_exit_code = ExitCode.PATH_IS_A_DIRECTORY
        expected_error_message = (
            f"Error: Output path is a directory, Path: {output_path}\n"
        )

    with pytest.raises(SystemExit) as exc_info:
        app([str(input_path), "--output", str(output_path)])
    out, err = capsys.readouterr()

    assert exc_info.value.code == expected_exit_code
    assert out == ""
    assert err == expected_error_message
    assert input_path.read_text() == INPUT_TEXT
    assert output_path.is_dir()


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Permission chmod 0o000 unreliable on Windows",
)
def test_app_fails_on_input_permission_error(
    capsys: pytest.CaptureFixture[str], input_path: Path, output_path: Path
) -> None:
    input_path.write_text(INPUT_TEXT)
    old_mode = input_path.stat().st_mode
    input_path.chmod(0o000)

    with pytest.raises(SystemExit) as exc_info:
        app([str(input_path), "--output", str(output_path)])
    out, err = capsys.readouterr()

    assert exc_info.value.code == ExitCode.NOT_ENOUGH_PERMISSIONS
    assert out == ""
    assert err == f"Error: Not enough permissions for input file, Path: {input_path}\n"
    input_path.chmod(old_mode)
    assert input_path.read_text() == INPUT_TEXT
    assert not output_path.exists()


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Permission mkdir 0o500 unreliable on Windows",
)
def test_app_fails_on_output_permission_error(
    capsys: pytest.CaptureFixture[str], input_path: Path, output_path: Path
) -> None:
    input_path.write_text(INPUT_TEXT)
    output_path.mkdir(mode=0o500)
    output_file = output_path / "file"
    expected_error_message = (
        f"Error: Not enough permissions for output file, Path: {output_file}\n"
    )

    with pytest.raises(SystemExit) as exc_info:
        app([str(input_path), "--output", str(output_file)])
    out, err = capsys.readouterr()

    assert exc_info.value.code == ExitCode.NOT_ENOUGH_PERMISSIONS
    assert out == ""
    assert err == expected_error_message
    assert input_path.read_text() == INPUT_TEXT
    assert not output_file.exists()


def test_app_fails_when_second_input_file_is_not_found(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, output_path: Path
) -> None:
    input_path_1 = tmp_path / "input_1"
    input_path_2 = tmp_path / "input_2"
    input_path_1.write_text(INPUT_TEXT)
    assert not input_path_2.exists()

    with pytest.raises(SystemExit) as exc_info:
        app([str(input_path_1), str(input_path_2), "--output", str(output_path)])
    out, err = capsys.readouterr()

    assert exc_info.value.code == ExitCode.FILE_NOT_FOUND
    assert out == ""
    assert err == f"Error: Input file not found, Path: {input_path_2}\n"
    assert not output_path.exists()
