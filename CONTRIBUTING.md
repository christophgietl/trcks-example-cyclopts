# Contributing to `trcks-example-cyclopts`

Thank you for considering contributing to `trcks-example-cyclopts`!
The following section describes how to set up and use a development environment.

## Development environment

> [!WARNING]
> The symlink [.agents/skills/trcks](.agents/skills/trcks) points to the POSIX
> path
> `../../.venv/lib/python3.14/site-packages/trcks/.agents/skills/trcks`.
> Windows users might need to reinstall the `trcks` library skill as described in
> [the section "Development tools" in `AGENTS.md`](AGENTS.md#development-tools)
> in order to get the appropriate path for their system.

`trcks-example-cyclopts` uses the following developer tools:

- [Library Skills](https://library-skills.io) for managing library skills for coding agents
- [pre-commit](https://pre-commit.com) for managing pre-commit hooks
  (particularly for code formatting and linting)
- [pyrefly](https://pyrefly.org) for static type checking
- [pytest](https://pytest.org) for unit testing and doctests
- [uv](https://docs.astral.sh/uv/) for dependency management and packaging

### Setup

Please follow these steps to set up your development environment:

1. Install `uv` if you have not already done so.
2. Clone the `trcks-example-cyclopts` repository and `cd` into it.
3. Install `trcks-example-cyclopts` and its (development) dependencies
   by running `uv sync`.
4. Set up the hooks by executing `uv run pre-commit install`.
   The output should look something like this:

   ```plain
   pre-commit installed at .git/hooks/commit-msg
   pre-commit installed at .git/hooks/pre-commit
   ```

### Usage

Check [the section "Development tools" in `AGENTS.md`](AGENTS.md#development-tools)
for instructions on how to use the development tools.
