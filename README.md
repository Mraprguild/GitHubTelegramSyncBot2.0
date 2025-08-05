# GitHub-Telegram Sync Bot

A comprehensive Python bot that bridges GitHub repositories with Telegram messaging, providing real-time notifications for GitHub events and interactive repository management through Telegram commands.

## 🚀 Features

### Core Functionality
- **Real-time GitHub Notifications**: Push events, issues, pull requests, and releases
- **Interactive Telegram Commands**: Repository management through chat interface
- **Web Management Dashboard**: Monitor bot status and webhook activity
- **Webhook Support**: Secure GitHub webhook handling with HMAC verification
- **Rate Limiting**: Configurable request limits to prevent abuse

### Telegram Commands
- `/start` - Initialize bot and show welcome message
- `/help` - Display available commands and usage
- `/profile [username]` - Get GitHub user profile information
- `/repos [username]` - List user's public repositories
- `/repo <owner/repo>` - Get detailed repository information
- `/commits <owner/repo>` - Show recent commits from repository
- `/issues <owner/repo>` - List open issues in repository
- `/search <query>` - Search GitHub repositories

### Security Features
- GitHub webhook signature verification (HMAC-SHA256)
- Telegram chat ID whitelisting
- Rate limiting per chat
- Secure token management through environment variables

## 📋 Requirements

### System Requirements
- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- Internet connection for GitHub and Telegram APIs

### API Keys and Tokens
You'll need to obtain the following credentials:

1. **Telegram Bot Token**
   - Create a new bot via [@BotFather](https://t.me/BotFather)
   - Use `/newbot` command and follow instructions
   - Save the provided token

2. **GitHub Personal Access Token**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate new token with `repo` and `read:user` scopes
   - Save the token securely

3. **GitHub Username**
   - Your GitHub username for default repository operations

## 🐳 Docker Deployment

### Quick Start with Docker Compose

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd github-telegram-bot
   ```

2. **Create Environment File**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   GITHUB_TOKEN=your_github_personal_access_token_here
   GITHUB_USERNAME=your_github_username_here
   GITHUB_WEBHOOK_SECRET=optional_webhook_secret
   ALLOWED_CHAT_IDS=comma_separated_chat_ids (optional)
   ```

3. **Build and Run**
   ```bash
   docker-compose up -d
   ```

4. **Access the Application**
   - Web Dashboard: http://localhost:5000
   - Telegram Bot Status: http://localhost:5000/telegram-status
   - Webhook Endpoint: http://localhost:8000/webhook

### Individual Docker Commands

```bash
# Build the image
docker build -t github-telegram-bot .

# Run the container
docker run -d \
  --name github-telegram-bot \
  -p 5000:5000 \
  -p 8000:8000 \
  --env-file .env \
  github-telegram-bot
```

## 🔧 Local Development

### Installation

1. **Install Dependencies**
   ```bash
   pip install python-telegram-bot requests flask python-dotenv
   ```

2. **Set Environment Variables**
   ```bash
   export TELEGRAM_BOT_TOKEN="your_token_here"
   export GITHUB_TOKEN="your_token_here"
   export GITHUB_USERNAME="your_username_here"
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```

## 🌐 GitHub Webhook Setup

For production deployment with webhook support:

1. **Configure Webhook in GitHub Repository**
   - Go to Repository Settings → Webhooks
   - Add webhook URL: `https://yourdomain.com:8000/webhook`
   - Content type: `application/json`
   - Secret: Set the same value as `GITHUB_WEBHOOK_SECRET`
   - Events: Push, Issues, Pull requests, Releases

2. **SSL Certificate Required**
   - GitHub requires HTTPS for webhook delivery
   - Use reverse proxy (nginx) or SSL termination

## 📊 Web Interface

### Available Endpoints
- `/` - Main dashboard
- `/status` - Bot status and metrics
- `/telegram-status` - Enhanced Telegram bot monitoring
- `/health` - Health check endpoint
- `/webhook` - GitHub webhook receiver (POST)

### Monitoring Features
- Real-time bot status
- Command usage statistics
- System resource monitoring
- GitHub API quota tracking
- Live activity feed

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from BotFather | - |
| `GITHUB_TOKEN` | Yes | GitHub personal access token | - |
| `GITHUB_USERNAME` | Yes | GitHub username | - |
| `GITHUB_WEBHOOK_SECRET` | No | Secret for webhook verification | - |
| `ALLOWED_CHAT_IDS` | No | Comma-separated chat IDs | All allowed |
| `WEBHOOK_HOST` | No | Webhook server host | 0.0.0.0 |
| `WEBHOOK_PORT` | No | Webhook server port | 8000 |
| `WEB_HOST` | No | Web interface host | 0.0.0.0 |
| `WEB_PORT` | No | Web interface port | 5000 |
| `DEBUG_MODE` | No | Enable debug logging | false |
| `RATE_LIMIT_REQUESTS` | No | Requests per time window | 10 |
| `RATE_LIMIT_WINDOW` | No | Rate limit window (seconds) | 60 |

### Notification Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `NOTIFY_ON_PUSH` | Send notifications for push events | true |
| `NOTIFY_ON_ISSUES` | Send notifications for issue events | true |
| `NOTIFY_ON_PULL_REQUESTS` | Send notifications for PR events | true |
| `NOTIFY_ON_RELEASES` | Send notifications for release events | true |

## 🔍 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check Telegram bot token validity
   - Verify bot is added to chat/group
   - Check network connectivity

2. **GitHub API errors**
   - Verify GitHub token has required permissions
   - Check API rate limits (5000 requests/hour)
   - Ensure repository access

3. **Webhook not receiving events**
   - Verify webhook URL is accessible from internet
   - Check webhook secret configuration
   - Ensure HTTPS for production

### Logs and Debugging

```bash
# View container logs
docker-compose logs -f

# Check specific service logs
docker-compose logs webhook-handler
docker-compose logs telegram-bot

# Enable debug mode
export DEBUG_MODE=true
```

## 🚀 Production Deployment

### Recommended Architecture
- Use reverse proxy (nginx) for SSL termination
- Set up log rotation for application logs
- Monitor resource usage and GitHub API quotas
- Implement backup for configuration

### Security Checklist
- [ ] Enable webhook secret verification
- [ ] Restrict allowed chat IDs
- [ ] Use HTTPS for all external endpoints
- [ ] Regular token rotation
- [ ] Monitor access logs

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📞 Support

For issues and questions:
- Check troubleshooting section
- Review logs for error details
- Open GitHub issue with detailed description