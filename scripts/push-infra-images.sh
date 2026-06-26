#!/usr/bin/env bash
# Mac 上执行：用 buildx 将基础镜像以 linux/amd64 推到 ACR
#
# 说明:
#   - acr-pusher 容器 builder 往往连不上 docker.io，改用 Docker Desktop 默认 builder
#   - 默认走 DaoCloud 镜像: docker.m.daocloud.io/library/...
#   - 可覆盖: DOCKER_HUB_MIRROR="" 走 docker.io（需 VPN）
#
# 用法:
#   docker login crpi-ewcecvhd15oyzexv.cn-chengdu.personal.cr.aliyuncs.com
#   ./scripts/push-infra-images.sh mysql redis nginx
set -euo pipefail

ACR="crpi-ewcecvhd15oyzexv.cn-chengdu.personal.cr.aliyuncs.com/speed-knowledge"
PLATFORM="linux/amd64"
# 国内 Mac 默认镜像；留空则使用 docker.io/library
DOCKER_HUB_MIRROR="${DOCKER_HUB_MIRROR:-docker.m.daocloud.io/library}"

declare -A IMAGES=(
  ["mysql-8.4.5"]="mysql:8.4.5"
  ["redis-7-alpine"]="redis:7-alpine"
  ["nginx-1.27-alpine"]="nginx:1.27-alpine"
  ["rabbitmq-3-management-alpine"]="rabbitmq:3-management-alpine"
)

declare -A ALIASES=(
  ["mysql"]="mysql-8.4.5"
  ["redis"]="redis-7-alpine"
  ["nginx"]="nginx-1.27-alpine"
  ["rabbitmq"]="rabbitmq-3-management-alpine"
)

hub_image_ref() {
  local name_tag="$1"
  if [[ -n "${DOCKER_HUB_MIRROR}" ]]; then
    echo "${DOCKER_HUB_MIRROR}/${name_tag}"
  else
    echo "docker.io/library/${name_tag}"
  fi
}

ensure_buildx() {
  if ! docker buildx version >/dev/null 2>&1; then
    echo "ERROR: 需要 Docker buildx"
    exit 1
  fi
  # Docker Desktop 常见 builder 名是 desktop-linux；default 需先切 context
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

push_one() {
  local repo="$1"
  local name_tag="${IMAGES[$repo]}"
  local hub_src
  hub_src="$(hub_image_ref "${name_tag}")"
  local dest="${ACR}/${repo}:latest"
  local tmpdir
  tmpdir="$(mktemp -d)"

  echo ""
  echo "=========================================="
  echo "  ${hub_src}"
  echo "  -> ${dest}"
  echo "  platform: ${PLATFORM}"
  echo "=========================================="

  echo "预拉取到本机（走 Docker Desktop 网络/镜像）..."
  docker pull --platform "${PLATFORM}" "${hub_src}"

  cat > "${tmpdir}/Dockerfile" <<EOF
FROM ${hub_src}
LABEL org.opencontainers.image.source="${hub_src}"
EOF

  docker buildx build \
    --platform "${PLATFORM}" \
    -t "${dest}" \
    --push \
    "${tmpdir}"

  rm -rf "${tmpdir}"

  if docker buildx imagetools inspect "${dest}" --format '{{.Manifest.Platform.Architecture}}' 2>/dev/null | grep -qx 'amd64'; then
    echo "OK: ACR 上镜像架构 = amd64"
  else
    echo "WARN: 未能远程校验，请在 ECS compose up 时确认无 arm64 警告"
  fi
  echo "Done: ${dest}"
}

resolve_targets() {
  if [[ $# -eq 0 ]]; then
    printf '%s\n' "${!IMAGES[@]}"
    return
  fi
  for arg in "$@"; do
    if [[ -n "${IMAGES[$arg]:-}" ]]; then
      echo "$arg"
    elif [[ -n "${ALIASES[$arg]:-}" ]]; then
      echo "${ALIASES[$arg]}"
    else
      echo "未知目标: ${arg}（可选: mysql redis nginx rabbitmq）" >&2
      exit 1
    fi
  done
}

main() {
  echo "ACR: ${ACR}"
  echo "Hub mirror: ${DOCKER_HUB_MIRROR:-docker.io/library}"
  echo "buildx + ${PLATFORM} push"
  ensure_buildx

  local targets=()
  while IFS= read -r line; do
    [[ -n "$line" ]] && targets+=("$line")
  done < <(resolve_targets "$@")

  for repo in "${targets[@]}"; do
    push_one "$repo"
  done

  echo ""
  echo "全部完成。ECS 上执行:"
  echo "  cd /opt/speed-knowledge-server"
  echo "  ./scripts/ecs-recreate-infra.sh"
}

main "$@"
