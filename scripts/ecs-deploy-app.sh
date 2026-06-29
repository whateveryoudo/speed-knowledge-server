#!/usr/bin/env bash
# ECS 上执行：从 ACR 拉取业务镜像并重建容器
#
# 用法（在 ECS 项目目录）:
#   ./scripts/ecs-deploy-app.sh              # 默认 app + nestjs
#   ./scripts/ecs-deploy-app.sh app
#   ./scripts/ecs-deploy-app.sh nestjs
#   ./scripts/ecs-deploy-app.sh app nestjs
#   ./scripts/ecs-deploy-app.sh all          # 同默认
#   IMAGE_TAG=v1.2.0 ./scripts/ecs-deploy-app.sh -t v1.2.0 app
#
# 若 compose 使用非 latest tag，可在 ECS .env 中设置 APP_IMAGE_TAG / NESTJS_IMAGE_TAG
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -f .env ]]; then
  set -a
  # shellcheck source=/dev/null
  source .env
  set +a
fi

IMAGE_TAG="${IMAGE_TAG:-${APP_IMAGE_TAG:-latest}}"
SERVICES=()

usage() {
  sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
  echo ""
  echo "选项:"
  echo "  -t, --tag TAG   镜像 tag（默认 latest，或 .env 中 APP_IMAGE_TAG）"
  echo "  -h, --help      显示帮助"
  echo ""
  echo "服务名: app | nestjs | all（all = app + nestjs）"
  exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--tag)
      IMAGE_TAG="$2"
      shift 2
      ;;
    -h|--help)
      usage 0
      ;;
    app|nestjs|all)
      SERVICES+=("$1")
      shift
      ;;
    *)
      echo "未知参数: $1" >&2
      usage 1
      ;;
  esac
done

if [[ ${#SERVICES[@]} -eq 0 ]]; then
  SERVICES=(app nestjs)
fi

if [[ "${SERVICES[*]}" == *all* ]]; then
  SERVICES=(app nestjs)
fi

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
echo "app 健康:   curl -s http://127.0.0.1/api/health"
echo "nestjs:     docker compose exec nestjs wget -qO- http://127.0.0.1:3000/health"
