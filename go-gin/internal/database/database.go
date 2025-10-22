package database

import (
	"fmt"
	"log"

	"github.com/yourusername/go-gin-api/internal/config"
	"github.com/yourusername/go-gin-api/internal/models"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// Init initializes database connection
func Init(cfg *config.Config) *gorm.DB {
	dsn := fmt.Sprintf(
		"host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		cfg.DBHost,
		cfg.DBPort,
		cfg.DBUser,
		cfg.DBPassword,
		cfg.DBName,
		cfg.DBSSLMode,
	)

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	log.Println("✅ Database connection established")
	return db
}

// AutoMigrate runs auto migration for database models
func AutoMigrate(db *gorm.DB) {
	if err := db.AutoMigrate(
		&models.User{},
	); err != nil {
		log.Fatalf("Failed to migrate database: %v", err)
	}
	log.Println("✅ Database migration completed")
}

