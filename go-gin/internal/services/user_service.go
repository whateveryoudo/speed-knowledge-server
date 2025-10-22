package services

import (
	"errors"

	"github.com/yourusername/go-gin-api/internal/dto"
	"github.com/yourusername/go-gin-api/internal/models"
	"github.com/yourusername/go-gin-api/pkg/utils"
	"gorm.io/gorm"
)

// UserService handles user business logic
type UserService struct {
	db *gorm.DB
}

// NewUserService creates a new UserService
func NewUserService(db *gorm.DB) *UserService {
	return &UserService{db: db}
}

// Create creates a new user
func (s *UserService) Create(req *dto.CreateUserRequest) (*dto.UserResponse, error) {
	// Check if email already exists
	var existingUser models.User
	if err := s.db.Where("email = ?", req.Email).First(&existingUser).Error; err == nil {
		return nil, errors.New("email already exists")
	}

	// Hash password
	hashedPassword, err := utils.HashPassword(req.Password)
	if err != nil {
		return nil, err
	}

	user := models.User{
		Email:    req.Email,
		Password: hashedPassword,
		Name:     req.Name,
	}

	if err := s.db.Create(&user).Error; err != nil {
		return nil, err
	}

	return s.toUserResponse(&user), nil
}

// GetAll returns all users
func (s *UserService) GetAll() ([]dto.UserResponse, error) {
	var users []models.User
	if err := s.db.Find(&users).Error; err != nil {
		return nil, err
	}

	responses := make([]dto.UserResponse, len(users))
	for i, user := range users {
		responses[i] = *s.toUserResponse(&user)
	}

	return responses, nil
}

// GetByID returns a user by ID
func (s *UserService) GetByID(id uint) (*dto.UserResponse, error) {
	var user models.User
	if err := s.db.First(&user, id).Error; err != nil {
		return nil, err
	}

	return s.toUserResponse(&user), nil
}

// GetByEmail returns a user by email
func (s *UserService) GetByEmail(email string) (*models.User, error) {
	var user models.User
	if err := s.db.Where("email = ?", email).First(&user).Error; err != nil {
		return nil, err
	}

	return &user, nil
}

// Update updates a user
func (s *UserService) Update(id uint, req *dto.UpdateUserRequest) (*dto.UserResponse, error) {
	var user models.User
	if err := s.db.First(&user, id).Error; err != nil {
		return nil, err
	}

	if req.Email != "" {
		user.Email = req.Email
	}
	if req.Name != "" {
		user.Name = req.Name
	}
	if req.Password != "" {
		hashedPassword, err := utils.HashPassword(req.Password)
		if err != nil {
			return nil, err
		}
		user.Password = hashedPassword
	}

	if err := s.db.Save(&user).Error; err != nil {
		return nil, err
	}

	return s.toUserResponse(&user), nil
}

// Delete deletes a user
func (s *UserService) Delete(id uint) error {
	result := s.db.Delete(&models.User{}, id)
	if result.Error != nil {
		return result.Error
	}
	if result.RowsAffected == 0 {
		return errors.New("user not found")
	}
	return nil
}

func (s *UserService) toUserResponse(user *models.User) *dto.UserResponse {
	return &dto.UserResponse{
		ID:        user.ID,
		Email:     user.Email,
		Name:      user.Name,
		CreatedAt: user.CreatedAt,
		UpdatedAt: user.UpdatedAt,
	}
}

