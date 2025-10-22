.PHONY: help run build test clean swag docker-build docker-up docker-down

help: ## 显示帮助信息
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

run: ## 运行应用
	go run cmd/server/main.go

build: ## 编译应用
	go build -o bin/server cmd/server/main.go

test: ## 运行测试
	go test -v ./...

clean: ## 清理编译产物
	rm -rf bin/
	rm -rf tmp/

swag: ## 生成 Swagger 文档
	swag init -g cmd/server/main.go -o docs

install: ## 安装依赖
	go mod download
	go mod tidy

lint: ## 运行代码检查
	golangci-lint run

format: ## 格式化代码
	gofmt -s -w .
	goimports -w .

docker-build: ## 构建 Docker 镜像
	docker build -t go-gin-api .

docker-up: ## 启动 Docker 容器
	docker-compose up -d

docker-down: ## 停止 Docker 容器
	docker-compose down

docker-logs: ## 查看 Docker 日志
	docker-compose logs -f

air: ## 使用 Air 热重载运行
	air

