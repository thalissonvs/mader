#!/bin/bash

poetry run alembic upgrade head

poetry run opentelemetry-instrument uvicorn mader.app:app --host 0.0.0.0