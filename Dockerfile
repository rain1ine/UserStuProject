FROM python:3.14-slim

WORKDIR /app

# 安装依赖（利用 Docker 缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码（保留 app 包结构：/app/app/main.py）
COPY app/ ./app/
COPY static/ ./static/

EXPOSE 8000

# 生产模式启动
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
