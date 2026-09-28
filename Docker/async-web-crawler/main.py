#!/usr/bin/env python3
"""
Main entry point for web crawler
@author pk
"""

import os
import sys
import logging
import asyncio
import signal
from crawler import WebCrawler
from storage import CsvStorage

# Setup logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    # Signal handlers for graceful shutdown
    def handle_shutdown(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    try:
        # Configuration
        urls = os.getenv('START_URLS', 'https://example.com').split(',')
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            logger.error("No URLs provided via START_URLS")
            sys.exit(1)
        
        try:
            max_retries = int(os.getenv('MAX_RETRIES', '3'))
            rate_limit = float(os.getenv('RATE_LIMIT_SEC', '5'))
        except ValueError:
            logger.warning("Invalid max retries or rate limit, using defaults")
            max_retries = 3
            rate_limit = 5.0
        
        proxy_url = os.getenv('PROXY_URL', '')
        output_file = os.getenv('OUTPUT_FILE', '/app/output/crawled_urls.csv')
        
        logger.info(f"Starting crawler: {len(urls)} URLs")
        
        # Run crawler
        crawler = WebCrawler(max_retries=max_retries, rate_limit=rate_limit)
        storage = CsvStorage(output_file)
        
        results = asyncio.run(
            crawler.crawl(urls, proxy=proxy_url or None, storage=storage)
        )
        
        # Validate results
        if not results:
            logger.error("No crawl results returned")
            sys.exit(1)
        
        # Check for errors in results
        error_count = sum(1 for r in results if r.get('content_type') == 'error' or r.get('suspicious') is None)
        logger.info(f"Crawl complete: {len(results)} URLs, {error_count} errors")
        
        # Save results
        if storage.save():
            logger.info("Results saved successfully.")
            sys.exit(0)
        else:
            logger.error("Failed to save results")
            sys.exit(1)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
