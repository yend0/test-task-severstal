#!/bin/bash
uv run uvicorn warehouse_app.app:create_app --reload --factory --host 0.0.0.0 --workers 1 --port 8000