# CHAMELEON

This is the code for the online version of the CHAMELEON melodic harmonisation assistant that includes blending.

In this version several things are not working properly and several things are missing, but they will all be worked out
gradually.

## Changelog (2025)

### UI/UX Redesign
- Full rebuild of the front page (`templates/index.html`, `static/style.css`) into a minimal, clean, two-tone design.
- Unified settings into a single card with modern toggles; automatic Blend when both styles are ON.
- Drag-and-drop file zone with click-to-open, clear CTA, and consistent component styling.
- Robust loading/result states; improved OSMD rendering container and controls (Play/Stop/Download).
- Removed Materialize and legacy JS inits that caused duplicated dropdowns; fixed paths for assets.
- Persisted form state and last file via `localStorage` for smoother “Harmonize again”.

### Score Generation and Exports
- Always render harmony on Bass clef; final score assembled as `music21.stream.Score` for reliable MusicXML/MIDI export.
- Conditional register normalisation: if harmony’s lowest pitch > D3, transpose harmony down one octave.
- Stable MIDI export by ensuring measures exist before writing (prevents expandRepeats errors).
- Metadata in MusicXML:
  - Title: `<inputName> - <uid>` (uid from request code suffix)
  - Subtitle: `idiom=<...> | blend=<True/False> | grp=<0/1> | vl=<...>`
  - Composer: `Chameleon Harmoniser`
- Filenames preserved: `<inputName>_<idiom>_grp<0/1>_<VL>_<uid>.xml/.mid`.

### Backend Improvements (Flask)
- Outputs written only to `static/harmonisations/`; periodic cleanup with `purge_old_files` to limit disk usage.
- Fixed `send_file` usage for Flask 2.x; hardened upload handling; corrected idiom load paths.
- Eliminated empty wrapper artefacts on view transitions; improved error handling and logging.

### Training
- `train_all_idioms.py` now:
  - Safely iterates folders, skipping those without XMLs.
  - Creates `training_logs/` if missing.
  - Skips writing if `trained_idioms/<idiom>.pickle` already exists (resume-friendly).

### Blending
- `blend_all_idioms.py` scans `trained_idioms/`, excludes existing `bl_*.pickle` from input list, and writes new blends to `trained_idioms/`.
- `CM_blending/CM_BlendingSession.py`:
  - Skips self-blends.
  - Skips writing if the target `bl_*.pickle` already exists (resume without overwriting).

### Deployment
- Added Dockerfile and docker-compose for reproducible builds; Traefik-ready setup for TLS via certresolver.
- Documented production flow (`docker compose up -d --build`). Suggested CI/CD via GitHub Actions (SSH deploy or GHCR + Watchtower).

### Misc Fixes
- `.gitignore` updated to keep `static/harmonisations/.gitkeep` and ignore generated files.
- Fixed multiple asset paths (CSS/JS/images). Resolved “harmonize again” state issues.

---
If you need a per-file diff summary or want flags (e.g., force overwrite) for training/blending scripts, see issues or open a PR.