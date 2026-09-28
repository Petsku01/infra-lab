"""
HTTP fetching module for web crawler
@author pk
"""

import logging
import aiohttp
import asyncio
import ssl
from typing import Optional, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Constants
REQUEST_TIMEOUT = 30
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30
MAX_PAGE_SIZE = 5 * 1024 * 1024  # 5MB


def is_valid_url(url: str) -> bool:
    """Validate URL format."""
    try:
        parsed = urlparse(url)
        # Must have scheme (http/https) and netloc (domain)
        if not parsed.scheme in ('http', 'https'):
            return False
        if not parsed.netloc:
            return False
        return True
    except Exception:
        return False


class HttpFetcher:
    """Handles HTTP requests with retry logic and timeout management."""
    
    def __init__(self, max_retries: int = 3, rate_limit: float = 5.0):
        self.max_retries = max_retries
        self.rate_limit = rate_limit
    
    async def fetch_url(
        self,
        session: aiohttp.ClientSession,
        url: str,
        proxy: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch a URL with retries and size limits.
        
        Args:
            session: aiohttp ClientSession
            url: URL to fetch
            proxy: Optional proxy URL
            
        Returns:
            Dict with keys: url, html, status, error
        """
        if not url or not url.strip():
            logger.error("Empty URL provided")
            return {'url': url, 'html': None, 'status': 'error', 'error': 'Empty URL'}
        
        # Validate URL format
        if not is_valid_url(url):
            logger.error(f"Invalid URL format: {url}")
            return {'url': url, 'html': None, 'status': 'error', 'error': 'Invalid URL format'}
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for attempt in range(self.max_retries):
            try:
                timeout = aiohttp.ClientTimeout(
                    total=REQUEST_TIMEOUT,
                    connect=CONNECT_TIMEOUT,
                    sock_read=READ_TIMEOUT
                )
                
                async with session.get(
                    url,
                    headers=headers,
                    proxy=proxy,
                    timeout=timeout
                ) as response:
                    response.raise_for_status()
                    
                    # Check content length before reading
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) > MAX_PAGE_SIZE:
                        logger.warning(f"Content too large: {content_length} bytes")
                        return {'url': url, 'html': None, 'status': 'rejected', 'error': 'Content too large'}
                    
                    html = await response.text()
                    
                    # Check actual size after reading
                    if len(html) > MAX_PAGE_SIZE:
                        logger.warning(f"Page exceeds size limit: {len(html)} bytes")
                        return {'url': url, 'html': None, 'status': 'rejected', 'error': 'Page too large'}
                    
                    logger.info(f"Fetched: {url} ({len(html)} bytes)")
                    return {'url': url, 'html': html, 'status': 'success', 'error': None}
                    
            except asyncio.TimeoutError:
                logger.warning(f"Timeout: {url} (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    backoff = self.rate_limit * (2 ** attempt)
                    await asyncio.sleep(backoff)
            except aiohttp.ClientError as e:
                logger.error(f"HTTP error: {url} - {e}")
                if attempt < self.max_retries - 1:
                    backoff = self.rate_limit * (2 ** attempt)
                    await asyncio.sleep(backoff)
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                if attempt < self.max_retries - 1:
                    backoff = self.rate_limit * (2 ** attempt)
                    await asyncio.sleep(backoff)
        
        logger.error(f"Failed after {self.max_retries} attempts: {url}")
        return {'url': url, 'html': None, 'status': 'failed', 'error': 'Max retries exceeded'}
