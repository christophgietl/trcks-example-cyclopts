from typing import TYPE_CHECKING, Literal

from trcks.oop import Wrapper

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from trcks import Result

type _ExtractFailureLiteral = Literal[
    "Encoding error in input file",
    "Input file not found",
    "Input path is a directory",
    "Not enough permissions for input file",
]

type _LoadFailureLiteral = Literal[
    "Encoding error in output file",
    "Not enough permissions for output file",
    "Output file not found",
    "Output path is a directory",
]

type _LoadResult = Result[_LoadFailureLiteral, None]

type FailureLiteral = _ExtractFailureLiteral | _LoadFailureLiteral


def _extract(input_: Path) -> Result[_ExtractFailureLiteral, str]:
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


def _load(output: Path) -> Callable[[str], _LoadResult]:
    def inner(s: str) -> _LoadResult:
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

    return inner


def _transform(s: str) -> str:
    return f"Length: {len(s)}"


def extract_transform_load(input_: Path, output: Path) -> Result[FailureLiteral, None]:
    return (
        Wrapper(input_)
        .map_to_result(_extract)
        .map_success(_transform)
        .map_success_to_result(_load(output))
        .core
    )
