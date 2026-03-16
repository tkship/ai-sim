# Repository Guidelines

## Project Structure & Module Organization
Core code lives in `src/`, organized by domain modules:
- `src/character`, `src/item`, `src/realm`, `src/interaction`, `src/world`, `src/game`, `src/ai`, `src/ui`
- Main game entrypoint: `src/main.py`
- Lightweight root entrypoint: `main.py`

Runtime/config artifacts are in the repository root:
- `config.yaml` for game and world configuration
- `game.db` for local SQLite data
- `test_game.py` for integration-style checks
- `openspec/` for design proposals and specs

## Build, Test, and Development Commands
Use `uv` for environment and execution:
- `uv sync` installs dependencies from `pyproject.toml`/`uv.lock`
- `uv run python src/main.py` starts the game loop with UI
- `uv run python test_game.py` runs the current test script (world, database, character flows)
- `uv run python main.py` runs the minimal root entrypoint

If `uv` is unavailable, create a Python 3.13+ venv and install equivalent packages from `pyproject.toml`.

## Coding Style & Naming Conventions
Follow current Python style in `src/`:
- 4-space indentation, type hints, and `dataclass` usage where appropriate
- `snake_case` for functions/variables/modules, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants
- Keep modules domain-focused (do not mix UI, persistence, and combat logic in one file)
- Prefer small immutable-style update methods for entities (see `Character.with_*` patterns)

No formatter/linter is configured yet. Keep imports tidy and code consistent with existing files.

## Testing Guidelines
Current testing is script-based, not `pytest`-based:
- Add scenario tests to `test_game.py` as `test_*` functions
- Keep tests deterministic and avoid requiring manual UI interaction
- Validate key state transitions (attributes, inventory, realm progress, DB reads/writes)

Run tests with:
- `uv run python test_game.py`

## Commit & Pull Request Guidelines
History currently uses short, direct commit subjects (for example: `first version with openspec`).
Use concise, imperative commit messages and keep one logical change per commit.

For pull requests:
- Describe what changed and why
- List manual test steps/commands executed
- Link related spec/docs in `openspec/` when relevant
- Include screenshots only when UI behavior changes

## Security & Configuration Tips
- Do not commit secrets, tokens, or private endpoints in `config.yaml`
- Treat `game.db` as local runtime data; avoid committing large or noisy DB diffs
- Keep `.venv/` and generated caches out of version control
