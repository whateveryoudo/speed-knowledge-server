# 多阶段构建
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY pnpm-lock.yaml* ./

# bcrypt 等 native 模块需要编译工具（仅 builder 阶段，不会进入最终镜像）
RUN apk add --no-cache python3 make g++

RUN corepack enable && corepack prepare pnpm@9.15.0 --activate
RUN pnpm install --frozen-lockfile

COPY . .

RUN pnpm run build
RUN pnpm prune --prod

# 生产阶段
FROM node:20-alpine

WORKDIR /app

RUN addgroup -g 1001 -S nodejs && adduser -S nestjs -u 1001

COPY --from=builder --chown=nestjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nestjs:nodejs /app/dist ./dist
COPY --chown=nestjs:nodejs package.json ./

USER nestjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["node", "dist/main"]
