package dto

import "time"

// CreateUserRequest represents the request to create a user
type CreateUserRequest struct {
	Email    string `json:"email" binding:"required,email" example:"user@example.com"`
	Password string `json:"password" binding:"required,min=6" example:"password123"`
	Name     string `json:"name" binding:"required,min=1" example:"John Doe"`
}

// UpdateUserRequest represents the request to update a user
type UpdateUserRequest struct {
	Email    string `json:"email" binding:"omitempty,email" example:"user@example.com"`
	Password string `json:"password" binding:"omitempty,min=6" example:"password123"`
	Name     string `json:"name" binding:"omitempty,min=1" example:"John Doe"`
}

// UserResponse represents a user response
type UserResponse struct {
	ID        uint      `json:"id" example:"1"`
	Email     string    `json:"email" example:"user@example.com"`
	Name      string    `json:"name" example:"John Doe"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// LoginRequest represents a login request
type LoginRequest struct {
	Email    string `json:"email" binding:"required,email" example:"user@example.com"`
	Password string `json:"password" binding:"required" example:"password123"`
}

// LoginResponse represents a login response
type LoginResponse struct {
	AccessToken string       `json:"access_token"`
	TokenType   string       `json:"token_type" example:"bearer"`
	User        UserResponse `json:"user"`
}

