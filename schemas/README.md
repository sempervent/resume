# Schemas

Pydantic models in `src/career_docs/models.py` are the source of truth. The JSON files in this directory are exported from those models for readers that are not running Python.

Regenerate them after a model change:

```bash
uv run python scripts/export_schemas.py
```
