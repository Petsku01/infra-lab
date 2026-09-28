#!/usr/bin/env python3
"""
Async Web Crawler
@author pk
"""

import os
import logging
import aiohttp
import asyncio
import csv
import signal
import sys
import ssl
from urllib import robotparser
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Constants
MAX_RETRIES = 3
MAX_CONCURRENT_REQUESTS = 5
DEFAULT_RATE_LIMIT = 5
REQUEST_TIMEOUT = 30  # Total timeout
CONNECT_TIMEOUT = 10  # Connection timeout
READ_TIMEOUT = 30  # Read timeout
MAX_PAGE_SIZE = 5 * 1024 * 1024  # 5MB max page size
SUSPICION_THRESHOLD = 5
CONFIDENCE_HIGH = 0.85
CONFIDENCE_LOW = 0.15

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def sanitize_url_for_logging(url):
    """Remove query parameters that might contain secrets."""
    try:
        parsed = urlparse(url)
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            clean_url += "?[PARAMS_REDACTED]"
        return clean_url
    except Exception:
        return "[INVALID_URL]"


def validate_proxy_url(proxy_url):
    """Validate proxy URL format before use."""
    if not proxy_url:
        return None
    try:
        parsed = urlparse(proxy_url)
        if parsed.scheme not in ('http', 'https', 'socks5'):
            logger.warning(f"Invalid proxy scheme: {parsed.scheme}, ignoring proxy")
            return None
        if not parsed.netloc:
            logger.warning("Proxy URL missing netloc, ignoring proxy")
            return None
        return proxy_url
    except Exception as e:
        logger.warning(f"Invalid proxy URL: {e}, ignoring proxy")
        return None


def check_robots_txt(url, user_agent='Mozilla/5.0'):
    """Check if URL is allowed by robots.txt"""
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        rp = robotparser.RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
            return rp.can_fetch(user_agent, url)
        except Exception:
            # If robots.txt doesn't exist or can't be read, allow crawling
            return True
    except Exception as e:
        logger.debug(f"Error checking robots.txt: {e}")
        return True  # Allow if check fails


async def crawl_url(session, url, proxy, rate_limit, model, max_retries=MAX_RETRIES):
    """Crawl a single URL with retries."""
    if not url or not url.strip():
        logger.error("Empty URL provided")
        return {'url': url, 'suspicious': None, 'confidence': 0}
    
    # Check robots.txt before crawling
    if not check_robots_txt(url):
        logger.info(f"URL disallowed by robots.txt: {sanitize_url_for_logging(url)}")
        return {'url': url, 'suspicious': None, 'confidence': 0}
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for attempt in range(max_retries):
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
                    logger.warning(f"Page too large ({content_length} bytes), skipping")
                    return {'url': url, 'suspicious': None, 'confidence': 0}
                
                html = await response.text()
                
                # Check actual size after reading
                if len(html) > MAX_PAGE_SIZE:
                    logger.warning(f"Page exceeds size limit ({len(html)} bytes), skipping")
                    return {'url': url, 'suspicious': None, 'confidence': 0}
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract content
                content = soup.find_all('div', class_='content')
                
                # Heuristic analysis (no ML model)
                is_suspicious = len(content) < SUSPICION_THRESHOLD
                confidence = CONFIDENCE_HIGH if is_suspicious else CONFIDENCE_LOW
                
                safe_url = sanitize_url_for_logging(url)
                logger.info(f"Crawled: {safe_url} (suspicious: {is_suspicious})")
                return {'url': url, 'suspicious': is_suspicious, 'confidence': confidence}
                
        except asyncio.TimeoutError:
            safe_url = sanitize_url_for_logging(url)
            logger.warning(f"Timeout: {safe_url} (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                # Proper exponential backoff
                backoff = rate_limit * (2 ** attempt)
                await asyncio.sleep(backoff)
        except Exception as e:
            safe_url = sanitize_url_for_logging(url)
            logger.error(f"Error crawling {safe_url}: {e}")
            if attempt < max_retries - 1:
                backoff = rate_limit * (2 ** attempt)
                await asyncio.sleep(backoff)
    
    safe_url = sanitize_url_for_logging(url)
    logger.error(f"Failed: {safe_url} after {max_retries} attempts")
    return {'url': url, 'suspicious': None, 'confidence': 0}


async def main(urls, proxy, rate_limit, model, max_concurrent=MAX_CONCURRENT_REQUESTS):
    """Crawl URLs with concurrency limit."""
    if not urls:
        logger.error("No URLs provided to main()")
        return []
    
    # Create SSL context with proper certificate validation
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    
    connector = aiohttp.TCPConnector(
        limit=max_concurrent,
        ssl=ssl_context
    )
    timeout = aiohttp.ClientTimeout(total=300)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [crawl_url(session, url, proxy, rate_limit, model) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results


def write_results(results, output_file):
    """Write results to CSV file with validation."""
    if not results:
        logger.warning("No results to write")
        return
    
    try:
        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        seen_urls = set()
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'suspicious', 'confidence'])
            writer.writeheader()
            written_count = 0
            for result in results:
                if isinstance(result, dict):
                    # Validate required fields
                    if not all(key in result for key in ['url', 'suspicious', 'confidence']):
                        logger.warning(f"Skipping invalid result: {result}")
                        continue
                    # Deduplicate
                    if result['url'] in seen_urls:
                        logger.debug(f"Skipping duplicate URL: {result['url']}")
                        continue
                    seen_urls.add(result['url'])
                    # Validate confidence range
                    if not (0 <= result['confidence'] <= 1):
                        logger.warning(f"Invalid confidence {result['confidence']}, clamping to [0,1]")
                        result['confidence'] = max(0, min(1, result['confidence']))
                    writer.writerow(result)
                    written_count += 1
                elif isinstance(result, Exception):
                    logger.warning(f"Skipping failed result: {result}")
            logger.info(f"Wrote {written_count} unique results to {output_file}")
    except IOError as e:
        logger.error(f"Failed to write results to {output_file}: {e}")
        raise


if __name__ == "__main__":
    # Signal handlers for graceful shutdown
    def handle_shutdown(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    try:
        urls = os.getenv('START_URLS', 'https://example.com').split(',')
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            logger.error("No URLs provided via START_URLS environment variable")
            sys.exit(1)
        
        try:
            rate_limit = int(os.getenv('RATE_LIMIT_SEC', str(DEFAULT_RATE_LIMIT)))
        except ValueError:
            logger.warning(f"Invalid RATE_LIMIT_SEC, using default of {DEFAULT_RATE_LIMIT}")
            rate_limit = DEFAULT_RATE_LIMIT
        
        proxy = validate_proxy_url(os.getenv('PROXY_URL', ''))
        output_file = os.getenv('OUTPUT_FILE', '/app/output/crawled_urls.csv')
        
        # Mock model (placeholder)
        model = None
        
        logger.info(f"Starting crawler: {len(urls)} URLs")
        results = asyncio.run(main(urls, proxy, rate_limit, model))
        
        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        write_results(results, output_file)
        
        logger.info(f"Crawling complete. Results saved to {output_file}")
        sys.exit(0)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
