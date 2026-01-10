import sys
from pathlib import Path
from typing import Literal, assert_never

import cyclopts

from trcks_example_cyclopts import service

type _ExitCode = Literal[0] | _PositiveExitCode
type _PositiveExitCode = Literal[1, 2, 3, 4]


app = cyclopts.App()


@app.default
def _default(input_: Path, output: Path) -> _ExitCode:  # pyright: ignore [reportUnusedFunction]
    """Read data from input file, transform it and write it to output file.

    Args:
        input_: File to read from.
        output: File to write to.
    """
    result = service.read_transform_write(input_, output)
    match result:
        case "failure", literal:
            print(f"Error: {literal}", file=sys.stderr)  # noqa: T201 # needed for CLI output
            return _to_positive_exit_code(literal)
        case "success", _:
            return 0
        case _:  # pragma: no cover
            assert_never(result)


def _to_positive_exit_code(lit: service.FailureLiteral) -> _PositiveExitCode:
    match lit:
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
            assert_never(lit)
