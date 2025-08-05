"""
Webhook handler for processing GitHub events.
"""

import json
import hmac
import hashlib
import logging
from flask import Flask, request, jsonify
import asyncio
from threading import Thread
from utils import escape_markdown, format_timestamp

logger = logging.getLogger(__name__)

class WebhookHandler:
    """Handles GitHub webhook events and forwards notifications to Telegram."""
    
    def __init__(self, config, telegram_bot):
        """
        Initialize webhook handler.
        
        Args:
            config: Configuration object
            telegram_bot: TelegramBot instance
        """
        self.config = config
        self.telegram_bot = telegram_bot
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes for webhook handling."""
        
        @self.app.route('/webhook', methods=['POST'])
        def handle_webhook():
            return self.process_webhook()
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({'status': 'healthy', 'service': 'webhook_handler'})
    
    def verify_signature(self, payload_body, signature_header):
        """
        Verify GitHub webhook signature.
        
        Args:
            payload_body: Raw payload body
            signature_header: X-Hub-Signature-256 header value
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.config.github_webhook_secret:
            logger.warning("No webhook secret configured, skipping signature verification")
            return True
        
        if not signature_header:
            logger.error("No signature header provided")
            return False
        
        if not signature_header.startswith('sha256='):
            logger.error("Invalid signature format")
            return False
        
        expected_signature = hmac.new(
            self.config.github_webhook_secret.encode('utf-8'),
            payload_body,
            hashlib.sha256
        ).hexdigest()
        
        signature = signature_header[7:]  # Remove 'sha256=' prefix
        
        return hmac.compare_digest(expected_signature, signature)
    
    def process_webhook(self):
        """Process incoming webhook requests."""
        try:
            # Get request data
            payload_body = request.get_data()
            signature_header = request.headers.get('X-Hub-Signature-256')
            event_type = request.headers.get('X-GitHub-Event')
            
            # Verify signature
            if not self.verify_signature(payload_body, signature_header):
                logger.error("Invalid webhook signature")
                return jsonify({'error': 'Invalid signature'}), 403
            
            # Parse JSON payload
            try:
                payload = json.loads(payload_body.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON payload: {e}")
                return jsonify({'error': 'Invalid JSON'}), 400
            
            # Process the event
            self.handle_github_event(event_type, payload)
            
            return jsonify({'status': 'success'}), 200
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def handle_github_event(self, event_type, payload):
        """
        Handle specific GitHub events.
        
        Args:
            event_type: Type of GitHub event
            payload: Event payload
        """
        try:
            message = None
            
            if event_type == 'push' and self.config.notify_on_push:
                message = self.format_push_event(payload)
            elif event_type == 'issues' and self.config.notify_on_issues:
                message = self.format_issues_event(payload)
            elif event_type == 'pull_request' and self.config.notify_on_pull_requests:
                message = self.format_pull_request_event(payload)
            elif event_type == 'release' and self.config.notify_on_releases:
                message = self.format_release_event(payload)
            elif event_type == 'ping':
                message = self.format_ping_event(payload)
            
            if message and self.config.allowed_chat_ids:
                # Send notification to all allowed chat IDs
                self.send_notification_async(message)
                
        except Exception as e:
            logger.error(f"Error handling {event_type} event: {e}")
    
    def format_push_event(self, payload):
        """Format push event notification."""
        try:
            repository = payload.get('repository', {})
            repo_name = repository.get('full_name', 'Unknown')
            ref = payload.get('ref', '')
            branch = ref.split('/')[-1] if ref.startswith('refs/heads/') else ref
            commits = payload.get('commits', [])
            pusher = payload.get('pusher', {}).get('name', 'Unknown')
            
            if not commits:
                return None
            
            message = f"🚀 **Push to {escape_markdown(repo_name)}**\n\n"
            message += f"🌿 **Branch:** {escape_markdown(branch)}\n"
            message += f"👤 **Pusher:** {escape_markdown(pusher)}\n"
            message += f"📝 **Commits:** {len(commits)}\n\n"
            
            # Show up to 3 commits
            for commit in commits[:3]:
                commit_message = commit.get('message', 'No message')
                author = commit.get('author', {}).get('name', 'Unknown')
                sha = commit.get('id', '')[:7]
                url = commit.get('url', '')
                
                message += f"🔸 **{escape_markdown(commit_message)}**\n"
                message += f"👤 {escape_markdown(author)} • [`{sha}`]({url})\n\n"
            
            if len(commits) > 3:
                message += f"... and {len(commits) - 3} more commits\n\n"
            
            repo_url = repository.get('html_url', '')
            if repo_url:
                message += f"🔗 [View Repository]({repo_url})"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting push event: {e}")
            return None
    
    def format_issues_event(self, payload):
        """Format issues event notification."""
        try:
            action = payload.get('action', 'unknown')
            issue = payload.get('issue', {})
            repository = payload.get('repository', {})
            
            repo_name = repository.get('full_name', 'Unknown')
            issue_title = issue.get('title', 'No title')
            issue_number = issue.get('number', 0)
            issue_url = issue.get('html_url', '')
            user = issue.get('user', {}).get('login', 'Unknown')
            
            action_emoji = {
                'opened': '🆕',
                'closed': '✅',
                'reopened': '🔄',
                'edited': '✏️'
            }.get(action, '📋')
            
            message = f"{action_emoji} **Issue {action} in {escape_markdown(repo_name)}**\n\n"
            message += f"🐛 **#{issue_number}: {escape_markdown(issue_title)}**\n"
            message += f"👤 **By:** {escape_markdown(user)}\n"
            
            if issue_url:
                message += f"🔗 [View Issue]({issue_url})"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting issues event: {e}")
            return None
    
    def format_pull_request_event(self, payload):
        """Format pull request event notification."""
        try:
            action = payload.get('action', 'unknown')
            pull_request = payload.get('pull_request', {})
            repository = payload.get('repository', {})
            
            repo_name = repository.get('full_name', 'Unknown')
            pr_title = pull_request.get('title', 'No title')
            pr_number = pull_request.get('number', 0)
            pr_url = pull_request.get('html_url', '')
            user = pull_request.get('user', {}).get('login', 'Unknown')
            
            action_emoji = {
                'opened': '🆕',
                'closed': '✅',
                'merged': '🎉',
                'reopened': '🔄',
                'edited': '✏️'
            }.get(action, '📋')
            
            message = f"{action_emoji} **Pull Request {action} in {escape_markdown(repo_name)}**\n\n"
            message += f"🔀 **#{pr_number}: {escape_markdown(pr_title)}**\n"
            message += f"👤 **By:** {escape_markdown(user)}\n"
            
            if pr_url:
                message += f"🔗 [View Pull Request]({pr_url})"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting pull request event: {e}")
            return None
    
    def format_release_event(self, payload):
        """Format release event notification."""
        try:
            action = payload.get('action', 'unknown')
            release = payload.get('release', {})
            repository = payload.get('repository', {})
            
            if action != 'published':
                return None
            
            repo_name = repository.get('full_name', 'Unknown')
            release_name = release.get('name', 'No name')
            tag_name = release.get('tag_name', 'Unknown')
            release_url = release.get('html_url', '')
            author = release.get('author', {}).get('login', 'Unknown')
            
            message = f"🎉 **New Release in {escape_markdown(repo_name)}**\n\n"
            message += f"🏷️ **{escape_markdown(release_name)}** ({escape_markdown(tag_name)})\n"
            message += f"👤 **By:** {escape_markdown(author)}\n"
            
            if release_url:
                message += f"🔗 [View Release]({release_url})"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting release event: {e}")
            return None
    
    def format_ping_event(self, payload):
        """Format ping event notification."""
        repository = payload.get('repository', {})
        repo_name = repository.get('full_name', 'Unknown')
        
        return f"🏓 **Webhook configured for {escape_markdown(repo_name)}**\n\nWebhook is working correctly!"
    
    def send_notification_async(self, message):
        """Send notification asynchronously."""
        def run_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    self.telegram_bot.send_notification(self.config.allowed_chat_ids, message)
                )
                loop.close()
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
        
        thread = Thread(target=run_async)
        thread.daemon = True
        thread.start()
    
    def run_server(self):
        """Run the webhook server."""
        try:
            logger.info(f"Starting webhook server on {self.config.webhook_host}:{self.config.webhook_port}")
            self.app.run(
                host=self.config.webhook_host,
                port=self.config.webhook_port,
                debug=self.config.debug_mode
            )
        except Exception as e:
            logger.error(f"Error running webhook server: {e}")
            raise
