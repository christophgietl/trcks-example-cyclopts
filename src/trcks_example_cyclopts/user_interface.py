import sys
from pathlib import Path
from typing import Literal, assert_never

import cyclopts

from trcks_example_cyclopts import service

type _ExitCode = Literal[0] | _PositiveExitCode
type _PositiveExitCode = Literal[1, 2, 3, 4]


app = cyclopts.App()


@app.default
def _default(*inputs: Path, output: Path | None = None) -> _ExitCode:
    """Read data from input files, transform it and write it to output file.

    Args:
        inputs: Files to read from.
        output: File to write to. Defaults to stdout.
    """
    match service.read_transform_write(inputs, output):
        case "failure", service.FileError(reason, path):
            print(f"Error: {reason}, Path: {path}", file=sys.stderr)  # noqa: T201 # needed for CLI output
            return _to_positive_exit_code(reason)
        case "success", _:
            return 0
        case _ as result:  # pragma: no cover
            assert_never(result)  # pyrefly: ignore[bad-argument-type]    # ty: ignore[type-assertion-failure]


def _to_positive_exit_code(reason: service.FileErrorReason) -> _PositiveExitCode:
    match reason:
        case "Encoding error in input file" | "Encoding error in output file":
            return 1
        case "Input file not found" | "Output file not found":
            return 2
        case (
            "Input path is a directory" | "Output path is a directory"
        ):  # pragma: no cover # Windows reports missing permissions in these cases.
            return 3
        case (
            "Not enough permissions for input file"
            | "Not enough permissions for output file"
        ):
            return 4
        case _:  # pragma: no cover
            assert_never(reason)
