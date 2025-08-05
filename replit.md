# Overview

The GitHub-Telegram Sync Bot is a Python-based integration service that bridges GitHub repositories with Telegram messaging. It provides real-time notifications for GitHub events (pushes, issues, PRs, releases) and offers interactive Telegram bot commands for repository management and monitoring. The system includes a web management interface for monitoring bot status and configuration.

# User Preferences

Preferred communication style: Simple, everyday language.

## Recent Updates (August 2025)
- Enhanced Telegram bot welcome and help messages with detailed, professional formatting
- Added comprehensive Docker deployment configuration
- Created advanced Telegram bot status dashboard with real-time monitoring
- Implemented complete command reference with practical examples and usage tips

# System Architecture

## Application Structure
The bot follows a modular architecture with separate components for different responsibilities:

- **Main Application**: Entry point (`main.py`) that orchestrates all components
- **Telegram Bot**: Handles user commands and interactions via Telegram API
- **Webhook Handler**: Processes GitHub webhook events and forwards notifications
- **Web Interface**: Flask-based dashboard for monitoring and management
- **GitHub Client**: API wrapper for GitHub repository operations
- **Configuration**: Centralized environment-based configuration management

## Bot Framework
Uses the python-telegram-bot library for Telegram integration, providing:
- Asynchronous command handling
- Rate limiting protection (configurable requests per time window)
- Chat ID whitelisting for security
- Markdown formatting for rich message display

## Security Model
Implements multiple security layers:
- GitHub webhook signature verification using HMAC-SHA256
- Telegram chat ID whitelisting
- Rate limiting per chat to prevent abuse
- Secure token management through environment variables

## Threading Architecture
Uses Python threading to run concurrent services:
- Main thread for Telegram bot polling
- Separate thread for Flask webhook server
- Separate thread for web management interface
- Signal handlers for graceful shutdown coordination

## Error Handling
Comprehensive error handling with:
- Structured logging to both console and file
- Graceful degradation when GitHub API is unavailable
- User-friendly error messages in Telegram
- Health check endpoints for monitoring

## Message Processing
The bot processes two types of interactions:
- **User Commands**: Interactive commands through Telegram chat
- **Webhook Events**: Automated notifications from GitHub repositories

# External Dependencies

## GitHub Integration
- **GitHub REST API v3**: For fetching repository data, user profiles, commits, issues
- **GitHub Webhooks**: For real-time event notifications (push, issues, PRs, releases)
- **Authentication**: GitHub Personal Access Token for API access
- **Webhook Security**: HMAC-SHA256 signature verification

## Telegram Platform
- **Telegram Bot API**: For sending/receiving messages and commands
- **Bot Token**: Authentication via Telegram BotFather
- **Message Formatting**: MarkdownV2 support for rich text formatting

## Web Technologies
- **Flask**: Lightweight web framework for webhook handling and management interface
- **Bootstrap 5**: Frontend styling and responsive design
- **Chart.js**: Real-time monitoring dashboards and visualizations
- **Font Awesome**: Icon library for UI elements

## Python Libraries
- **python-telegram-bot**: Telegram Bot API wrapper
- **requests**: HTTP client for GitHub API calls
- **flask**: Web framework for webhooks and dashboard
- **python-dotenv**: Environment variable management
- **hmac/hashlib**: Cryptographic functions for webhook verification

## Infrastructure Requirements
- **HTTPS Domain**: Required for GitHub webhook delivery (production)
- **Port Configuration**: Separate ports for webhook handler and web interface
- **Environment Variables**: Configuration through .env file or system environment
- **File System**: Local logging and temporary file storage