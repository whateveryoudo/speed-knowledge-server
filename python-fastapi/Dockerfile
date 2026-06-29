# 多阶段构建
# 国内 Mac 默认走 DaoCloud 镜像；可覆盖: --build-arg PYTHON_IMAGE=python:3.13-slim
ARG PYTHON_IMAGE=docker.m.daocloud.io/library/python:3.13-slim
FROM ${PYTHON_IMAGE} AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv


WORKDIR /app


# 安装依赖
COPY pyproject.toml uv.lock ./
ENV UV_LINK_MODE=copy
RUN uv sync --frozen --no-dev --no-install-project

# 复制应用代码
COPY . .

RUN uv sync --frozen --no-dev

FROM ${PYTHON_IMAGE}

WORKDIR /app


RUN useradd -m -u 1001 fastapi

COPY --from=builder --chown=fastapi:fastapi /app /app

USER fastapi

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8010

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8010/health')" || exit 1

# 启动应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]

