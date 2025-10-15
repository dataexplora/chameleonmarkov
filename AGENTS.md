# Repository Guidelines

## Project Structure & Module Organization
- `chameleon_server.py`: Flask web app (serves `templates/` and `static/`).
- `CM_generate/`, `CM_train/`, `CM_blending/`, `CM_auxiliary/`: core generation, training, blending, and helper modules.
- `CM_NN_VL/`: LSTM voice-leading model, training scripts, and assets.
- `training_data/`: XML datasets; `trained_idioms/` and `blended_idioms/`: model artifacts (`.pickle`).
- `templates/`, `static/`: UI (HTML/CSS/JS) and generated outputs (`static/harmonisations/`).
- Top-level scripts: `train_all_idioms.py`, `blend_all_idioms.py`, `idiom_printer.py`.
- Infra: `requirements.txt`, `Dockerfile`, `docker-compose.yml`, `SETUP_GUIDE.md`, `DEPLOYMENT_CLOUDFLARE.md`.

## Build, Test, and Development Commands
- Setup: `python -m venv .venv && .venv\Scripts\activate` (Windows), then `pip install -r requirements.txt`.
- Run server: `python chameleon_server.py` (serves on `http://localhost:8885`).
- Train idioms: `python train_all_idioms.py` (writes to `trained_idioms/`).
- Blend idioms: `python blend_all_idioms.py` (writes to `blended_idioms/`).
- Docker (optional): `docker compose up --build` (uses `Dockerfile`/`docker-compose.yml`).

## Coding Style & Naming Conventions
- Python 3.8+; follow PEP 8, 4-space indentation.
- Names: modules `lower_snake_case.py`; functions/vars `snake_case`; classes `PascalCase`.
- Imports: prefer explicit module imports; avoid relative path hacks—if needed, centralize sys.path edits in entrypoints.
- Keep functions small and pure; avoid side effects in import time. Use `if __name__ == "__main__":` for script entry.

## Testing Guidelines
- No formal test suite yet. Add `pytest` tests under `tests/` (e.g., `tests/test_harmonise.py`).
- Provide small fixture XMLs under `tests/fixtures/` and assert deterministic outputs for simple modes.
- Smoke test: start server and upload a sample XML; verify `.xml/.mid` appear in `static/harmonisations/`.

## Commit & Pull Request Guidelines
- Commits: imperative mood, concise subject; optional scope (e.g., `feat: add BBVL toggle`, `fix(server): guard empty uploads`).
- PRs: include purpose, runnable steps, sample input, and screenshots of UI if applicable. Link related issues.
- Avoid committing large binaries or `.venv/`; keep generated models out of Git unless essential. Use `.gitignore` and document data sources.

## Security & Configuration Tips
- Never commit secrets. Expose config via env vars if added later.
- Validate and sanitize uploaded files; keep `static/harmonisations/` cleaned (see cleanup in server code).
- For deployment, see `DEPLOYMENT_CLOUDFLARE.md`; ensure port 8885 mapping is correct.

