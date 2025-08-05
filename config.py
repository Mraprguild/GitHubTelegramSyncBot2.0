"""
Configuration management for the GitHub-Telegram Sync Bot.
Handles environment variables and validation.
"""

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Config:
    """Configuration class for the bot."""
    
    def __init__(self):
        """Initialize configuration by loading environment variables."""
        load_dotenv()
        
        # Telegram Bot Configuration
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.allowed_chat_ids = self._parse_chat_ids(os.getenv('ALLOWED_CHAT_IDS', ''))
        
        # GitHub Configuration
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.github_username = os.getenv('GITHUB_USERNAME', '')
        self.github_webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET', '')
        
        # Server Configuration
        self.webhook_host = os.getenv('WEBHOOK_HOST', '0.0.0.0')
        self.webhook_port = int(os.getenv('WEBHOOK_PORT', '8000'))
        self.web_host = os.getenv('WEB_HOST', '0.0.0.0')
        self.web_port = int(os.getenv('WEB_PORT', '5000'))
        
        # Bot Configuration
        self.debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        self.rate_limit_requests = int(os.getenv('RATE_LIMIT_REQUESTS', '10'))
        self.rate_limit_window = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
        
        # Notification Settings
        self.notify_on_push = os.getenv('NOTIFY_ON_PUSH', 'True').lower() == 'true'
        self.notify_on_issues = os.getenv('NOTIFY_ON_ISSUES', 'True').lower() == 'true'
        self.notify_on_pull_requests = os.getenv('NOTIFY_ON_PULL_REQUESTS', 'True').lower() == 'true'
        self.notify_on_releases = os.getenv('NOTIFY_ON_RELEASES', 'True').lower() == 'true'
        
    def _parse_chat_ids(self, chat_ids_str):
        """Parse comma-separated chat IDs."""
        if not chat_ids_str:
            return []
        try:
            return [int(chat_id.strip()) for chat_id in chat_ids_str.split(',') if chat_id.strip()]
        except ValueError:
            logger.warning("Invalid chat IDs format in ALLOWED_CHAT_IDS")
            return []
    
    def validate(self):
        """Validate required configuration parameters."""
        errors = []
        
        if not self.telegram_token:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        
        if not self.github_token:
            errors.append("GITHUB_TOKEN is required")
            
        if not self.github_username:
            errors.append("GITHUB_USERNAME is required")
        
        if errors:
            error_msg = "Configuration errors:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Configuration validated successfully")
    
    def is_chat_allowed(self, chat_id):
        """Check if a chat ID is allowed to use the bot."""
        if not self.allowed_chat_ids:
            return True  # Allow all if no restriction is set
        return chat_id in self.allowed_chat_ids
    
    def get_webhook_url(self):
        """Get the webhook URL for GitHub."""
        return f"http://{self.webhook_host}:{self.webhook_port}/webhook"
