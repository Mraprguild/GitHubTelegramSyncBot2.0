#!/usr/bin/env python3
"""
Alternative launcher for the GitHub-Telegram Sync Bot.
Provides more control over the startup process and error handling.
"""

import sys
import logging
import signal
import threading
import time
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
        logging.FileHandler('bot.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

class BotLauncher:
    """Launcher class for managing bot lifecycle."""
    
    def __init__(self):
        """Initialize the bot launcher."""
        self.config = None
        self.telegram_bot = None
        self.webhook_handler = None
        self.web_interface = None
        self.running = False
        self.threads = []
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
    
    def initialize_components(self):
        """Initialize all bot components."""
        try:
            # Initialize configuration
            logger.info("Initializing configuration...")
            self.config = Config()
            self.config.validate()
            
            # Initialize Telegram bot
            logger.info("Initializing Telegram bot...")
            self.telegram_bot = TelegramBot(self.config)
            
            # Initialize webhook handler
            logger.info("Initializing webhook handler...")
            self.webhook_handler = WebhookHandler(self.config, self.telegram_bot)
            
            # Initialize web interface
            logger.info("Initializing web interface...")
            self.web_interface = WebInterface(self.config, self.telegram_bot)
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def start_services(self):
        """Start all services in separate threads."""
        try:
            # Start web interface
            web_thread = threading.Thread(
                target=self.web_interface.run_server,
                name="WebInterface",
                daemon=True
            )
            web_thread.start()
            self.threads.append(web_thread)
            
            # Wait for web interface to start
            time.sleep(2)
            logger.info(f"Web interface started on http://{self.config.web_host}:{self.config.web_port}")
            
            # Start webhook handler
            webhook_thread = threading.Thread(
                target=self.webhook_handler.run_server,
                name="WebhookHandler",
                daemon=True
            )
            webhook_thread.start()
            self.threads.append(webhook_thread)
            
            # Wait for webhook handler to start
            time.sleep(2)
            logger.info(f"Webhook handler started on http://{self.config.webhook_host}:{self.config.webhook_port}")
            
            logger.info("All services started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            raise
    
    def run(self):
        """Main run method."""
        try:
            logger.info("Starting GitHub-Telegram Sync Bot...")
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Initialize components
            self.initialize_components()
            
            # Start services
            self.start_services()
            
            # Mark as running
            self.running = True
            
            # Start Telegram bot (this will block)
            logger.info("Starting Telegram bot polling...")
            self.telegram_bot.start()
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown of all components."""
        if not self.running:
            return
        
        logger.info("Shutting down bot...")
        self.running = False
        
        # Stop Telegram bot
        if self.telegram_bot:
            self.telegram_bot.stop()
        
        # Wait for threads to finish (with timeout)
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
                if thread.is_alive():
                    logger.warning(f"Thread {thread.name} did not shut down gracefully")
        
        logger.info("Bot shutdown complete")

def main():
    """Main entry point."""
    launcher = BotLauncher()
    launcher.run()

if __name__ == '__main__':
    main()
