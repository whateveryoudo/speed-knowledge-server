package services

import (
	"errors"
	"time"

	"github.com/yourusername/go-gin-api/internal/config"
	"github.com/yourusername/go-gin-api/internal/dto"
	"github.com/yourusername/go-gin-api/pkg/utils"
	"gorm.io/gorm"
)

// AuthService handles authentication business logic
type AuthService struct {
	db          *gorm.DB
	cfg         *config.Config
	userService *UserService
}

// NewAuthService creates a new AuthService
func NewAuthService(db *gorm.DB, cfg *config.Config) *AuthService {
	return &AuthService{
		db:          db,
		cfg:         cfg,
		userService: NewUserService(db),
	}
}

// Login authenticates a user and returns a token
func (s *AuthService) Login(req *dto.LoginRequest) (*dto.LoginResponse, error) {
	// Find user by email
	user, err := s.userService.GetByEmail(req.Email)
	if err != nil {
		return nil, errors.New("invalid credentials")
	}

	// Verify password
	if !utils.CheckPasswordHash(req.Password, user.Password) {
		return nil, errors.New("invalid credentials")
	}

	// Parse token expiration duration
	expiresIn, err := time.ParseDuration(s.cfg.JWTExpiresIn)
	if err != nil {
		expiresIn = 168 * time.Hour // Default to 7 days
	}

	// Generate JWT token
	token, err := utils.GenerateToken(user.ID, s.cfg.JWTSecret, expiresIn)
	if err != nil {
		return nil, err
	}

	return &dto.LoginResponse{
		AccessToken: token,
		TokenType:   "bearer",
		User: dto.UserResponse{
			ID:        user.ID,
			Email:     user.Email,
			Name:      user.Name,
			CreatedAt: user.CreatedAt,
			UpdatedAt: user.UpdatedAt,
		},
	}, nil
}

