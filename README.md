# trcks-example-cyclopts

This example CLI application shows you how to use
the [trcks](https://pypi.org/project/trcks/) library
for type-safe railway-oriented programming in Python.

## How It Works

The [trcks_example_cyclopts._service](src/trcks_example_cyclopts/_service.py)
module contains three private functions.
The `_extract` and `_load` functions return `trcks.Result` objects.
The `_transform` function returns a `str` object.
This module also contains the public function `extract_transform_load`, which
composes the private functions using `trcks.oop.Wrapper` and
returns a `trcks.Result` object.

The [trcks_example_cyclopts](src/trcks_example_cyclopts/__init__.py) module
contains the [cyclopts](https://pypi.org/project/cyclopts/) application `app`
and its default action handler.
The action handler calls the public function `extract_transform_load` and
returns an appropriate exit code based on the result.

## Quick Start

1. Install `uv` if you haven't already.
2. Clone the `trcks-example-cyclopts` repository and navigate into it.
3. Run `uv run tec --help` to see the available commands.
