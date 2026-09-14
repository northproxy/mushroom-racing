# Data

## Policy

Do not commit large raw GIS datasets blindly.

Use this structure:

- `raw/` — source extracts, usually gitignored;
- `processed/` — derived datasets, usually gitignored;
- `samples/` — tiny reproducible fixtures safe to commit.

Every real external dataset must be documented in `docs/02_DATA_SOURCES.md`.

Keep licensing and provenance visible.
