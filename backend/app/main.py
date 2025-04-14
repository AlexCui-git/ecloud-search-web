from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.api.endpoints import router as api_router
import os

app = FastAPI(
    title="ECloud Search API",
    description="移动云帮助中心搜索服务",
    version="1.0.0"
)

# 配置静态文件
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>ECloud Search API</title>
            <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
        </head>
        <body>
            <h1>Welcome to ECloud Search API</h1>
            <p>API documentation available at <a href="/docs">/docs</a></p>
        </body>
    </html>
    """

app.include_router(api_router, prefix="/api")