"""
Flask web interface for bot management and monitoring.
"""

import logging
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class WebInterface:
    """Web interface for bot management."""
    
    def __init__(self, config, telegram_bot):
        """
        Initialize web interface.
        
        Args:
            config: Configuration object
            telegram_bot: TelegramBot instance
        """
        self.config = config
        self.telegram_bot = telegram_bot
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes for web interface."""
        
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/status')
        def status():
            return render_template('bot_status.html')
        
        @self.app.route('/telegram-status')
        def telegram_status():
            return render_template('telegram_status.html')
        
        @self.app.route('/api/status')
        def api_status():
            return jsonify(self.get_bot_status())
        
        @self.app.route('/api/config')
        def api_config():
            return jsonify(self.get_config_info())
        
        @self.app.route('/health')
        def health_check():
            return jsonify({'status': 'healthy', 'service': 'web_interface'})
    
    def get_bot_status(self):
        """Get current bot status information."""
        try:
            # Get GitHub API rate limit
            rate_limit_info = self.telegram_bot.github_client.get_rate_limit()
            
            status_data = {
                'bot_running': self.telegram_bot.running,
                'timestamp': datetime.now().isoformat(),
                'github_api': {
                    'connected': bool(rate_limit_info),
                    'rate_limit': rate_limit_info.get('rate', {}) if rate_limit_info else None
                },
                'configuration': {
                    'github_username': self.config.github_username,
                    'allowed_chats': len(self.config.allowed_chat_ids),
                    'rate_limit': f"{self.config.rate_limit_requests}/{self.config.rate_limit_window}s",
                    'notifications': {
                        'push': self.config.notify_on_push,
                        'issues': self.config.notify_on_issues,
                        'pull_requests': self.config.notify_on_pull_requests,
                        'releases': self.config.notify_on_releases
                    }
                }
            }
            
            return status_data
            
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            return {
                'error': 'Failed to get bot status',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_config_info(self):
        """Get configuration information (sanitized)."""
        return {
            'github_username': self.config.github_username,
            'webhook_url': self.config.get_webhook_url(),
            'allowed_chats_count': len(self.config.allowed_chat_ids),
            'rate_limiting': {
                'requests': self.config.rate_limit_requests,
                'window': self.config.rate_limit_window
            },
            'notifications': {
                'push': self.config.notify_on_push,
                'issues': self.config.notify_on_issues,
                'pull_requests': self.config.notify_on_pull_requests,
                'releases': self.config.notify_on_releases
            }
        }
    
    def run_server(self):
        """Run the web interface server."""
        try:
            logger.info(f"Starting web interface on {self.config.web_host}:{self.config.web_port}")
            self.app.run(
                host=self.config.web_host,
                port=self.config.web_port,
                debug=self.config.debug_mode
            )
        except Exception as e:
            logger.error(f"Error running web interface: {e}")
            raise
