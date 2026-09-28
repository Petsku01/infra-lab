#!/usr/bin/env python3
"""
Data processing script
@author pk
"""

import json
from datetime import datetime, timezone
from typing import NoReturn

# Simulate processing some data
def process_data() -> None:
    """Process API data from log file and create output JSON."""
    # Load the API data saved by the Bash script
    try:
        with open('logs/api.log', 'r', encoding='utf-8') as f:
            api_data = f.read()
        print(f"Processing API data: {api_data.strip()}")
        
        # Create a sample JSON file with proper timezone
        data = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z"),
            "message": "Processed by Python script",
            "status": "success"
        }
        with open('data/output.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print("Created output.json with processed data")
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"Error during processing: {str(e)}")

if __name__ == "__main__":
    process_data()