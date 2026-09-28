# Integration Tests

A containerized testing environment for running integration tests and automated scripts with Python and common utilities.

## Overview

This Docker container provides a lightweight Ubuntu-based environment pre-configured with Python 3, pip, and essential development tools for running integration tests, scripts, and automated workflows.

## Features

- **Python 3.10**: Full Python environment with pip package manager
- **Development Tools**: curl, jq, nano, git for scripting and debugging
- **Lightweight**: Ubuntu 22.04 base with minimal footprint (287 MB)
- **Flexible**: Run arbitrary Python scripts or shell commands
- **CI/CD Ready**: Designed for continuous integration pipelines

## Architecture

```
integration-tests/
├── process.py           # Example Python processing script
├── test_process.py      # Example test file
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container definition
└── .dockerignore        # Build exclusions
```

## Building the Container

```bash
docker build -t integration-tests:latest ./integration-tests
```

## Usage

### Run Python Scripts

Execute a Python script from the host:

```bash
docker run --rm -v $(pwd):/app integration-tests:latest python3 /app/your_script.py
```

### Run Tests

Execute test suite:

```bash
docker run --rm -v $(pwd):/app integration-tests:latest python3 -m pytest /app/tests/
```

### Interactive Shell

Start an interactive session for debugging:

```bash
docker run -it --rm integration-tests:latest /bin/bash
```

### Check Python Version

Verify Python installation:

```bash
docker run --rm integration-tests:latest python3 --version
```

### Install Additional Packages

Install packages at runtime:

```bash
docker run --rm integration-tests:latest pip install requests pytest
```

Or mount requirements file:

```bash
docker run --rm -v $(pwd)/requirements.txt:/tmp/requirements.txt \
  integration-tests:latest pip install -r /tmp/requirements.txt
```

## Pre-installed Tools

### Python Ecosystem
- **python3**: Python 3.10.12
- **pip**: 22.0.2 (Python package manager)

### System Utilities
- **curl**: HTTP client for API testing
- **jq**: JSON processor for parsing responses
- **nano**: Text editor
- **git**: Version control (for cloning test repositories)

## Example: Running Integration Tests

### Directory Structure
```
your-project/
├── tests/
│   ├── test_api.py
│   ├── test_database.py
│   └── test_integration.py
└── requirements.txt
```

### Execute All Tests

```bash
docker run --rm \
  -v $(pwd):/app \
  -w /app \
  integration-tests:latest \
  python3 -m pytest tests/ -v
```

## Example: Processing Scripts

The container includes `process.py` as an example script demonstrating:

- File I/O operations
- Data processing patterns
- Error handling
- Logging

Run the example:

```bash
docker run --rm integration-tests:latest python3 /app/process.py
```

## Environment Variables

- `DEBIAN_FRONTEND=noninteractive`: Non-interactive package installation
- `PYTHONUNBUFFERED=1`: Real-time Python output (no buffering)
- `PYTHONDONTWRITEBYTECODE=1`: Prevent .pyc file generation

## CI/CD Integration

### GitHub Actions Example

```yaml
jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build test container
        run: docker build -t integration-tests:latest ./integration-tests
      
      - name: Run integration tests
        run: |
          docker run --rm \
            -v ${{ github.workspace }}:/app \
            integration-tests:latest \
            python3 -m pytest /app/tests/ -v
```

### GitLab CI Example

```yaml
integration-tests:
  image: integration-tests:latest
  script:
    - python3 -m pytest tests/ -v
  artifacts:
    reports:
      junit: test-results.xml
```

## Use Cases

### API Testing
Test REST APIs with requests library:

```bash
docker run --rm -v $(pwd):/app integration-tests:latest \
  python3 -c "import requests; print(requests.get('https://api.example.com').json())"
```

### Data Validation
Validate CSV/JSON data files:

```bash
docker run --rm -v $(pwd):/app integration-tests:latest \
  python3 /app/validate_data.py --input /app/data.csv
```

### Database Integration Tests
Connect to databases for integration testing:

```bash
docker run --rm \
  --network host \
  -v $(pwd):/app \
  integration-tests:latest \
  python3 /app/test_database_integration.py
```

### Smoke Tests
Quick health checks after deployment:

```bash
docker run --rm integration-tests:latest \
  curl -f http://your-service:8080/health || exit 1
```

## Mounting Volumes

### Mount Current Directory

```bash
docker run --rm -v $(pwd):/app -w /app integration-tests:latest python3 script.py
```

### Mount Multiple Directories

```bash
docker run --rm \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/tests:/app/tests \
  integration-tests:latest \
  python3 -m pytest /app/tests/
```

### Read-Only Mounts

```bash
docker run --rm -v $(pwd):/app:ro integration-tests:latest python3 /app/read_only_script.py
```

## Networking

### Connect to Other Containers

```bash
docker network create test-network
docker run -d --network test-network --name database postgres:latest
docker run --rm --network test-network integration-tests:latest \
  python3 /app/test_with_database.py
```

### Access Host Services

```bash
docker run --rm --network host integration-tests:latest \
  curl http://localhost:8080/api/test
```

## Performance Considerations

- **Startup Time**: < 1 second
- **Memory Footprint**: ~50-100 MB base + script requirements
- **Build Time**: ~30 seconds (cached layers)
- **Image Size**: 287 MB

## Security Features

- Minimal base image (Ubuntu 22.04)
- No unnecessary services running
- Cleaned apt cache (no leftover package lists)
- Non-interactive installation (no prompts)

## Troubleshooting

### Issue: Python module not found

**Solution**: Install required packages:

```bash
docker run --rm integration-tests:latest pip install module-name
```

Or add to requirements.txt and rebuild:

```bash
echo "module-name==version" >> integration-tests/requirements.txt
docker build -t integration-tests:latest ./integration-tests
```

### Issue: Permission denied on mounted volumes

**Solution**: Ensure files have appropriate permissions:

```bash
chmod -R 755 your-script-directory
docker run --rm -v $(pwd):/app integration-tests:latest python3 /app/script.py
```

### Issue: Cannot connect to network services

**Solution**: Use `--network host` or connect containers to same network:

```bash
docker run --rm --network host integration-tests:latest curl localhost:8080
```

## Example Test Script

Create a simple test file `test_example.py`:

```python
import pytest

def test_addition():
    assert 1 + 1 == 2

def test_string_operations():
    assert "hello".upper() == "HELLO"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

Run it:

```bash
docker run --rm -v $(pwd):/app integration-tests:latest python3 /app/test_example.py
```

## Container Specifications

- **Base Image**: ubuntu:22.04
- **Size**: 287 MB
- **Python**: 3.10.12
- **Package Manager**: pip 22.0.2
- **Shell**: /bin/bash

## Exit Codes

- **0**: Tests passed / script executed successfully
- **1**: Tests failed / script error
- **2**: Command not found or syntax error

## Version

Current version: 1.0.0

## License

See project root for license information.

## Contributing

Contributions welcome. When adding new system packages, update Dockerfile and ensure image size remains reasonable.
