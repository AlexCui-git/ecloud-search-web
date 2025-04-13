# ECloud Search Web

基于 FastAPI 和 Vue.js 的移动云帮助中心搜索工具

## 技术栈

- 后端: FastAPI + Playwright
- 前端: Vue 3 + Element Plus

## 快速开始

### 后端设置
```bash
cd backend
pip install -r requirements.txt
python -m playwright install chromium
uvicorn app.main:app --reload --port 8000
```

### 前端设置
```bash
cd frontend
npm install
npm run dev
```

## 项目文档

- API 文档: http://localhost:8000/docs
- 前端访问: http://localhost:5173