"""
Storage module for crawler results
@author pk
"""

import logging
import csv
import os
import tempfile
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class CsvStorage:
    """Stores crawler results to CSV with atomic writes."""
    
    FIELDNAMES = ['url', 'suspicious', 'confidence', 'content_type']
    
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.results = []
    
    def add_result(self, result: Dict[str, Any]) -> None:
        """Add a result to storage."""
        if self._validate_result(result):
            self.results.append(result)
    
    def _validate_result(self, result: Dict[str, Any]) -> bool:
        """Validate result structure."""
        required_keys = {'url', 'suspicious', 'confidence'}
        if not all(key in result for key in required_keys):
            logger.warning(f"Invalid result missing keys: {result}")
            return False
        
        # Validate confidence range
        if not (0 <= result['confidence'] <= 1):
            logger.warning(f"Invalid confidence {result['confidence']}, clamping")
            result['confidence'] = max(0, min(1, result['confidence']))
        
        return True
    
    def save(self) -> bool:
        """
        Save results to CSV atomically.
        Writes to temp file first, then renames (atomic).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create output directory if needed
            os.makedirs(os.path.dirname(self.output_file) or '.', exist_ok=True)
            
            # Write to temp file first
            temp_fd, temp_path = tempfile.mkstemp(suffix='.csv', dir=os.path.dirname(self.output_file) or '.')
            
            try:
                with os.fdopen(temp_fd, 'w', newline='') as temp_file:
                    writer = csv.DictWriter(temp_file, fieldnames=self.FIELDNAMES)
                    writer.writeheader()
                    
                    # Deduplicate URLs
                    seen_urls = set()
                    written_count = 0
                    
                    for result in self.results:
                        if result['url'] in seen_urls:
                            logger.debug(f"Skipping duplicate: {result['url']}")
                            continue
                        
                        seen_urls.add(result['url'])
                        
                        # Only write fields in FIELDNAMES
                        row = {key: result.get(key) for key in self.FIELDNAMES}
                        writer.writerow(row)
                        written_count += 1
                
                # Atomic rename (Windows/Unix compatible)
                # os.replace() is atomic on both Windows and Unix (Python 3.8+)
                os.replace(temp_path, self.output_file)
                
                logger.info(f"Saved {written_count} results to {self.output_file}")
                return True
                
            except Exception as e:
                # Clean up temp file on error
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
                raise e
                
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return False
