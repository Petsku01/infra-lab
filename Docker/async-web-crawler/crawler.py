"""
Crawler orchestration module
@author pk
"""

import logging
import aiohttp
import asyncio
import ssl
from typing import List, Optional, Dict, Any
from fetcher import HttpFetcher
from parser import ContentParser
from storage import CsvStorage
from validators import validate_proxy_url, check_robots_txt

logger = logging.getLogger(__name__)

MAX_CONCURRENT_REQUESTS = 5


class WebCrawler:
    """Main crawler orchestrator."""
    
    def __init__(self, max_concurrent: int = MAX_CONCURRENT_REQUESTS, max_retries: int = 3, rate_limit: float = 5.0):
        self.max_concurrent = max_concurrent
        self.fetcher = HttpFetcher(max_retries=max_retries, rate_limit=rate_limit)
        self.parser = ContentParser()
        self.rate_limit = rate_limit
    
    async def crawl(
        self,
        urls: List[str],
        proxy: Optional[str] = None,
        storage: Optional[CsvStorage] = None
    ) -> List[Dict[str, Any]]:
        """
        Crawl multiple URLs concurrently.
        
        Args:
            urls: List of URLs to crawl
            proxy: Optional proxy URL
            storage: Optional storage backend
            
        Returns:
            List of results
        """
        if not urls:
            logger.error("No URLs provided")
            return []
        
        # Validate proxy
        proxy = validate_proxy_url(proxy) if proxy else None
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            ssl=ssl_context
        )
        timeout = aiohttp.ClientTimeout(total=300)
        
        results = []
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def crawl_url_with_semaphore(url: str) -> Dict[str, Any]:
                async with semaphore:
                    return await self._crawl_single_url(session, url, proxy, storage)
            
            tasks = [crawl_url_with_semaphore(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        filtered_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task failed with exception: {result}")
                # Return error dict for failed tasks
                filtered_results.append({
                    'url': 'unknown',
                    'suspicious': None,
                    'confidence': 0.0,
                    'content_type': 'error',
                    'error': str(result)
                })
            else:
                filtered_results.append(result)
        
        return filtered_results
    
    async def _crawl_single_url(
        self,
        session: aiohttp.ClientSession,
        url: str,
        proxy: Optional[str],
        storage: Optional[CsvStorage]
    ) -> Dict[str, Any]:
        """Crawl a single URL."""
        try:
            # Check robots.txt
            if not check_robots_txt(url):
                logger.info(f"URL disallowed by robots.txt: {url}")
                result = {
                    'url': url,
                    'suspicious': None,
                    'confidence': 0.0,
                    'content_type': 'disallowed'
                }
                if storage:
                    storage.add_result(result)
                return result
            
            # Fetch HTML
            fetch_result = await self.fetcher.fetch_url(session, url, proxy)
            
            if fetch_result['status'] != 'success':
                if storage:
                    storage.add_result({
                        'url': url,
                        'suspicious': None,
                        'confidence': 0.0,
                        'content_type': fetch_result['status']
                    })
                return fetch_result
            
            # Parse content
            html = fetch_result['html']
            result = self.parser.analyze(html, url)
            
            if storage:
                storage.add_result(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            error_result = {
                'url': url,
                'suspicious': None,
                'confidence': 0.0,
                'content_type': 'error'
            }
            if storage:
                storage.add_result(error_result)
            return error_result
