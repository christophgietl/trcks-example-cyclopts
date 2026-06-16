import logging
from typing import TYPE_CHECKING, Final, Generic, Literal, NamedTuple, TypeVar

from trcks.oop import TupleWrapper

if TYPE_CHECKING:
    from pathlib import Path

    from trcks import Result, ResultTuple

type _ReadErrorReason = Literal[
    "Encoding error in input file",
    "Input file not found",
    "Input path is a directory",
    "Not enough permissions for input file",
]
type _WriteErrorReason = Literal[
    "Encoding error in output file",
    "Not enough permissions for output file",
    "Output file not found",
    "Output path is a directory",
]
type FileErrorReason = _ReadErrorReason | _WriteErrorReason
_R_co = TypeVar("_R_co", bound=FileErrorReason, covariant=True)

_logger: Final = logging.getLogger(__name__)


class FileError(NamedTuple, Generic[_R_co]):  # noqa: UP046 # see https://github.com/python/mypy/issues/17623
    reason: _R_co
    path: Path | None


def _read(input_: Path) -> Result[FileError[_ReadErrorReason], str]:
    try:
        with input_.open("r") as f:
            s = f.read()
    except FileNotFoundError:
        return "failure", FileError(reason="Input file not found", path=input_)
    except (
        IsADirectoryError
    ):  # pragma: no cover # Python for Windows raises a PermissionError instead.
        return "failure", FileError(reason="Input path is a directory", path=input_)
    except PermissionError:
        return "failure", FileError(
            reason="Not enough permissions for input file", path=input_
        )
    except ValueError:
        return "failure", FileError(reason="Encoding error in input file", path=input_)
    else:
        return "success", s


def _transform(s: str) -> str:
    return f"Length: {len(s)}"


def _write(
    s: str, *, output: Path | None
) -> Result[FileError[_WriteErrorReason], None]:
    if output is None:
        print(s)  # noqa: T201 # needed for CLI output
        return "success", None

    try:
        with output.open("a") as f:
            f.write(s + "\n")
    except FileNotFoundError:
        return "failure", FileError(reason="Output file not found", path=output)
    except (
        IsADirectoryError
    ):  # pragma: no cover # Python for Windows raises a PermissionError instead.
        return "failure", FileError(reason="Output path is a directory", path=output)
    except PermissionError:
        return "failure", FileError(
            reason="Not enough permissions for output file", path=output
        )
    except ValueError:
        return "failure", FileError(reason="Encoding error in output file", path=output)
    else:
        return "success", None


def read_transform_write(
    inputs: tuple[Path, ...], output: Path | None
) -> ResultTuple[FileError[FileErrorReason], None]:
    return (
        TupleWrapper(inputs)
        .map_to_result(_read)
        .tap_successes(lambda s: _logger.debug("Transforming %r ...", s))
        .map_successes(_transform)
        .tap_successes(lambda s: _logger.debug("Transformed into %r.", s))
        .map_successes_to_result(lambda s: _write(s, output=output))
        .core
    )
