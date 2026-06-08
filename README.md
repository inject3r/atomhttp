<p align="center">
  <img src="https://inject3r.github.io/atomhttp/logo.jpg" alt="AtomHTTP Logo" width="350">
</p>

# AtomHTTP

A professional, feature-rich asynchronous HTTP client for Python — designed for developers who need reliability, flexibility, and performance.

**[Full Documentation](https://inject3r.github.io/atomhttp)** — Complete API reference, advanced guides, and examples

<br/>

## Features

- **Full HTTP Method Support**: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS with async/await syntax
- **Request & Response Interceptors**: Modify requests before sending and responses before returning
- **Upload & Download Progress Tracking**: Real-time callbacks for monitoring data transfer
- **FormData Support**: Multipart/form-data and URL-encoded form handling with file uploads
- **Multiple Response Types**: JSON (auto-parsed), text, blob, arraybuffer, and stream
- **Concurrent Request Helpers**: Execute multiple requests in parallel with `all()` and `spread()`
- **Base URL Configuration**: Set a base URL once and use relative paths
- **Automatic JSON Serialization**: No need to manually encode/decode JSON
- **Authentication**: Basic Auth and Bearer Token support
- **Comprehensive Error Handling**: Typed exceptions with standardized error codes
- **Timeout & Redirect Control**: Configurable timeouts and maximum redirect limits
- **Keep-Alive & Connection Pooling**: Reuse connections for better performance
- **Proxy Support**: Route requests through HTTP proxies
- **Unix Socket Path Support**: Connect via Unix domain sockets
- **Size Limits**: Configure maximum request body and response content lengths
- **Status Code Validation**: Custom validation functions for HTTP status codes
- **CSRF Protection**: Built-in support for XSRF token headers
- **Automatic Decompression**: Handles gzip and deflate compressed responses
- **Mock Adapter for Testing**: Simulate responses without network calls
- **Type Hints**: Full typing support for excellent IDE autocompletion

## Installation

```bash
pip install atomhttp
```

With development dependencies:

```bash
pip install atomhttp[dev]
```

## Quick Start

```python
import asyncio
from atomhttp import AtomHTTP

async def main():
    client = AtomHTTP({'baseURL': 'https://api.example.com'})
    response = await client.get('/users')
    print(response.status, response.data)
    await client.close()

asyncio.run(main())
```

## Documentation

For complete documentation, API reference, and advanced usage examples, visit:

**[https://inject3r.github.io/atomhttp](https://inject3r.github.io/atomhttp)**

The documentation includes:

- Detailed API reference for all classes and methods
- Advanced usage patterns and best practices
- Configuration options and their effects
- Error handling strategies
- Migration guides from other HTTP clients

## Requirements

- Python 3.8+
- aiohttp 3.8.0+

## Running Tests

```bash
# Run all tests with coverage
./scripts/tests.sh

# Clean test output files
./scripts/test_clean.sh
```

## License

This project is licensed under the MIT License.

## Author

**Abolfazl Hosseini**

- Email: tryuzr@gmail.com
- GitHub: [@inject3r](https://github.com/inject3r)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- [aiohttp](https://docs.aiohttp.org/) - Async HTTP client/server framework
- All contributors and users of this project
