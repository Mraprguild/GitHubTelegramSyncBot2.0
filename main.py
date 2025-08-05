#!/usr/bin/env python3
"""
Main entry point for the GitHub-Telegram Sync Bot.
Starts both the Telegram bot and the Flask webhook server.
"""

import logging
import threading
import time
import os
from config import Config
from telegram_bot import TelegramBot
from webhook_handler import WebhookHandler
from web_interface import WebInterface

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the bot and webhook server."""
    try:
        # Initialize configuration
        config = Config()
        config.validate()
        
        logger.info("Starting GitHub-Telegram Sync Bot...")
        
        # Initialize Telegram bot
        telegram_bot = TelegramBot(config)
        
        # Initialize webhook handler
        webhook_handler = WebhookHandler(config, telegram_bot)
        
        # Initialize web interface
        web_interface = WebInterface(config, telegram_bot)
        
        # Start Flask web server in a separate thread
        web_thread = threading.Thread(
            target=web_interface.run_server,
            daemon=True
        )
        web_thread.start()
        
        # Give the web server time to start
        time.sleep(2)
        logger.info("Web interface started on http://0.0.0.0:5000")
        
        # Start Telegram bot webhook handler in a separate thread
        webhook_thread = threading.Thread(
            target=webhook_handler.run_server,
            daemon=True
        )
        webhook_thread.start()
        
        # Give the webhook server time to start
        time.sleep(2)
        logger.info("Webhook handler started on port 8000")
        
        logger.info("Starting Telegram bot polling...")
        # Start the Telegram bot (this will block)
        telegram_bot.start()
        
    except KeyboardInterrupt:
        logger.info("Shutting down bot...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == '__main__':
    main()
