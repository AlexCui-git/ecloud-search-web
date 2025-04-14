# ECloud Search Web

基于 FastAPI 和 Vue.js 的移动云帮助中心搜索工具，提供智能搜索和问答功能。

## 项目特点

- 智能搜索：使用相似度算法匹配最相关的答案
- 实时反馈：异步处理确保快速响应
- 美观界面：基于 Element Plus 的现代化 UI
- 完整日志：支持按天切割的日志记录系统

## 技术栈

### 后端
- FastAPI：高性能异步 API 框架
- Playwright：现代化浏览器自动化工具
- Python 3.9+：利用最新的异步特性

### 前端
- Vue 3：响应式前端框架
- Element Plus：优雅的 UI 组件库
- Vite：现代化构建工具

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- npm 8+

### 一键启动
```bash
# 添加执行权限
chmod +x run.sh

# 启动项目
./run.sh
```

### 手动启动

1. 后端设置
```bash
cd backend
pip install -r requirements.txt
python -m playwright install chromium
uvicorn app.main:app --reload --port 8000
```

2. 前端设置
```bash
cd frontend
npm install
npm run dev
```

## 项目结构
```
ecloud_web/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心功能
│   │   └── main.py      # 应用入口
│   └── requirements.txt  # 依赖配置
├── frontend/            # Vue.js 前端
│   ├── src/
│   │   ├── components/  # Vue 组件
│   │   └── App.vue      # 根组件
│   └── package.json     # 前端依赖
└── run.sh              # 一键启动脚本
```

## 访问地址

- 前端界面: http://localhost:5173
- API 文档: http://localhost:8000/docs
- API 详细文档: http://localhost:8000/redoc

## 开发指南

### 日志查看
```bash
tail -f backend/logs/search_automation.log
```

### 调试模式
前端开发模式自带热重载，后端使用 uvicorn 的 reload 模式：
```bash
uvicorn app.main:app --reload --port 8000 --log-level debug
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License - 详见 LICENSE 文件