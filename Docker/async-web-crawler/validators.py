"""
Validator utilities for crawler
@author pk
"""

import logging
from urllib.parse import urlparse
from urllib import robotparser

logger = logging.getLogger(__name__)


def validate_proxy_url(proxy_url: str) -> str:
    """Validate proxy URL format."""
    if not proxy_url:
        return None
    try:
        parsed = urlparse(proxy_url)
        if parsed.scheme not in ('http', 'https', 'socks5'):
            logger.warning(f"Invalid proxy scheme: {parsed.scheme}")
            return None
        if not parsed.netloc:
            logger.warning("Proxy URL missing netloc")
            return None
        return proxy_url
    except Exception as e:
        logger.warning(f"Invalid proxy URL: {e}")
        return None


def check_robots_txt(url: str, user_agent: str = 'Mozilla/5.0') -> bool:
    """Check if URL is allowed by robots.txt with timeout."""
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        rp = robotparser.RobotFileParser()
        rp.set_url(robots_url)
        try:
            # Set timeout to prevent hanging, restore after
            import socket
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(5)  # 5 second timeout
            try:
                rp.read()
                result = rp.can_fetch(user_agent, url)
                return result
            finally:
                socket.setdefaulttimeout(old_timeout)  # Restore original timeout
        except Exception:
            # If robots.txt doesn't exist or times out, allow crawling
            return True
    except Exception as e:
        logger.debug(f"Error checking robots.txt: {e}")
        return True
