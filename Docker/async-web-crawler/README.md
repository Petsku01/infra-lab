# Async Web Crawler

A high-performance asynchronous web crawler built with Python, designed for concurrent URL fetching and content analysis.

## Overview

This Docker container provides a production-ready web crawling service that efficiently fetches web pages, analyzes content, validates URLs, and exports results to CSV format. Built with aiohttp for async HTTP operations and BeautifulSoup4 for HTML parsing.

## Features

- **Asynchronous HTTP Fetching**: Concurrent request handling with configurable retry logic
- **URL Validation**: Validates URL schemes and network locations before processing
- **Content Analysis**: Heuristic-based detection for suspicious or low-quality content
- **Robots.txt Compliance**: Respects robots.txt directives with timeout protection
- **CSV Export**: Atomic file operations with deduplication and error handling
- **Observability**: Structured logging for monitoring and debugging

## Architecture

```
async-web-crawler/
├── main.py              # Entry point with signal handling
├── crawler.py           # Orchestration and concurrent request management
├── fetcher.py           # HTTP client with retry logic and URL validation
├── parser.py            # HTML content analysis and heuristics
├── storage.py           # Atomic CSV operations with deduplication
├── validators.py        # URL validation and robots.txt checking
├── observability.py     # Logging configuration
└── requirements.txt     # Python dependencies
```

## Building the Container

```bash
docker build -t async-web-crawler:latest ./async-web-crawler
```

## Usage

### Basic Usage

Crawl a single URL (default: https://example.com):

```bash
docker run --rm async-web-crawler:latest
```

### Crawl Multiple URLs

```bash
docker run --rm async-web-crawler:latest \
  --urls "https://example.com,https://example.org,https://example.net"
```

### Custom Output Location

```bash
docker run --rm \
  -v /path/to/output:/app/output \
  async-web-crawler:latest \
  --urls "https://example.com" \
  --output /app/output/results.csv
```

### Configure Concurrency

```bash
docker run --rm async-web-crawler:latest \
  --urls "https://example.com,https://example.org" \
  --max-concurrent 10
```

## Command-Line Options

- `--urls`: Comma-separated list of URLs to crawl (default: https://example.com)
- `--output`: Output CSV file path (default: /app/output/crawled_urls.csv)
- `--max-concurrent`: Maximum concurrent requests (default: 5)

## Output Format

Results are saved to CSV with the following columns:

- **url**: The crawled URL
- **status_code**: HTTP status code (200, 404, etc.)
- **content_length**: Response size in bytes
- **title**: Page title extracted from HTML
- **suspicious**: Boolean flag for low-quality content detection
- **timestamp**: ISO 8601 timestamp of the crawl

## Error Handling

The crawler handles various error scenarios:

- **Network Errors**: Retries with exponential backoff
- **Timeout Errors**: Configurable timeout with fallback
- **Invalid URLs**: Pre-validation prevents malformed URL processing
- **Robots.txt Violations**: Skips URLs disallowed by robots.txt
- **Parse Errors**: Logs errors without stopping the crawl

## Performance Considerations

- Default concurrency: 5 simultaneous requests
- Connection timeout: 10 seconds per request
- Retry logic: 3 attempts with exponential backoff
- Memory efficient: Streams large responses

## Security Features

- Non-root user execution (appuser:appgroup)
- Read-only filesystem where possible
- URL scheme validation (http/https only)
- Timeout protection on all network operations

## Environment Variables

- `PYTHONUNBUFFERED=1`: Enable real-time logging output
- `PYTHONDONTWRITEBYTECODE=1`: Prevent .pyc file generation

## Monitoring

Logs are structured with severity levels:

- **INFO**: Successful operations and progress updates
- **WARNING**: Retries and recoverable errors
- **ERROR**: Failed requests and critical errors

View logs in real-time:

```bash
docker logs -f <container_id>
```

## Health Check

Verify the container is operational:

```bash
docker run --rm async-web-crawler:latest --help
```

## Troubleshooting

### Issue: No output file generated

**Solution**: Ensure the output directory is mounted and writable:

```bash
docker run --rm -v $(pwd)/output:/app/output async-web-crawler:latest
```

### Issue: Connection timeouts

**Solution**: Increase timeout values or reduce concurrency:

```bash
docker run --rm async-web-crawler:latest --max-concurrent 2
```

### Issue: Empty results

**Solution**: Check logs for URL validation or robots.txt violations:

```bash
docker logs <container_id>
```

## Dependencies

- Python 3.12 (Alpine-based)
- aiohttp 3.11.11 (async HTTP client)
- beautifulsoup4 4.12.3 (HTML parsing)
- csv (standard library)
- asyncio (standard library)

## Version

Current version: 1.0.0

## License

See project root for license information.

## Contributing

Bug fixes and feature enhancements welcome. Ensure all changes pass linting (black, flake8, pylint) before submission.
