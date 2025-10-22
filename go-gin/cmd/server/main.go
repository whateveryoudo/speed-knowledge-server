package main

import (
	"log"

	"github.com/yourusername/go-gin-api/internal/config"
	"github.com/yourusername/go-gin-api/internal/database"
	"github.com/yourusername/go-gin-api/internal/router"
)

// @title           Gin API Server
// @version         1.0
// @description     This is a sample server using Gin framework.
// @termsOfService  http://swagger.io/terms/

// @contact.name   API Support
// @contact.url    http://www.example.com/support
// @contact.email  support@example.com

// @license.name  MIT
// @license.url   https://opensource.org/licenses/MIT

// @host      localhost:8080
// @BasePath  /api/v1

// @securityDefinitions.apikey BearerAuth
// @in header
// @name Authorization
// @description Type "Bearer" followed by a space and JWT token.

func main() {
	// 加载配置
	cfg := config.Load()

	// 初始化数据库
	db := database.Init(cfg)

	// 自动迁移
	database.AutoMigrate(db)

	// 初始化路由
	r := router.SetupRouter(db, cfg)

	// 启动服务器
	log.Printf("🚀 Server is running on http://localhost:%s", cfg.Port)
	log.Printf("📚 API Documentation: http://localhost:%s/swagger/index.html", cfg.Port)
	
	if err := r.Run(":" + cfg.Port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

