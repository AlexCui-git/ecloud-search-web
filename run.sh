#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查并清理已使用的端口
check_and_kill_port() {
    local port=$1
    if lsof -i :$port > /dev/null; then
        echo -e "${RED}Port $port is in use. Killing process...${NC}"
        kill -9 $(lsof -ti:$port) 2>/dev/null
        sleep 1
    fi
}

# 错误处理函数
handle_error() {
    echo -e "${RED}Error occurred in script at line $1${NC}"
    # 清理所有相关进程
    pkill -f "uvicorn"
    pkill -f "vite"
    exit 1
}

# 设置错误处理
trap 'handle_error $LINENO' ERR

# 检查必要的程序是否安装
command -v uvicorn >/dev/null 2>&1 || { echo -e "${RED}uvicorn is required but not installed${NC}"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo -e "${RED}npm is required but not installed${NC}"; exit 1; }

# 清理已使用的端口
check_and_kill_port 8000
check_and_kill_port 3000

# 启动后端
echo -e "${GREEN}Starting backend server...${NC}"
cd backend || { echo -e "${RED}Backend directory not found${NC}"; exit 1; }
uvicorn app.main:app --reload --port 8000 &
backend_pid=$!

# 等待后端启动
sleep 2
if ! lsof -i :8000 > /dev/null; then
    echo -e "${RED}Backend failed to start${NC}"
    exit 1
fi

# 启动前端
echo -e "${GREEN}Starting frontend server...${NC}"
cd ../frontend || { echo -e "${RED}Frontend directory not found${NC}"; exit 1; }
npm run dev &
frontend_pid=$!

# 清理函数
cleanup() {
    echo -e "${GREEN}Cleaning up processes...${NC}"
    kill $backend_pid 2>/dev/null
    kill $frontend_pid 2>/dev/null
    pkill -f "uvicorn"
    pkill -f "vite"
}

# 设置清理钩子
trap cleanup EXIT

# 等待所有进程
echo -e "${GREEN}Services started successfully!${NC}"
echo -e "${GREEN}Backend running on http://localhost:8000${NC}"
echo -e "${GREEN}Frontend running on http://localhost:3000${NC}"
echo -e "${GREEN}Press Ctrl+C to stop all services${NC}"

wait