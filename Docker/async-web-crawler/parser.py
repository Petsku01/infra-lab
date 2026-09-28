"""
Content parsing and analysis module
@author pk
"""

import logging
from typing import Dict, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Suspicion thresholds
SUSPICION_THRESHOLD = 5
CONFIDENCE_HIGH = 0.85
CONFIDENCE_LOW = 0.15


class ContentParser:
    """Parses HTML and performs heuristic content analysis."""
    
    def analyze(self, html: str, url: str) -> Dict[str, Any]:
        """
        Parse HTML and detect suspicious content.
        
        Args:
            html: HTML content
            url: Source URL (for logging)
            
        Returns:
            Dict with: suspicious, confidence, content_type, analysis
        """
        if not html:
            logger.warning(f"Empty HTML for {url}")
            return {
                'url': url,
                'suspicious': None,
                'confidence': 0.0,
                'content_type': 'empty',
                'analysis': 'No content'
            }
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract content sections
            content_divs = soup.find_all('div', class_='content')
            main_content = soup.find('main')
            article = soup.find('article')
            
            # Count meaningful content
            content_count = len(content_divs)
            has_main = main_content is not None
            has_article = article is not None
            
            # Heuristic analysis: suspicious if SPARSE unstructured content
            # Legitimate sites have semantic tags (main, article) or structured divs
            is_suspicious = content_count < SUSPICION_THRESHOLD and not has_main and not has_article
            # Higher confidence for well-structured legitimate content
            confidence = CONFIDENCE_HIGH if (has_main or has_article) else CONFIDENCE_LOW
            
            # Determine content type
            if content_count > 0:
                content_type = 'structured'
            elif has_main or has_article:
                content_type = 'semantic'
            else:
                content_type = 'unstructured'
            
            analysis = {
                'content_divs': content_count,
                'has_main': has_main,
                'has_article': has_article,
                'html_size': len(html),
                'text_size': len(soup.get_text()),
            }
            
            logger.debug(f"Analysis {url}: suspicious={is_suspicious}, type={content_type}")
            
            return {
                'url': url,
                'suspicious': is_suspicious,
                'confidence': confidence,
                'content_type': content_type,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Parse error for {url}: {e}")
            return {
                'url': url,
                'suspicious': None,
                'confidence': 0.0,
                'content_type': 'error',
                'analysis': str(e)
            }
