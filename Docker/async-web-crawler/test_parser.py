"""
Business logic tests for content analysis
@author pk
"""

import pytest
from parser import ContentParser


class TestContentAnalysis:
    """Test heuristic content detection."""
    
    def test_suspicious_minimal_content(self):
        """Detect suspicious pages with minimal content."""
        parser = ContentParser()
        
        # Minimal HTML with no content divs
        html = '<html><body><h1>Title</h1><p>Minimal text</p></body></html>'
        result = parser.analyze(html, 'http://example.com')
        
        assert result['suspicious'] == True
        assert result['confidence'] == 0.85
        assert result['content_type'] != 'structured'
    
    def test_legitimate_structured_content(self):
        """Detect legitimate pages with structured content."""
        parser = ContentParser()
        
        # Rich content with multiple divs
        html = '''<html><body>
            <div class="content">Article 1</div>
            <div class="content">Article 2</div>
            <div class="content">Article 3</div>
            <div class="content">Article 4</div>
            <div class="content">Article 5</div>
            <div class="content">Article 6</div>
        </body></html>'''
        result = parser.analyze(html, 'http://example.com')
        
        assert result['suspicious'] == False
        assert result['confidence'] == 0.15
        assert result['content_type'] == 'structured'
    
    def test_semantic_html_content(self):
        """Detect pages with semantic HTML elements."""
        parser = ContentParser()
        
        html = '''<html><body>
            <main>
                <article>Long form content here</article>
            </main>
        </body></html>'''
        result = parser.analyze(html, 'http://example.com')
        
        assert result['suspicious'] == False
        assert result['content_type'] == 'semantic'
    
    def test_empty_html(self):
        """Handle empty HTML gracefully."""
        parser = ContentParser()
        result = parser.analyze('', 'http://example.com')
        
        assert result['suspicious'] is None
        assert result['content_type'] == 'empty'
    
    def test_malformed_html(self):
        """Handle malformed HTML gracefully."""
        parser = ContentParser()
        html = '<html><body><div unclosed'
        result = parser.analyze(html, 'http://example.com')
        
        # Should not crash
        assert 'suspicious' in result
        assert result['url'] == 'http://example.com'
    
    def test_analysis_metadata(self):
        """Verify analysis metadata is captured."""
        parser = ContentParser()
        html = '<html><body><div class="content">Test</div></body></html>'
        result = parser.analyze(html, 'http://example.com')
        
        assert 'analysis' in result
        assert 'content_divs' in result['analysis']
        assert 'has_main' in result['analysis']
        assert 'html_size' in result['analysis']
        assert result['analysis']['html_size'] > 0
