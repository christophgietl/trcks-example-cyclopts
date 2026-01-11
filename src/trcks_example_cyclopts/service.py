import functools
import logging
from typing import TYPE_CHECKING, Literal

from trcks.oop import Wrapper

if TYPE_CHECKING:
    from pathlib import Path

    from trcks import Result

_logger = logging.getLogger(__name__)

type _ReadFailureLiteral = Literal[
    "Encoding error in input file",
    "Input file not found",
    "Input path is a directory",
    "Not enough permissions for input file",
]

type _WriteFailureLiteral = Literal[
    "Encoding error in output file",
    "Not enough permissions for output file",
    "Output file not found",
    "Output path is a directory",
]

type _ReadResult = Result[_ReadFailureLiteral, str]

type _WriteResult = Result[_WriteFailureLiteral, None]

type FailureLiteral = _ReadFailureLiteral | _WriteFailureLiteral


def _read(input_: Path) -> _ReadResult:
    try:
        with input_.open("r") as f:
            s = f.read()
    except FileNotFoundError:
        return "failure", "Input file not found"
    except (
        IsADirectoryError
    ):  # pragma: no cover # Python for Windows raises a PermissionError instead.
        return "failure", "Input path is a directory"
    except PermissionError:
        return "failure", "Not enough permissions for input file"
    except ValueError:
        return "failure", "Encoding error in input file"
    else:
        return "success", s


def _transform(s: str) -> str:
    return f"Length: {len(s)}"


def _write(s: str, *, output: Path) -> _WriteResult:
    try:
        with output.open("w") as f:
            _ = f.write(s)
    except FileNotFoundError:
        return "failure", "Output file not found"
    except (
        IsADirectoryError
    ):  # pragma: no cover # Python for Windows raises a PermissionError instead.
        return "failure", "Output path is a directory"
    except PermissionError:
        return "failure", "Not enough permissions for output file"
    except ValueError:
        return "failure", "Encoding error in output file"
    else:
        return "success", None


def read_transform_write(input_: Path, output: Path) -> Result[FailureLiteral, None]:
    return (
        Wrapper(input_)
        .map_to_result(_read)
        .tap_success(lambda s: _logger.debug("Transforming %r ...", s))
        .map_success(_transform)
        .tap_success(lambda s: _logger.debug("Transformed into %r.", s))
        .map_success_to_result(functools.partial(_write, output=output))
        .core
    )
