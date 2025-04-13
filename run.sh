#!/bin/bash

# 启动后端
cd backend
uvicorn app.main:app --reload --port 8000 &

# 启动前端
cd ../frontend
npm run dev &

wait
