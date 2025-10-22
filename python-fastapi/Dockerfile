# 多阶段构建
FROM python:3.11-slim as builder

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 生产阶段
FROM python:3.11-slim

WORKDIR /app

# 创建非 root 用户
RUN useradd -m -u 1001 fastapi

# 从构建阶段复制依赖
COPY --from=builder /root/.local /home/fastapi/.local

# 复制应用代码
COPY . .

# 设置 Python 路径
ENV PATH=/home/fastapi/.local/bin:$PATH
ENV PYTHONPATH=/app

# 设置用户
USER fastapi

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# 启动应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

