"""
GitHub API client for repository management and data fetching.
"""

import requests
import logging
from typing import Dict, List, Optional
from utils import escape_markdown, format_timestamp

logger = logging.getLogger(__name__)

class GitHubClient:
    """GitHub API client for interacting with GitHub repositories."""
    
    def __init__(self, token: str, username: str):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token
            username: GitHub username
        """
        self.token = token
        self.username = username
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Telegram-Bot/1.0'
        })
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Make a request to the GitHub API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response or None on error
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Resource not found: {endpoint}")
                return None
            elif response.status_code == 403:
                logger.error(f"API rate limit exceeded or forbidden: {endpoint}")
                return None
            else:
                logger.error(f"GitHub API error {response.status_code}: {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request error for {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {endpoint}: {e}")
            return None
    
    def get_rate_limit(self) -> Optional[Dict]:
        """Get current API rate limit status."""
        return self._make_request('/rate_limit')
    
    def get_user_info(self, username: str = None) -> Optional[Dict]:
        """
        Get user information.
        
        Args:
            username: GitHub username (defaults to authenticated user)
            
        Returns:
            User information dictionary
        """
        if username:
            endpoint = f"/users/{username}"
        else:
            endpoint = "/user"
        
        return self._make_request(endpoint)
    
    def get_user_repositories(self, username: str = None, limit: int = 10) -> List[Dict]:
        """
        Get user repositories.
        
        Args:
            username: GitHub username (defaults to authenticated user)
            limit: Maximum number of repositories to return
            
        Returns:
            List of repository dictionaries
        """
        if username:
            endpoint = f"/users/{username}/repos"
        else:
            endpoint = "/user/repos"
        
        params = {
            'sort': 'updated',
            'per_page': min(limit, 100)
        }
        
        result = self._make_request(endpoint, params)
        return result if result else []
    
    def get_repository_details(self, owner: str, repo: str) -> Optional[Dict]:
        """
        Get detailed repository information.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository information dictionary
        """
        endpoint = f"/repos/{owner}/{repo}"
        return self._make_request(endpoint)
    
    def get_repository_commits(self, owner: str, repo: str, limit: int = 10) -> List[Dict]:
        """
        Get repository commits.
        
        Args:
            owner: Repository owner
            repo: Repository name
            limit: Maximum number of commits to return
            
        Returns:
            List of commit dictionaries
        """
        endpoint = f"/repos/{owner}/{repo}/commits"
        params = {
            'per_page': min(limit, 100)
        }
        
        result = self._make_request(endpoint, params)
        return result if result else []
    
    def get_repository_issues(self, owner: str, repo: str, limit: int = 10) -> List[Dict]:
        """
        Get repository issues.
        
        Args:
            owner: Repository owner
            repo: Repository name
            limit: Maximum number of issues to return
            
        Returns:
            List of issue dictionaries
        """
        endpoint = f"/repos/{owner}/{repo}/issues"
        params = {
            'state': 'open',
            'per_page': min(limit, 100)
        }
        
        result = self._make_request(endpoint, params)
        return result if result else []
    
    def search_repositories(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search repositories.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of repository dictionaries
        """
        endpoint = "/search/repositories"
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': min(limit, 100)
        }
        
        result = self._make_request(endpoint, params)
        if result and 'items' in result:
            return result['items']
        return []
    
    def format_user_info(self, user_info: Dict) -> str:
        """
        Format user information for display.
        
        Args:
            user_info: User information dictionary
            
        Returns:
            Formatted user information string
        """
        login = user_info.get('login', 'Unknown')
        name = user_info.get('name', 'No name')
        bio = user_info.get('bio', 'No bio')
        public_repos = user_info.get('public_repos', 0)
        followers = user_info.get('followers', 0)
        following = user_info.get('following', 0)
        location = user_info.get('location', 'Unknown')
        company = user_info.get('company', 'Unknown')
        blog = user_info.get('blog', '')
        created_at = user_info.get('created_at', '')
        
        message = f"👤 **GitHub Profile: {escape_markdown(login)}**\n\n"
        
        if name and name != 'No name':
            message += f"🏷️ **Name:** {escape_markdown(name)}\n"
        
        if bio and bio != 'No bio':
            message += f"📝 **Bio:** {escape_markdown(bio)}\n"
        
        message += f"📊 **Stats:**\n"
        message += f"• 📦 Repositories: {public_repos}\n"
        message += f"• 👥 Followers: {followers}\n"
        message += f"• 👁️ Following: {following}\n"
        
        if location and location != 'Unknown':
            message += f"📍 **Location:** {escape_markdown(location)}\n"
        
        if company and company != 'Unknown':
            message += f"🏢 **Company:** {escape_markdown(company)}\n"
        
        if blog:
            message += f"🌐 **Website:** {escape_markdown(blog)}\n"
        
        if created_at:
            join_date = format_timestamp(created_at)
            message += f"📅 **Joined:** {join_date}\n"
        
        profile_url = user_info.get('html_url', '')
        if profile_url:
            message += f"\n🔗 [View Profile]({profile_url})"
        
        return message
    
    def format_repository_info(self, repo_info: Dict) -> str:
        """
        Format repository information for display.
        
        Args:
            repo_info: Repository information dictionary
            
        Returns:
            Formatted repository information string
        """
        name = repo_info.get('name', 'Unknown')
        full_name = repo_info.get('full_name', 'Unknown')
        description = repo_info.get('description', 'No description') or 'No description'
        language = repo_info.get('language', 'Unknown')
        stars = repo_info.get('stargazers_count', 0)
        forks = repo_info.get('forks_count', 0)
        watchers = repo_info.get('watchers_count', 0)
        open_issues = repo_info.get('open_issues_count', 0)
        size = repo_info.get('size', 0)
        default_branch = repo_info.get('default_branch', 'main')
        private = repo_info.get('private', False)
        created_at = repo_info.get('created_at', '')
        updated_at = repo_info.get('updated_at', '')
        html_url = repo_info.get('html_url', '')
        
        message = f"📦 **Repository: {escape_markdown(full_name)}**\n\n"
        message += f"📝 **Description:** {escape_markdown(description)}\n\n"
        
        message += f"📊 **Statistics:**\n"
        message += f"• ⭐ Stars: {stars}\n"
        message += f"• 🍴 Forks: {forks}\n"
        message += f"• 👁️ Watchers: {watchers}\n"
        message += f"• 🐛 Open Issues: {open_issues}\n"
        message += f"• 📏 Size: {size} KB\n"
        
        message += f"\n🔧 **Details:**\n"
        message += f"• 💻 Language: {escape_markdown(language)}\n"
        message += f"• 🌿 Default Branch: {escape_markdown(default_branch)}\n"
        message += f"• 🔒 Visibility: {'Private' if private else 'Public'}\n"
        
        if created_at:
            created_date = format_timestamp(created_at)
            message += f"• 📅 Created: {created_date}\n"
        
        if updated_at:
            updated_date = format_timestamp(updated_at)
            message += f"• 🔄 Updated: {updated_date}\n"
        
        if html_url:
            message += f"\n🔗 [View Repository]({html_url})"
        
        return message
