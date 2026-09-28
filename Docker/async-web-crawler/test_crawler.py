"""
Integration tests for crawler module
@author pk
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from crawler import WebCrawler
from fetcher import HttpFetcher
from parser import ContentParser
from storage import CsvStorage


class TestWebCrawler:
    """Test crawler orchestration and integration."""
    
    @pytest.fixture
    def mock_fetcher(self):
        """Create mock HTTP fetcher."""
        fetcher = AsyncMock(spec=HttpFetcher)
        fetcher.fetch_url = AsyncMock()
        return fetcher
    
    @pytest.fixture
    def mock_parser(self):
        """Create mock content parser."""
        parser = MagicMock(spec=ContentParser)
        parser.analyze = MagicMock()
        return parser
    
    @pytest.fixture
    def mock_storage(self):
        """Create mock storage."""
        storage = MagicMock(spec=CsvStorage)
        storage.add_result = MagicMock()
        return storage
    
    @pytest.fixture
    def crawler(self, mock_fetcher, mock_parser):
        """Create crawler with mocks."""
        return WebCrawler(
            fetcher=mock_fetcher,
            parser=mock_parser,
            max_concurrent=2,
            timeout_seconds=10
        )
    
    @pytest.mark.asyncio
    async def test_crawl_single_url(self, crawler, mock_fetcher, mock_parser, mock_storage):
        """Test crawling a single URL."""
        # Setup mocks
        mock_fetcher.fetch_url.return_value = {
            'url': 'http://example.com',
            'html': '<html><body>Content</body></html>',
            'status': 200,
            'error': None
        }
        mock_parser.analyze.return_value = {
            'url': 'http://example.com',
            'suspicious': False,
            'confidence': 0.1,
            'content_type': 'structured'
        }
        
        # Run crawl
        urls = ['http://example.com']
        await crawler.crawl(urls, storage=mock_storage)
        
        # Verify
        mock_fetcher.fetch_url.assert_called()
        mock_parser.analyze.assert_called()
        mock_storage.add_result.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_crawl_multiple_urls_respects_concurrency(self, crawler, mock_fetcher, mock_parser, mock_storage):
        """Test that crawler respects max_concurrent limit."""
        # Setup mocks
        mock_fetcher.fetch_url = AsyncMock()
        mock_fetcher.fetch_url.return_value = {
            'url': 'http://example.com',
            'html': '<html></html>',
            'status': 200,
            'error': None
        }
        mock_parser.analyze.return_value = {
            'url': 'http://example.com',
            'suspicious': False,
            'confidence': 0.1,
            'content_type': 'structured'
        }
        
        # Create multiple URLs
        urls = [f'http://example.com/{i}' for i in range(5)]
        
        # Run crawl
        await crawler.crawl(urls, storage=mock_storage)
        
        # Verify all URLs were processed
        assert mock_fetcher.fetch_url.call_count == 5
        assert mock_storage.add_result.call_count == 5
    
    @pytest.mark.asyncio
    async def test_crawl_handles_fetch_errors(self, crawler, mock_fetcher, mock_parser, mock_storage):
        """Test crawler handles fetch errors gracefully."""
        # Setup mocks - return error
        mock_fetcher.fetch_url.return_value = {
            'url': 'http://example.com',
            'html': None,
            'status': 0,
            'error': 'Connection timeout'
        }
        mock_parser.analyze.return_value = {
            'url': 'http://example.com',
            'suspicious': None,
            'confidence': 0.0,
            'content_type': 'error'
        }
        
        # Run crawl
        urls = ['http://example.com']
        await crawler.crawl(urls, storage=mock_storage)
        
        # Verify error was stored
        mock_storage.add_result.assert_called_once()
        call_args = mock_storage.add_result.call_args
        assert call_args[0][0]['content_type'] == 'error'
    
    @pytest.mark.asyncio
    async def test_crawl_stores_suspicious_detection(self, crawler, mock_fetcher, mock_parser, mock_storage):
        """Test that suspicious pages are correctly stored."""
        # Setup mocks
        mock_fetcher.fetch_url.return_value = {
            'url': 'http://badsite.com',
            'html': '<html><body>Minimal</body></html>',
            'status': 200,
            'error': None
        }
        mock_parser.analyze.return_value = {
            'url': 'http://badsite.com',
            'suspicious': True,
            'confidence': 0.85,
            'content_type': 'sparse'
        }
        
        # Run crawl
        urls = ['http://badsite.com']
        await crawler.crawl(urls, storage=mock_storage)
        
        # Verify suspicious flag was stored
        call_args = mock_storage.add_result.call_args
        result = call_args[0][0]
        assert result['suspicious'] == True
        assert result['confidence'] == 0.85
