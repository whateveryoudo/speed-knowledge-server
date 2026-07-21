#!/usr/bin/env bash
# 对比 .env.example 与 .env 的「键名」，不比 value
#
# 用法:
#   ./scripts/check-env-keys.sh
#   ./scripts/check-env-keys.sh path/to/.env.example path/to/.env
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

extract_keys() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    echo "ERROR: 文件不存在: $file" >&2
    return 1
  fi
  grep -E '^[A-Za-z_][A-Za-z0-9_]*=' "$file" | cut -d= -f1 | sort -u
}

check_pair() {
  local example="$1"
  local env_file="$2"
  local label="$3"

  echo "==> 检查 ${label}"
  echo "    example: ${example}"
  echo "    env:     ${env_file}"

  if [[ ! -f "$env_file" ]]; then
    echo "ERROR: 缺少 ${env_file}，请从 example 复制并填写生产值" >&2
    return 1
  fi

  local missing
  missing=$(comm -23 \
    <(extract_keys "$example") \
    <(extract_keys "$env_file") \
  ) || true

  if [[ -n "$missing" ]]; then
    echo "ERROR: ${label} 缺少以下配置项（example 有、.env 没有）：" >&2
    echo "$missing" | sed 's/^/  - /' >&2
    return 1
  fi

  echo "OK: ${label} 键齐全"
}

main() {
  local failed=0

  if [[ $# -eq 2 ]]; then
    check_pair "$1" "$2" "custom" || failed=1
  else
    check_pair "${ROOT}/.env.example" "${ROOT}/.env" "compose 根 .env" || failed=1
    echo ""
    check_pair \
      "${ROOT}/python-fastapi/.env.example" \
      "${ROOT}/python-fastapi/.env" \
      "python-fastapi/.env" || failed=1
    echo ""
    check_pair \
      "${ROOT}/nodejs-nestjs/.env.example" \
      "${ROOT}/nodejs-nestjs/.env" \
      "nodejs-nestjs/.env" || failed=1
  fi

  if [[ $failed -ne 0 ]]; then
    echo ""
    echo "请补全上述键后再部署（值可保持生产配置，不必与 example 相同）" >&2
    exit 1
  fi

  echo ""
  echo "全部 env 键检查通过"
}

main "$@"
