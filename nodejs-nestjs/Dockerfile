# 多阶段构建
# ECS 为 linux/amd64；Mac 上请用 scripts/deploy-app.sh nestjs（buildx --platform linux/amd64）
ARG NODE_IMAGE=docker.m.daocloud.io/library/node:20-alpine
ARG NPM_REGISTRY=https://registry.npmmirror.com

FROM ${NODE_IMAGE} AS builder

WORKDIR /app

COPY package.json pnpm-lock.yaml ./

RUN npm config set registry "${NPM_REGISTRY}" \
  && npm install -g pnpm@9.15.0 \
  && pnpm config set registry "${NPM_REGISTRY}"

# 构建阶段不需要运行 native install 脚本（bcrypt 在生产阶段编译）
RUN pnpm install --frozen-lockfile --ignore-scripts

COPY . .

RUN pnpm run build

# 生产阶段在本镜像平台安装依赖并编译 bcrypt，避免跨架构拷贝 node_modules
FROM ${NODE_IMAGE}

ARG NPM_REGISTRY=https://registry.npmmirror.com

WORKDIR /app

RUN apk add --no-cache python3 make g++ \
  && npm config set registry "${NPM_REGISTRY}" \
  && npm install -g pnpm@9.15.0 \
  && pnpm config set registry "${NPM_REGISTRY}"

COPY package.json pnpm-lock.yaml ./

ENV npm_config_build_from_source=true
RUN pnpm install --frozen-lockfile --prod \
  && pnpm rebuild bcrypt \
  && apk del python3 make g++

RUN addgroup -g 1001 -S nodejs && adduser -S nestjs -u 1001 \
  && chown -R nestjs:nodejs /app

COPY --from=builder --chown=nestjs:nodejs /app/dist ./dist

USER nestjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["node", "dist/main"]
