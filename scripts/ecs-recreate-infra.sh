#!/usr/bin/env bash
# ECS 上执行：拉取 amd64 基础镜像并重建（修复 arm64 平台警告）
# 用法: ./scripts/ecs-recreate-infra.sh
set -euo pipefail

cd "$(dirname "$0")/.."

SERVICES=(db redis nginx rabbitmq)

echo "==> pull ${SERVICES[*]}"
docker compose pull "${SERVICES[@]}"

echo "==> recreate ${SERVICES[*]}"
docker compose up -d --force-recreate "${SERVICES[@]}"

echo ""
echo "==> 检查平台（应为 amd64，不应再出现 arm64 警告）"
docker compose ps

echo ""
echo "若 app 异常，可: docker compose logs app --tail 50"
echo "数据库迁移: docker compose exec app alembic upgrade head"
