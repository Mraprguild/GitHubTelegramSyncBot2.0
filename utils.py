"""
Utility functions for the GitHub-Telegram Sync Bot.
"""

import re
import logging
from datetime import datetime
from typing import Union

logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    """
    Escape special characters for Telegram MarkdownV2.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for Telegram markdown
    """
    if not text:
        return ""
    
    # Characters that need to be escaped in MarkdownV2
    special_chars = r'_*[]()~`>#+-=|{}.!'
    
    # Escape each special character
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def format_timestamp(timestamp: Union[str, int], is_timestamp: bool = False) -> str:
    """
    Format timestamp for display.
    
    Args:
        timestamp: ISO timestamp string or Unix timestamp
        is_timestamp: True if timestamp is Unix timestamp, False if ISO string
        
    Returns:
        Formatted timestamp string
    """
    try:
        if is_timestamp:
            # Unix timestamp
            dt = datetime.fromtimestamp(int(timestamp))
        else:
            # ISO timestamp string
            # Handle GitHub's ISO format with Z suffix
            if timestamp.endswith('Z'):
                timestamp = timestamp[:-1] + '+00:00'
            dt = datetime.fromisoformat(timestamp)
        
        return dt.strftime('%Y-%m-%d %H:%M UTC')
        
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to format timestamp {timestamp}: {e}")
        return "Unknown date"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def validate_repo_path(repo_path: str) -> tuple:
    """
    Validate and parse repository path.
    
    Args:
        repo_path: Repository path in format "owner/repo"
        
    Returns:
        Tuple of (owner, repo) or (None, None) if invalid
    """
    if not repo_path or '/' not in repo_path:
        return None, None
    
    parts = repo_path.split('/', 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None, None
    
    owner, repo = parts
    
    # Basic validation - GitHub usernames and repo names
    if not re.match(r'^[a-zA-Z0-9._-]+$', owner) or not re.match(r'^[a-zA-Z0-9._-]+$', repo):
        return None, None
    
    return owner, repo

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip()
    
    # Ensure filename is not too long
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def is_valid_github_username(username: str) -> bool:
    """
    Validate GitHub username format.
    
    Args:
        username: Username to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not username:
        return False
    
    # GitHub username rules:
    # - May only contain alphanumeric characters or single hyphens
    # - Cannot begin or end with a hyphen
    # - Maximum 39 characters
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$'
    return bool(re.match(pattern, username))

def format_duration(seconds: int) -> str:
    """
    Format duration in human readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        return f"{hours}h"

def extract_command_args(message_text: str) -> list:
    """
    Extract command arguments from message text.
    
    Args:
        message_text: Full message text
        
    Returns:
        List of command arguments (excluding the command itself)
    """
    if not message_text:
        return []
    
    parts = message_text.strip().split()
    return parts[1:] if len(parts) > 1 else []
