#!/usr/bin/env python3
"""
Unit tests for web crawler
@author pk
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from web_crawler import (
    validate_proxy_url,
    sanitize_url_for_logging,
    crawl_url,
    write_results,
    MAX_RETRIES,
    REQUEST_TIMEOUT
)
import os
import tempfile


class TestValidateProxyUrl:
    """Test proxy URL validation."""
    
    def test_valid_http_proxy(self):
        assert validate_proxy_url("http://proxy.example.com:8080") == "http://proxy.example.com:8080"
    
    def test_valid_https_proxy(self):
        assert validate_proxy_url("https://secure-proxy.example.com:443") == "https://secure-proxy.example.com:443"
    
    def test_valid_socks5_proxy(self):
        assert validate_proxy_url("socks5://socks.example.com:1080") == "socks5://socks.example.com:1080"
    
    def test_invalid_scheme(self):
        assert validate_proxy_url("ftp://proxy.example.com") is None
    
    def test_missing_netloc(self):
        assert validate_proxy_url("http://") is None
    
    def test_empty_proxy(self):
        assert validate_proxy_url("") is None
    
    def test_none_proxy(self):
        assert validate_proxy_url(None) is None
    
    def test_malformed_url(self):
        assert validate_proxy_url("not-a-url") is None


class TestSanitizeUrl:
    """Test URL sanitization for logging."""
    
    def test_simple_url(self):
        result = sanitize_url_for_logging("https://example.com/path")
        assert result == "https://example.com/path"
    
    def test_url_with_query_params(self):
        result = sanitize_url_for_logging("https://example.com/api?key=secret123&token=abc")
        assert result == "https://example.com/api?[PARAMS_REDACTED]"
    
    def test_url_with_fragment(self):
        result = sanitize_url_for_logging("https://example.com/page#section")
        assert result == "https://example.com/page"
    
    def test_invalid_url(self):
        result = sanitize_url_for_logging("not a url at all")
        assert result == "[INVALID_URL]"


@pytest.mark.asyncio
class TestCrawlUrl:
    """Test URL crawling with retries."""
    
    async def test_successful_crawl(self):
        """Test successful URL crawl."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='<html><div class="content">Test</div></html>')
        mock_response.raise_for_status = Mock()
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)
        
        result = await crawl_url(mock_session, "https://example.com", None, 1, None)
        
        assert result['url'] == "https://example.com"
        assert result['suspicious'] is True  # Only 1 content div < threshold
        assert 0 <= result['confidence'] <= 1
    
    async def test_empty_url(self):
        """Test handling of empty URL."""
        mock_session = AsyncMock()
        result = await crawl_url(mock_session, "", None, 1, None)
        
        assert result['url'] == ""
        assert result['suspicious'] is None
        assert result['confidence'] == 0
    
    async def test_timeout_retry(self):
        """Test retry on timeout."""
        mock_session = AsyncMock()
        mock_session.get.side_effect = asyncio.TimeoutError()
        
        result = await crawl_url(mock_session, "https://slow.example.com", None, 0.1, None, max_retries=2)
        
        assert result['suspicious'] is None
        assert result['confidence'] == 0
        assert mock_session.get.call_count == 2
    
    async def test_http_error_retry(self):
        """Test retry on HTTP errors."""
        mock_session = AsyncMock()
        mock_session.get.side_effect = aiohttp.ClientError("Connection failed")
        
        result = await crawl_url(mock_session, "https://error.example.com", None, 0.1, None, max_retries=2)
        
        assert result['suspicious'] is None
        assert mock_session.get.call_count == 2


class TestWriteResults:
    """Test result writing with validation."""
    
    def test_write_valid_results(self):
        """Test writing valid results to CSV."""
        results = [
            {'url': 'https://example1.com', 'suspicious': True, 'confidence': 0.85},
            {'url': 'https://example2.com', 'suspicious': False, 'confidence': 0.15}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name
        
        try:
            write_results(results, temp_file)
            
            # Verify file was created and has content
            assert os.path.exists(temp_file)
            with open(temp_file, 'r') as f:
                content = f.read()
                assert 'url,suspicious,confidence' in content
                assert 'example1.com' in content
                assert 'example2.com' in content
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_write_empty_results(self):
        """Test handling of empty results."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name
        
        try:
            # Should not raise, just log warning
            write_results([], temp_file)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_deduplicate_urls(self):
        """Test URL deduplication."""
        results = [
            {'url': 'https://example.com', 'suspicious': True, 'confidence': 0.85},
            {'url': 'https://example.com', 'suspicious': False, 'confidence': 0.15},  # Duplicate
            {'url': 'https://example2.com', 'suspicious': True, 'confidence': 0.90}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name
        
        try:
            write_results(results, temp_file)
            
            with open(temp_file, 'r') as f:
                lines = f.readlines()
                # Should have header + 2 unique URLs
                assert len(lines) == 3
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_validate_confidence_range(self):
        """Test confidence value clamping."""
        results = [
            {'url': 'https://example.com', 'suspicious': True, 'confidence': 1.5},  # Out of range
            {'url': 'https://example2.com', 'suspicious': False, 'confidence': -0.2}  # Out of range
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name
        
        try:
            write_results(results, temp_file)
            
            # Should clamp values but still write
            assert os.path.exists(temp_file)
            with open(temp_file, 'r') as f:
                content = f.read()
                assert 'example.com' in content
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_skip_invalid_results(self):
        """Test skipping invalid result dictionaries."""
        results = [
            {'url': 'https://example.com', 'suspicious': True, 'confidence': 0.85},
            {'url': 'https://bad.com'},  # Missing required fields
            Exception("Some error"),  # Exception object
            {'url': 'https://example2.com', 'suspicious': False, 'confidence': 0.15}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name
        
        try:
            write_results(results, temp_file)
            
            with open(temp_file, 'r') as f:
                lines = f.readlines()
                # Should have header + 2 valid results
                assert len(lines) == 3
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
