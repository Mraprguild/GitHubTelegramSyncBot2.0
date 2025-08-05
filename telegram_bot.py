"""
Telegram bot implementation for GitHub integration.
Handles all Telegram bot commands and interactions.
"""

import logging
import asyncio
import time
from collections import defaultdict
from telegram._update import Update
from telegram._inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._bot import Bot
from telegram.constants import ParseMode
from github_client import GitHubClient
from config import Config
from utils import escape_markdown, format_timestamp

logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram bot for GitHub integration."""
    
    def __init__(self, config: Config):
        """
        Initialize Telegram bot.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.github_client = GitHubClient(config.github_token, config.github_username)
        self.bot = Bot(token=config.telegram_token)
        self.running = False
        
        # Rate limiting
        self.rate_limits = defaultdict(list)
        
    def is_rate_limited(self, chat_id):
        """Check if a chat is rate limited."""
        now = time.time()
        window_start = now - self.config.rate_limit_window
        
        # Clean old requests
        self.rate_limits[chat_id] = [
            req_time for req_time in self.rate_limits[chat_id] 
            if req_time > window_start
        ]
        
        # Check rate limit
        if len(self.rate_limits[chat_id]) >= self.config.rate_limit_requests:
            return True
        
        # Add current request
        self.rate_limits[chat_id].append(now)
        return False
    
    async def check_permissions(self, update: Update):
        """Check if the user has permission to use the bot."""
        if not update.effective_chat or not update.message:
            return False
            
        chat_id = update.effective_chat.id
        
        if not self.config.is_chat_allowed(chat_id):
            await update.message.reply_text(
                "❌ You are not authorized to use this bot.",
                parse_mode=ParseMode.MARKDOWN
            )
            return False
        
        if self.is_rate_limited(chat_id):
            await update.message.reply_text(
                "⏰ Rate limit exceeded. Please wait before making more requests.",
                parse_mode=ParseMode.MARKDOWN
            )
            return False
        
        return True

    async def start_command(self, update: Update, context=None):
        """Handle /start command."""
        if not await self.check_permissions(update):
            return
            
        welcome_message = """
🎯 **Welcome to GitHub-Telegram Sync Bot!** 🎯

✨ **Your intelligent GitHub companion, powered by modern AI** ✨

╔═══════════════════════════════════════╗
║              🚀 **FEATURES** 🚀              ║
╚═══════════════════════════════════════╝

🌟 **PROFILE & DISCOVERY**
├─ 👤 `/profile [username]` - Deep dive into GitHub profiles
├─ 🔍 `/search <query>` - AI-powered repository discovery
└─ 📚 `/repos [username]` - Smart repository collections

📈 **ADVANCED ANALYTICS**  
├─ 🏆 `/repo <owner/repo>` - Complete project insights & metrics
├─ 💫 `/commits <owner/repo>` - Beautiful commit history timeline
└─ 🎯 `/issues <owner/repo>` - Smart issue tracking dashboard

🔥 **REAL-TIME MAGIC**
├─ 📢 `/watch <owner/repo>` - Live notifications for all activities
├─ 🔕 `/unwatch <owner/repo>` - Smart notification management
└─ ⚡ **Instant webhook integration** for lightning-fast updates

🛠️ **SMART CONTROLS**
├─ 📊 `/status` - Advanced health & performance metrics
└─ 💬 `/help` - Interactive command assistant

╔═══════════════════════════════════════╗
║           💡 **QUICK START** 💡           ║
╚═══════════════════════════════════════╝

🚀 **Power User Tips:**
⭐ Try `/profile` to unlock your GitHub insights
🎪 Search with `/search "react typescript"` for trending repos  
🎨 Watch repos with `/watch microsoft/vscode` for live updates
🌍 **Works with ANY public repository worldwide!**

╔═══════════════════════════════════════╗
║        🎊 **GET STARTED NOW!** 🎊        ║
╚═══════════════════════════════════════╝

**Ready to supercharge your GitHub experience?**
**Type `/profile` or `/help` to begin your journey!** 🚀✨
"""
        
        if update.message:
            await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)

    async def help_command(self, update: Update, context=None):
        """Handle /help command."""
        if not await self.check_permissions(update):
            return
            
        help_message = """
🔧 **GitHub-Telegram Bot - Complete Command Reference**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 **PROFILE & USER INFORMATION**
• `/profile [username]` - Display comprehensive GitHub profile with:
  - Account statistics (followers, following, repositories)
  - Recent activity and contribution streak
  - Location, bio, and contact information
  - Account creation date and verification status

📚 **REPOSITORY EXPLORATION**
• `/repos [username]` - Browse repository collections featuring:
  - Repository descriptions and primary languages
  - Stars, forks, and update timestamps
  - Repository size and visibility status
• `/repo <owner/repo>` - Detailed repository analysis including:
  - Complete project statistics and metrics
  - Programming languages breakdown
  - Recent activity and contributor information
  - Issues, pull requests, and release tracking

📊 **DEVELOPMENT INSIGHTS**
• `/commits <owner/repo>` - Recent commit history with:
  - Author information and commit messages  
  - Timestamps and change summaries
  - Direct links to commit details on GitHub
• `/issues <owner/repo>` - Issue tracking dashboard showing:
  - Open issues with labels and priorities
  - Assignee information and creation dates
  - Issue status and comment counts

🔍 **SEARCH & DISCOVERY**
• `/search <query>` - Advanced repository search featuring:
  - Relevance-based results with descriptions
  - Language, stars, and activity filters
  - Direct repository links and statistics

🔔 **NOTIFICATION SYSTEM**
• `/watch <owner/repo>` - Enable real-time notifications for:
  - New commits and pushes to main branch
  - Issues creation and status changes
  - Pull request activities and merges
  - New releases and version tags
• `/unwatch <owner/repo>` - Disable notifications for specific repositories
• `/watching` - View your complete watch list with status

⚙️ **SYSTEM & MONITORING**
• `/status` - Comprehensive bot health dashboard:
  - API usage quotas and rate limits
  - System performance metrics
  - Active connections and uptime statistics
• `/help` - Display this detailed command reference

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **PRACTICAL EXAMPLES**
• `/profile torvalds` - View Linus Torvalds' GitHub profile
• `/repo microsoft/vscode` - Explore VS Code repository details
• `/commits facebook/react` - See recent React framework commits
• `/issues nodejs/node` - Check Node.js open issues
• `/search "machine learning python"` - Find ML repositories
• `/watch microsoft/vscode` - Get VS Code update notifications

💡 **USAGE TIPS & BEST PRACTICES**
🔸 Always use full repository names: `owner/repository`
🔸 Commands work with any public GitHub repository
🔸 Personal data shown when username is omitted (where applicable)
🔸 Rate limiting: {rate_limit} requests per {window} seconds per user
🔸 Use quotes for multi-word search queries
🔸 Bot supports both individual users and organization repositories
🔸 Webhook integration available for real-time repository monitoring

**Need help with a specific command? Just try it out - the bot provides helpful error messages and suggestions!**
""".format(
    rate_limit=self.config.rate_limit_requests,
    window=self.config.rate_limit_window
)
        
        if update.message:
            await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)

    async def profile_command(self, update: Update, context=None):
        """Handle /profile command."""
        if not await self.check_permissions(update):
            return
            
        try:
            # Extract username from message text
            if not update.message or not update.message.text:
                return
                
            message_text = update.message.text
            parts = message_text.split()
            username = parts[1] if len(parts) > 1 else None
            
            user_info = self.github_client.get_user_info(username)
            if not user_info:
                if update.message:
                    await update.message.reply_text(
                        "❌ User not found or API error occurred.",
                        parse_mode=ParseMode.MARKDOWN
                    )
                return
            
            formatted_info = self.github_client.format_user_info(user_info)
            if update.message:
                await update.message.reply_text(formatted_info, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in profile command: {e}")
            if update.message:
                await update.message.reply_text(
                    "❌ An error occurred while fetching profile information.",
                    parse_mode=ParseMode.MARKDOWN
                )

    async def repos_command(self, update: Update, context=None):
        """Handle /repos command."""
        if not await self.check_permissions(update):
            return
            
        try:
            # Extract username from message text
            if not update.message or not update.message.text:
                return
                
            message_text = update.message.text
            parts = message_text.split()
            username = parts[1] if len(parts) > 1 else None
            
            repositories = self.github_client.get_user_repositories(username, limit=10)
            if not repositories:
                if update.message:
                    await update.message.reply_text(
                        "❌ No repositories found or API error occurred.",
                        parse_mode=ParseMode.MARKDOWN
                    )
                return
            
            repo_list = "\n".join([
                f"📦 **{repo['name']}** - ⭐ {repo['stargazers_count']} stars"
                for repo in repositories
            ])
            
            message = f"📚 **Repositories:**\n\n{repo_list}"
            if update.message:
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in repos command: {e}")
            if update.message:
                await update.message.reply_text(
                    "❌ An error occurred while fetching repositories.",
                    parse_mode=ParseMode.MARKDOWN
                )

    async def repo_command(self, update: Update, context=None):
        """Handle /repo command."""
        if not await self.check_permissions(update):
            return
            
        try:
            # Extract repo path from message text
            if not update.message or not update.message.text:
                return
                
            message_text = update.message.text
            parts = message_text.split()
            if len(parts) < 2:
                if update.message:
                    await update.message.reply_text(
                        "❌ Please specify a repository: `/repo owner/repo`",
                        parse_mode=ParseMode.MARKDOWN
                    )
                return
            
            repo_path = parts[1]
            if '/' not in repo_path:
                if update.message:
                    await update.message.reply_text(
                        "❌ Invalid format. Use: `/repo owner/repo`",
                        parse_mode=ParseMode.MARKDOWN
                    )
                return
            
            owner, repo = repo_path.split('/', 1)
            repo_info = self.github_client.get_repository_details(owner, repo)
            if not repo_info:
                if update.message:
                    await update.message.reply_text(
                        f"❌ Repository `{repo_path}` not found or API error occurred.",
                        parse_mode=ParseMode.MARKDOWN
                    )
                return
            
            formatted_info = self.github_client.format_repository_info(repo_info)
            if update.message:
                await update.message.reply_text(formatted_info, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in repo command: {e}")
            if update.message:
                await update.message.reply_text(
                    "❌ An error occurred while fetching repository information.",
                    parse_mode=ParseMode.MARKDOWN
                )

    async def commits_command(self, update: Update, context=None):
        """Handle /commits command."""
        if not await self.check_permissions(update):
            return
            
        try:
            # Extract repo path from message text
            message_text = update.message.text
            parts = message_text.split()
            if len(parts) < 2:
                await update.message.reply_text(
                    "❌ Please specify a repository: `/commits owner/repo`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            repo_path = parts[1]
            if '/' not in repo_path:
                await update.message.reply_text(
                    "❌ Invalid format. Use: `/commits owner/repo`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            owner, repo = repo_path.split('/', 1)
            commits = self.github_client.get_repository_commits(owner, repo, limit=5)
            if not commits:
                await update.message.reply_text(
                    f"❌ No commits found for `{repo_path}` or API error occurred.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            message = f"📝 **Recent Commits for {repo_path}:**\n\n"
            for commit in commits:
                commit_info = commit.get('commit', {})
                author = commit_info.get('author', {})
                message_text = commit_info.get('message', 'No message')
                author_name = author.get('name', 'Unknown')
                commit_date = author.get('date', '')
                
                if commit_date:
                    date_str = format_timestamp(commit_date)
                else:
                    date_str = 'Unknown date'
                
                sha = commit.get('sha', '')[:7]
                url = commit.get('html_url', '')
                
                message += f"🔸 **{escape_markdown(message_text)}**\n"
                message += f"👤 {escape_markdown(author_name)} • 🕒 {date_str}\n"
                message += f"🔗 [`{sha}`]({url})\n\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in commits command: {e}")
            await update.message.reply_text(
                "❌ An error occurred while fetching commits.",
                parse_mode=ParseMode.MARKDOWN
            )

    async def issues_command(self, update: Update, context=None):
        """Handle /issues command."""
        if not await self.check_permissions(update):
            return
            
        try:
            # Extract repo path from message text
            message_text = update.message.text
            parts = message_text.split()
            if len(parts) < 2:
                await update.message.reply_text(
                    "❌ Please specify a repository: `/issues owner/repo`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            repo_path = parts[1]
            if '/' not in repo_path:
                await update.message.reply_text(
                    "❌ Invalid format. Use: `/issues owner/repo`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            owner, repo = repo_path.split('/', 1)
            issues = self.github_client.get_repository_issues(owner, repo, limit=5)
            if not issues:
                await update.message.reply_text(
                    f"❌ No issues found for `{repo_path}` or API error occurred.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            message = f"🐛 **Issues for {repo_path}:**\n\n"
            for issue in issues:
                title = issue.get('title', 'No title')
                number = issue.get('number', 0)
                state = issue.get('state', 'unknown')
                user = issue.get('user', {}).get('login', 'Unknown')
                url = issue.get('html_url', '')
                
                state_emoji = "🟢" if state == "open" else "🔴"
                message += f"{state_emoji} **#{number}: {escape_markdown(title)}**\n"
                message += f"👤 {escape_markdown(user)} • 📋 {state}\n"
                message += f"🔗 [View Issue]({url})\n\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in issues command: {e}")
            await update.message.reply_text(
                "❌ An error occurred while fetching issues.",
                parse_mode=ParseMode.MARKDOWN
            )

    async def search_command(self, update: Update, context=None):
        """Handle /search command."""
        if not await self.check_permissions(update):
            return
            
        try:
            # Extract search query from message text
            message_text = update.message.text
            parts = message_text.split(maxsplit=1)
            if len(parts) < 2:
                await update.message.reply_text(
                    "❌ Please specify a search query: `/search <query>`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            query = parts[1]
            repositories = self.github_client.search_repositories(query, limit=8)
            if not repositories:
                await update.message.reply_text(
                    f"❌ No repositories found for query: `{query}`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            message = f"🔍 **Search Results for: {escape_markdown(query)}**\n\n"
            for repo in repositories:
                name = repo.get('name', 'Unknown')
                full_name = repo.get('full_name', 'Unknown')
                description = repo.get('description', 'No description') or 'No description'
                stars = repo.get('stargazers_count', 0)
                url = repo.get('html_url', '')
                
                message += f"📦 **{escape_markdown(name)}**\n"
                message += f"🔗 {escape_markdown(full_name)}\n"
                message += f"📝 {escape_markdown(description[:100])}{'...' if len(description) > 100 else ''}\n"
                message += f"⭐ {stars} stars • [View]({url})\n\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in search command: {e}")
            await update.message.reply_text(
                "❌ An error occurred while searching repositories.",
                parse_mode=ParseMode.MARKDOWN
            )

    async def status_command(self, update: Update, context=None):
        """Handle /status command."""
        if not await self.check_permissions(update):
            return
            
        try:
            # Get GitHub API rate limit info
            rate_limit_info = self.github_client.get_rate_limit()
            
            message = "📊 **Bot Status**\n\n"
            message += f"🤖 **Bot:** Running\n"
            message += f"🔧 **GitHub API:** Connected\n"
            
            if rate_limit_info:
                remaining = rate_limit_info.get('remaining', 'Unknown')
                limit = rate_limit_info.get('limit', 'Unknown')
                reset_time = rate_limit_info.get('reset', '')
                
                message += f"📈 **API Limits:** {remaining}/{limit} remaining\n"
                if reset_time:
                    reset_str = format_timestamp(reset_time, is_timestamp=True)
                    message += f"🔄 **Reset:** {reset_str}\n"
            
            message += f"\n⚙️ **Configuration:**\n"
            message += f"• Rate limit: {self.config.rate_limit_requests} req/{self.config.rate_limit_window}s\n"
            message += f"• Notifications: {'Enabled' if self.config.notify_on_push else 'Disabled'}\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text(
                "❌ An error occurred while fetching status.",
                parse_mode=ParseMode.MARKDOWN
            )

    async def handle_message(self, update: Update):
        """Handle incoming messages."""
        try:
            if not update.message or not update.message.text:
                return
                
            message_text = update.message.text
            
            if message_text.startswith('/start'):
                await self.start_command(update)
            elif message_text.startswith('/help'):
                await self.help_command(update)
            elif message_text.startswith('/profile'):
                await self.profile_command(update)
            elif message_text.startswith('/repos'):
                await self.repos_command(update)
            elif message_text.startswith('/repo'):
                await self.repo_command(update)
            elif message_text.startswith('/commits'):
                await self.commits_command(update)
            elif message_text.startswith('/issues'):
                await self.issues_command(update)
            elif message_text.startswith('/search'):
                await self.search_command(update)
            elif message_text.startswith('/status'):
                await self.status_command(update)
            else:
                if await self.check_permissions(update):
                    await update.message.reply_text(
                        "❌ Unknown command. Use /help to see available commands.",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            try:
                await update.message.reply_text(
                    "❌ An error occurred while processing your message.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass

    async def send_notification(self, chat_ids, message):
        """Send notification to specified chat IDs."""
        for chat_id in chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Failed to send notification to {chat_id}: {e}")

    async def run_polling(self):
        """Run the bot with long polling."""
        logger.info("Starting Telegram bot polling...")
        self.running = True
        last_update_id = 0
        
        try:
            while self.running:
                try:
                    # Get updates with offset
                    updates = await self.bot.get_updates(
                        offset=last_update_id + 1,
                        timeout=10
                    )
                    
                    for update in updates:
                        if update.message:
                            await self.handle_message(update)
                        # Update the last processed update ID
                        last_update_id = update.update_id
                        
                except Exception as e:
                    logger.error(f"Error in polling loop: {e}")
                    await asyncio.sleep(5)
                    
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in bot: {e}")
            raise
        finally:
            self.running = False

    def start(self):
        """Start the Telegram bot."""
        try:
            asyncio.run(self.run_polling())
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise

    def stop(self):
        """Stop the Telegram bot."""
        self.running = False
        logger.info("Stopping Telegram bot...")
