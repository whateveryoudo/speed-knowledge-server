#!/usr/bin/env bash
# 本地 Mac 执行：构建 app / nestjs 镜像并推送到阿里云 ACR
#
# 用法:
#   cp scripts/deploy.env.example scripts/deploy.env   # 首次
#   ./scripts/deploy-app.sh              # 默认只构建并推送 app:latest
#   ./scripts/deploy-app.sh app          # 同上
#   ./scripts/deploy-app.sh nestjs       # 协作服务
#   ./scripts/deploy-app.sh all          # app + nestjs
#   ./scripts/deploy-app.sh -t v1.2.0 app
#   ./scripts/deploy-app.sh --deploy app # 推送后在 ECS 上 pull + 重建
#
# 登录:
#   - 未配置 ACR_USERNAME/ACR_PASSWORD 时会交互式 docker login（弹出用户名密码）
#   - 或事先执行: docker login crpi-ewcecvhd15oyzexv.cn-chengdu.personal.cr.aliyuncs.com
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -f "${SCRIPT_DIR}/deploy.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${SCRIPT_DIR}/deploy.env"
  set +a
fi

ACR_REGISTRY="${ACR_REGISTRY:-crpi-ewcecvhd15oyzexv.cn-chengdu.personal.cr.aliyuncs.com/speed-knowledge}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
PLATFORM="${PLATFORM:-linux/amd64}"
ECS_HOST="${ECS_HOST:-}"
ECS_USER="${ECS_USER:-root}"
ECS_PROJECT_DIR="${ECS_PROJECT_DIR:-/opt/speed-knowledge-server}"

DO_PUSH=1
DO_LOGIN=1
DO_DEPLOY=0
SERVICES=()

usage() {
  sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
  echo ""
  echo "选项:"
  echo "  -t, --tag TAG        镜像 tag（默认: latest，或 deploy.env 中 IMAGE_TAG）"
  echo "  -r, --registry REG   ACR 前缀（默认见 deploy.env / 示例 compose）"
  echo "      --platform PLAT  构建平台（默认: linux/amd64）"
  echo "      --no-push        仅构建到本地（单平台时可 --load）"
  echo "      --skip-login     跳过 docker login 检查"
  echo "      --deploy         推送后 SSH 到 ECS 拉取并 force-recreate"
  echo "  -h, --help           显示帮助"
  exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--tag)
      IMAGE_TAG="$2"
      shift 2
      ;;
    -r|--registry)
      ACR_REGISTRY="$2"
      shift 2
      ;;
    --platform)
      PLATFORM="$2"
      shift 2
      ;;
    --no-push)
      DO_PUSH=0
      shift
      ;;
    --skip-login)
      DO_LOGIN=0
      shift
      ;;
    --deploy)
      DO_DEPLOY=1
      shift
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
  SERVICES=(app)
fi

if [[ "${SERVICES[*]}" == *all* ]]; then
  SERVICES=(app nestjs)
fi

acr_host() {
  echo "${ACR_REGISTRY%%/*}"
}

ensure_buildx() {
  if ! docker buildx version >/dev/null 2>&1; then
    echo "ERROR: 需要 Docker buildx" >&2
    exit 1
  fi
  local builder=""
  for candidate in desktop-linux default; do
    if docker buildx inspect "${candidate}" >/dev/null 2>&1; then
      if docker buildx use "${candidate}" 2>/dev/null; then
        builder="${candidate}"
        break
      fi
    fi
  done
  if [[ -z "${builder}" ]]; then
    docker context use default 2>/dev/null || true
    docker buildx use default
    builder="default"
  fi
  echo "使用 buildx builder: ${builder}"
}

ensure_acr_login() {
  [[ "${DO_LOGIN}" -eq 1 ]] || return 0
  local host
  host="$(acr_host)"
  echo ""
  echo "==> ACR 登录检查: ${host}"
  if [[ -n "${ACR_USERNAME:-}" && -n "${ACR_PASSWORD:-}" ]]; then
    echo "${ACR_PASSWORD}" | docker login "${host}" -u "${ACR_USERNAME}" --password-stdin
    return
  fi
  echo "未配置 ACR_USERNAME/ACR_PASSWORD，将打开交互式 docker login。"
  echo "（阿里云: 容器镜像服务 -> 访问凭证 -> 设置固定密码）"
  docker login "${host}"
}

service_context() {
  case "$1" in
    app) echo "${ROOT_DIR}/python-fastapi" ;;
    nestjs) echo "${ROOT_DIR}/nodejs-nestjs" ;;
    *) echo "未知服务: $1" >&2; exit 1 ;;
  esac
}

build_one() {
  local service="$1"
  local context
  context="$(service_context "${service}")"
  local image="${ACR_REGISTRY}/${service}:${IMAGE_TAG}"

  echo ""
  echo "=========================================="
  echo "  构建: ${service}"
  echo "  上下文: ${context}"
  echo "  镜像: ${image}"
  echo "  平台: ${PLATFORM}"
  echo "=========================================="

  local -a build_args=(
    buildx build
    --platform "${PLATFORM}"
    -t "${image}"
  )

  if [[ "${DO_PUSH}" -eq 1 ]]; then
    build_args+=(--push)
  else
    build_args+=(--load)
  fi

  docker "${build_args[@]}" "${context}"

  echo "Done: ${image}"
}

remote_deploy() {
  if [[ -z "${ECS_HOST}" ]]; then
    echo "ERROR: --deploy 需要配置 ECS_HOST（scripts/deploy.env）" >&2
    exit 1
  fi
  local services_csv
  services_csv="$(IFS=,; echo "${SERVICES[*]}")"
  echo ""
  echo "==> SSH 到 ECS 部署: ${ECS_USER}@${ECS_HOST}"
  echo "    服务: ${services_csv}  tag: ${IMAGE_TAG}"
  ssh "${ECS_USER}@${ECS_HOST}" \
    "cd '${ECS_PROJECT_DIR}' && IMAGE_TAG='${IMAGE_TAG}' APP_IMAGE_TAG='${IMAGE_TAG}' NESTJS_IMAGE_TAG='${IMAGE_TAG}' ./scripts/ecs-deploy-app.sh ${SERVICES[*]}"
}

main() {
  echo "ACR: ${ACR_REGISTRY}"
  echo "Tag: ${IMAGE_TAG}"
  echo "Services: ${SERVICES[*]}"
  ensure_buildx
  ensure_acr_login

  for svc in "${SERVICES[@]}"; do
    build_one "${svc}"
  done

  if [[ "${DO_DEPLOY}" -eq 1 ]]; then
    remote_deploy
  else
    echo ""
    echo "推送完成。ECS 上手动更新:"
    echo "  ssh ${ECS_USER:-root}@${ECS_HOST:-<ECS_IP>} 'cd ${ECS_PROJECT_DIR} && ./scripts/ecs-deploy-app.sh ${SERVICES[*]}'"
    echo "或本地: ./scripts/deploy-app.sh --deploy ${SERVICES[*]}"
  fi
}

main
