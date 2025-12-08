#!/bin/bash
cd /opt/render/project/src
python -m uvicorn backend.app:app --host 0.0.0.0 --port $PORT
