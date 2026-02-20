## What
Adds a schema-first Office Skills Pack (local-only MVP):
- XLSX: multi-sheet writer + formatting + image embed (charts)
- PPTX: slide deck generator (title/bullets/images) + chart PNG embedding
- DOCX: report generator (sections/bullets/tables)
- PNG charts: render via matplotlib for artifact embedding

## Why
Fixes the "last-mile disconnect" where agents compute results but users manually copy into Excel/PowerPoint.

## How to run demo
From repo root:
python tools/examples/office_skills_pack_demo.py

## How to run tests
cd tools
python -m pytest -q -k "not symlink"

## Security
All inputs/outputs resolved using session sandbox via get_secure_path (no arbitrary FS writes).
No cloud APIs/OAuth in MVP.
