"""
Business logic tests for crawler modules.
Tests edge cases, error conditions, and data validation.
@author pk
"""

import pytest
import tempfile
import os
from pathlib import Path
from storage import CsvStorage
from validators import InputValidator
from parser import ContentParser


class TestStorageBusinessLogic:
    """Test business logic for storage module."""
    
    def test_atomic_write_prevents_partial_files(self):
        """Verify atomic writes prevent partial file corruption."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'test.csv')
            storage = CsvStorage(output_file)
            
            # Add valid results
            storage.add_result({
                'url': 'https://example.com',
                'suspicious': False,
                'confidence': 0.8
            })
            
            # File should not exist until save() is called
            assert not os.path.exists(output_file)
            
            # Save should create file atomically
            assert storage.save() is True
            assert os.path.exists(output_file)
    
    def test_duplicate_url_deduplication(self):
        """Verify duplicate URLs are deduplicated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'test.csv')
            storage = CsvStorage(output_file)
            
            # Add same URL multiple times
            for _ in range(3):
                storage.add_result({
                    'url': 'https://example.com',
                    'suspicious': False,
                    'confidence': 0.9
                })
            
            storage.save()
            
            # Read file and verify only one entry
            with open(output_file, 'r') as f:
                lines = f.readlines()
                assert len(lines) == 2  # Header + 1 data row
    
    def test_invalid_confidence_is_clamped(self):
        """Verify confidence values are clamped to [0, 1]."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'test.csv')
            storage = CsvStorage(output_file)
            
            # Add result with invalid confidence
            result = {
                'url': 'https://example.com',
                'suspicious': False,
                'confidence': 1.5  # Invalid - too high
            }
            
            storage.add_result(result)
            
            # Confidence should be clamped to 1.0
            assert result['confidence'] == 1.0
    
    def test_missing_required_fields_rejected(self):
        """Verify results missing required fields are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'test.csv')
            storage = CsvStorage(output_file)
            
            # Add result missing 'confidence'
            storage.add_result({
                'url': 'https://example.com',
                'suspicious': False
            })
            
            # No results should be stored
            assert len(storage.results) == 0
    
    def test_save_failure_cleanup(self):
        """Verify temp files are cleaned up on save failure."""
        # Use invalid path to force failure
        storage = CsvStorage('/invalid/path/that/does/not/exist/test.csv')
        storage.add_result({
            'url': 'https://example.com',
            'suspicious': False,
            'confidence': 0.8
        })
        
        # Save should fail gracefully
        assert storage.save() is False


class TestValidatorBusinessLogic:
    """Test business logic for input validation."""
    
    def test_empty_url_list_rejected(self):
        """Verify empty URL lists are rejected."""
        validator = InputValidator()
        
        result = validator.validate_urls([])
        
        assert result['valid'] is False
        assert 'empty' in result['error'].lower()
    
    def test_malformed_urls_filtered(self):
        """Verify malformed URLs are filtered out."""
        validator = InputValidator()
        
        urls = [
            'https://valid.com',
            'not-a-url',
            'ftp://unsupported.com',
            'https://another-valid.com'
        ]
        
        result = validator.validate_urls(urls)
        
        assert result['valid'] is True
        assert len(result['urls']) == 2
        assert 'https://valid.com' in result['urls']
        assert 'https://another-valid.com' in result['urls']
    
    def test_localhost_urls_rejected(self):
        """Verify localhost URLs are rejected in production."""
        validator = InputValidator(allow_localhost=False)
        
        urls = [
            'http://localhost:8080',
            'https://127.0.0.1',
            'https://example.com'
        ]
        
        result = validator.validate_urls(urls)
        
        assert len(result['urls']) == 1
        assert 'https://example.com' in result['urls']
    
    def test_maximum_url_limit(self):
        """Verify maximum URL limit is enforced."""
        validator = InputValidator(max_urls=5)
        
        urls = [f'https://example{i}.com' for i in range(10)]
        
        result = validator.validate_urls(urls)
        
        assert len(result['urls']) <= 5


class TestParserBusinessLogic:
    """Test business logic for content parsing."""
    
    def test_empty_html_handled_gracefully(self):
        """Verify empty HTML content is handled gracefully."""
        parser = ContentParser()
        
        result = parser.parse('')
        
        assert result['suspicious'] is False
        assert result['confidence'] >= 0
        assert result['patterns'] == []
    
    def test_multiple_patterns_increase_confidence(self):
        """Verify multiple suspicious patterns increase confidence."""
        parser = ContentParser()
        
        # HTML with multiple suspicious patterns
        html = """
        <html>
            <script>eval(atob('encoded'))</script>
            <iframe src="http://malicious.com"></iframe>
            <form action="http://phishing.com">
                <input type="password" name="pass">
            </form>
        </html>
        """
        
        result = parser.parse(html)
        
        assert result['suspicious'] is True
        assert result['confidence'] > 0.5
        assert len(result['patterns']) >= 2
    
    def test_benign_content_low_confidence(self):
        """Verify benign content has low suspicion confidence."""
        parser = ContentParser()
        
        html = """
        <html>
            <head><title>Normal Page</title></head>
            <body>
                <h1>Welcome</h1>
                <p>This is a normal page with regular content.</p>
            </body>
        </html>
        """
        
        result = parser.parse(html)
        
        assert result['suspicious'] is False
        assert result['confidence'] < 0.3
    
    def test_encoded_scripts_detected(self):
        """Verify base64-encoded scripts are detected."""
        parser = ContentParser()
        
        html = '<script>eval(atob("ZXZpbChhdG9iKCJleGVjKCkiKSk="))</script>'
        
        result = parser.parse(html)
        
        assert result['suspicious'] is True
        assert any('encoded' in p.lower() for p in result['patterns'])
    
    def test_html_with_only_whitespace(self):
        """Verify HTML with only whitespace is handled."""
        parser = ContentParser()
        
        result = parser.parse('   \n\t\r\n   ')
        
        assert result['suspicious'] is False
        assert result['confidence'] == 0.0


@pytest.mark.integration
class TestIntegrationBusinessLogic:
    """Integration tests for business logic across modules."""
    
    def test_end_to_end_suspicious_url_workflow(self):
        """Test complete workflow from validation to storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'results.csv')
            
            # Validate URLs
            validator = InputValidator()
            url_result = validator.validate_urls(['https://example.com'])
            assert url_result['valid'] is True
            
            # Parse suspicious content
            parser = ContentParser()
            html = '<script>eval(atob("malicious"))</script>'
            parse_result = parser.parse(html)
            
            # Store results
            storage = CsvStorage(output_file)
            storage.add_result({
                'url': url_result['urls'][0],
                'suspicious': parse_result['suspicious'],
                'confidence': parse_result['confidence']
            })
            
            assert storage.save() is True
            assert os.path.exists(output_file)
    
    def test_batch_processing_performance(self):
        """Test performance with batch URL processing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'batch_results.csv')
            storage = CsvStorage(output_file)
            
            # Process 1000 URLs
            for i in range(1000):
                storage.add_result({
                    'url': f'https://example{i}.com',
                    'suspicious': i % 2 == 0,
                    'confidence': 0.5 + (i % 50) / 100
                })
            
            # Verify deduplication and save work correctly
            import time
            start = time.time()
            assert storage.save() is True
            duration = time.time() - start
            
            # Should complete in reasonable time (< 1 second)
            assert duration < 1.0
