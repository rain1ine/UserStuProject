
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
from app.api.user import router as user_router
from app.api.student import router as student_router
from app.api.model import router as model_router
from app.api.teacher import router as teacher_router
from app.api.classes import router as classes_router
from app.api.course import router as course_router
app = FastAPI(title="学校管理系统")

# CORS 中间件 — 允许跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由（必须在静态文件挂载之前注册，确保 API 路径优先匹配）
app.include_router(user_router)
app.include_router(student_router)
app.include_router(model_router)
app.include_router(teacher_router)
app.include_router(classes_router)
app.include_router(course_router)


@app.get("/")
def index():
    return {"message": "欢迎进入学校管理平台"}


# 静态文件目录 — 基于本文件的绝对路径，确保无论从哪里启动都能找到
STATIC_DIR = str(Path(__file__).resolve().parent.parent / "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")



if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)

