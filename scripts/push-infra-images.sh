#!/usr/bin/env bash
# Mac 上执行：将基础镜像 push 到 ACR（需先 docker login）
set -euo pipefail

ACR="crpi-ewcecvhd15oyzexv.cn-chengdu.personal.cr.aliyuncs.com/speed-knowledge"

declare -A IMAGES=(
  ["mysql-8.4.5"]="mysql:8.4.5"
  ["redis-7-alpine"]="redis:7-alpine"
  ["nginx-1.27-alpine"]="nginx:1.27-alpine"
  ["rabbitmq-3-management-alpine"]="rabbitmq:3-management-alpine"
)

for repo in "${!IMAGES[@]}"; do
  src="${IMAGES[$repo]}"
  echo "==> $src -> $ACR/$repo:latest"
  docker pull --platform linux/amd64 "$src"
  docker tag "$src" "$ACR/$repo:latest"
  docker push "$ACR/$repo:latest"
done

echo "Done. app / nestjs 请单独 build push。"
