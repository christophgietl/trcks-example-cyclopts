# AI coding agent instructions for `trcks-example-cyclopts`

## Project requirements

- Demonstrate how to use the `trcks` library in a CLI application.
- Use the CLI library `cyclopts`.

## Architecture decisions

- `trcks_example_cyclopts.service` contains I/O functions returning `trcks.Result`.
- `trcks_example_cyclopts.user_interface` contains the CLI entry point `app` and
  its action handlers; handlers call I/O functions and return exit codes.

## Code style

- Sort functions alphabetically within each module.
- Sort classes alphabetically within each module.
- Sort methods alphabetically within each class.
- Do not use `from __future__ import annotations` (not needed in Python 3.14+).

## Development tools

`trcks-example-cyclopts` uses `uv` for managing dependencies and tools.

```shell
# Run linting and code formatting:
uv run pre-commit run --all-files
# Check types:
uv run mypy
# Run tests:
uv run pytest
# Build distribution package:
uv build
# Run the example application:
uv run rtw --help
```

## Testing strategy

- Invoke `trcks_example_cyclopts.user_interface.app` directly.
- Dedicate a test case to every exit code and failure branch.
- Assert exit code, stdout, stderr and filesystem state after every call.
- Do not mock `trcks_example_cyclopts.service` functions.
- Use `monkeypatch` to simulate errors (e.g. raise `ValueError` from `Path.open`).
- 100% coverage required; mark unreachable lines with `# pragma: no cover`
  (not needed for `if TYPE_CHECKING`).

## Documentation requirements

- Update `AGENTS.md` on architecture and tooling changes.
- Update `CONTRIBUTING.md` on tooling changes.
- Update `README.md` on feature and UI changes.
