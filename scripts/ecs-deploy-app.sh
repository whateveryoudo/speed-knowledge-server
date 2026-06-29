#!/usr/bin/env bash
# ECS 上执行：从 ACR 拉取业务镜像并重建容器
#
# 用法（在 ECS 项目目录）:
#   ./scripts/ecs-deploy-app.sh              # 默认 app
#   ./scripts/ecs-deploy-app.sh app
#   ./scripts/ecs-deploy-app.sh app nestjs
#   IMAGE_TAG=v1.2.0 ./scripts/ecs-deploy-app.sh app
#
# 若 compose 使用非 latest tag，需在 ECS .env 中设置:
#   APP_IMAGE_TAG=v1.2.0
# 并在 docker-compose.yml 里把 app 镜像改为:
#   image: ${ACR_REGISTRY}/app:${APP_IMAGE_TAG:-latest}
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -f .env ]]; then
  set -a
  # shellcheck source=/dev/null
  source .env
  set +a
fi

IMAGE_TAG="${IMAGE_TAG:-${APP_IMAGE_TAG:-latest}}"
SERVICES=("$@")
if [[ ${#SERVICES[@]} -eq 0 ]]; then
  SERVICES=(app)
fi

# 将 tag 传给 compose（app / nestjs 使用独立变量）
export APP_IMAGE_TAG="${IMAGE_TAG}"
export NESTJS_IMAGE_TAG="${IMAGE_TAG}"

echo "==> pull ${SERVICES[*]} (tag: ${IMAGE_TAG})"
docker compose pull "${SERVICES[@]}"

echo "==> recreate ${SERVICES[*]}"
docker compose up -d --force-recreate --no-deps "${SERVICES[@]}"

echo ""
echo "==> 状态"
docker compose ps "${SERVICES[@]}"

echo ""
echo "查看日志: docker compose logs ${SERVICES[0]} --tail 80"
echo "健康检查: curl -s http://127.0.0.1/api/health || curl -s http://127.0.0.1/health"
