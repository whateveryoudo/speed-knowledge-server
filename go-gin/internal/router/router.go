package router

import (
	"net/http"

	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
	"github.com/yourusername/go-gin-api/internal/config"
	"github.com/yourusername/go-gin-api/internal/handlers"
	"github.com/yourusername/go-gin-api/internal/middleware"
	"gorm.io/gorm"

	_ "github.com/yourusername/go-gin-api/docs" // Import generated docs
)

// SetupRouter sets up the Gin router
func SetupRouter(db *gorm.DB, cfg *config.Config) *gin.Engine {
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.Default()

	// Middleware
	r.Use(middleware.CORSMiddleware(cfg))

	// Health check
	r.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message":     "Welcome to " + cfg.AppName + "!",
			"docs":        "/swagger/index.html",
			"environment": cfg.Environment,
		})
	})

	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	// Swagger documentation
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	// API v1 routes
	v1 := r.Group("/api/v1")
	{
		// Auth routes (no authentication required)
		authHandler := handlers.NewAuthHandler(db, cfg)
		auth := v1.Group("/auth")
		{
			auth.POST("/login", authHandler.Login)
		}

		// User routes
		userHandler := handlers.NewUserHandler(db)
		users := v1.Group("/users")
		{
			users.POST("", userHandler.CreateUser)
			
			// Protected routes
			users.Use(middleware.AuthMiddleware(cfg))
			users.GET("", userHandler.GetUsers)
			users.GET("/:id", userHandler.GetUser)
			users.PATCH("/:id", userHandler.UpdateUser)
			users.DELETE("/:id", userHandler.DeleteUser)
		}
	}

	return r
}

