import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Literal

from trcks.oop import TupleWrapper

if TYPE_CHECKING:
    from pathlib import Path

    from trcks import Result, ResultTuple

type _ReadFileErrorReason = Literal[
    "Encoding error in input file",
    "Input file not found",
    "Input path is a directory",
    "Not enough permissions for input file",
]
type _WriteFileErrorReason = Literal[
    "Encoding error in output file",
    "Not enough permissions for output file",
    "Output file not found",
    "Output path is a directory",
]
type FileErrorReason = _ReadFileErrorReason | _WriteFileErrorReason

_logger: Final = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True, slots=True)
class FileError:
    reason: FileErrorReason
    path: Path | None


@dataclass(frozen=True, kw_only=True, slots=True)
class _ReadFileError(FileError):
    reason: _ReadFileErrorReason


@dataclass(frozen=True, kw_only=True, slots=True)
class _WriteFileError(FileError):
    reason: _WriteFileErrorReason


def _read(input_: Path) -> Result[_ReadFileError, str]:
    try:
        with input_.open("r") as f:
            s = f.read()
    except FileNotFoundError:
        return "failure", _ReadFileError(reason="Input file not found", path=input_)
    except (
        IsADirectoryError
    ):  # pragma: no cover # Python for Windows raises a PermissionError instead.
        return "failure", _ReadFileError(
            reason="Input path is a directory", path=input_
        )
    except PermissionError:
        return "failure", _ReadFileError(
            reason="Not enough permissions for input file", path=input_
        )
    except ValueError:
        return "failure", _ReadFileError(
            reason="Encoding error in input file", path=input_
        )
    else:
        return "success", s


def _transform(s: str) -> str:
    return f"Length: {len(s)}"


def _write(s: str, *, output: Path | None) -> Result[_WriteFileError, None]:
    if output is None:
        print(s)  # noqa: T201 # needed for CLI output
        return "success", None

    try:
        with output.open("a") as f:
            f.write(s + "\n")
    except FileNotFoundError:
        return "failure", _WriteFileError(reason="Output file not found", path=output)
    except (
        IsADirectoryError
    ):  # pragma: no cover # Python for Windows raises a PermissionError instead.
        return "failure", _WriteFileError(
            reason="Output path is a directory", path=output
        )
    except PermissionError:
        return "failure", _WriteFileError(
            reason="Not enough permissions for output file", path=output
        )
    except ValueError:
        return "failure", _WriteFileError(
            reason="Encoding error in output file", path=output
        )
    else:
        return "success", None


def read_transform_write(
    inputs: tuple[Path, ...], output: Path | None
) -> ResultTuple[FileError, None]:
    return (
        TupleWrapper(inputs)
        .map_to_result(_read)
        .tap_successes(lambda s: _logger.debug("Transforming %r ...", s))
        .map_successes(_transform)
        .tap_successes(lambda s: _logger.debug("Transformed into %r.", s))
        .map_successes_to_result(lambda s: _write(s, output=output))
        .core
    )
