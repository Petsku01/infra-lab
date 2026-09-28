"""
Test suite for process.py data processing script
@author pk
"""

import json
import os
import tempfile
import shutil
from pathlib import Path
import pytest
from process import process_data


class TestProcessData:
    """Test cases for process_data function"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with logs and data directories"""
        temp_dir = tempfile.mkdtemp()
        logs_dir = Path(temp_dir) / 'logs'
        data_dir = Path(temp_dir) / 'data'
        logs_dir.mkdir()
        data_dir.mkdir()
        
        # Save current directory and change to temp
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        yield temp_dir, logs_dir, data_dir
        
        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(temp_dir)
    
    def test_successful_processing(self, temp_workspace):
        """Test successful data processing with valid input"""
        temp_dir, logs_dir, data_dir = temp_workspace
        
        # Create input file
        api_log = logs_dir / 'api.log'
        api_log.write_text('Test API data')
        
        # Process
        process_data()
        
        # Verify output
        output_file = data_dir / 'output.json'
        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert 'timestamp' in data
        assert data['message'] == 'Processed by Python script'
        assert data['status'] == 'success'
    
    def test_missing_input_file(self, temp_workspace, capsys):
        """Test handling of missing input file"""
        temp_dir, logs_dir, data_dir = temp_workspace
        
        # Don't create input file
        process_data()
        
        # Verify error message
        captured = capsys.readouterr()
        assert 'Error' in captured.out
        assert 'File not found' in captured.out
    
    def test_empty_input_file(self, temp_workspace):
        """Test processing of empty input file"""
        temp_dir, logs_dir, data_dir = temp_workspace
        
        # Create empty input file
        api_log = logs_dir / 'api.log'
        api_log.write_text('')
        
        # Process - should succeed with empty data
        process_data()
        
        output_file = data_dir / 'output.json'
        assert output_file.exists()
    
    def test_large_input_file(self, temp_workspace):
        """Test processing of large input file"""
        temp_dir, logs_dir, data_dir = temp_workspace
        
        # Create large input file (10KB)
        api_log = logs_dir / 'api.log'
        api_log.write_text('X' * 10000)
        
        process_data()
        
        output_file = data_dir / 'output.json'
        assert output_file.exists()
