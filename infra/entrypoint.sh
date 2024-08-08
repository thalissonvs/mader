#!/bin/bash

poetry run alembic upgrade head

poetry run fastapi run mader/app.py --host 0.0.0.0