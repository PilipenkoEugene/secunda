#!/bin/bash
export PYTHONPATH=/app:$PYTHONPATH
alembic upgrade head
python seed.py
uvicorn app.main:app --host $APP_HOST --port $APP_PORT