# Contributing to AtomHTTP

First off, thank you for considering contributing to AtomHTTP! It's people like you that make AtomHTTP such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue tracker as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title** for the issue to identify the problem
- **Describe the exact steps which reproduce the problem** in as many details as possible
- **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead and why**
- **Include Python version and operating system information**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement** in as many details as possible
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior** and **explain which behavior you expected to see instead**
- **Explain why this enhancement would be useful** to most AtomHTTP users

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Follow the Python style guidelines
- Include appropriate test cases
- Update documentation for any new features or changes
- Ensure all tests pass before submitting

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Setting Up Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork locally**:

```bash
git clone https://github.com/inject3r/atomhttp.git
cd atomhttp
```

3. **Install development dependencies**:

```bash
pip install -e ".[dev]"
```

4. **Create a branch for your changes**:

```bash
git checkout -b feature/your-feature-name
```

### Running Tests

Run the test suite to ensure everything is working:

```bash
# Run all tests
./scripts/tests.sh

# Run specific test file
pytest tests/test_client.py -v

# Run with coverage report
pytest --cov=atomhttp tests/
```

### Code Style

AtomHTTP follows PEP 8 with some adjustments. We use:

- **Black** for code formatting (line length: 100)
- **isort** for import sorting
- **mypy** for type checking
- **ruff** for linting

Before submitting a pull request, run:

```bash
# Format code
black .

# Sort imports
isort .

# Run type checker
mypy atomhttp

# Run linter
ruff check .
```

### Testing Guidelines

- Write tests for any new functionality
- Update existing tests when modifying behavior
- Aim for high test coverage (new code should have >90% coverage)
- Use pytest fixtures for common setup
- Mark async tests with `@pytest.mark.asyncio`

### Documentation

- Update docstrings for any modified functions or classes
- Update the README.md if you change user-facing features
- Add examples for new functionality
- Keep the documentation clear and concise

## Project Structure

```
atomhttp/
├── atomhttp/           # Main package source code
│   ├── core/           # Core classes (RequestConfig, Response, etc.)
│   ├── adapters/       # HTTP adapters (HTTPAdapter, MockAdapter)
│   ├── interceptors/   # Interceptor management
│   ├── transforms/     # Request/response transformers
│   ├── errors/         # Exception classes
│   ├── auth/           # Authentication handlers
│   ├── progress/       # Progress tracking
│   └── utils/          # Utility functions
├── tests/              # Test suite
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── scripts/            # Utility scripts (tests.sh, test_clean.sh)
└── examples/           # Example usage code
```

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Example: `feat: add support for custom headers in redirects`

## Release Process

1. Ensure all tests pass
2. Update version in `pyproject.toml` and `atomhttp/__init__.py`
3. Update CHANGELOG.md
4. Create a pull request for the release
5. After merging, tag the release: `git tag -a v2.0.0 -m "Version 2.0.0"`
6. Push the tag: `git push origin v2.0.0`

## Getting Help

- **GitHub Issues**: Use for bug reports and feature requests
- **Documentation**: [https://inject3r.github.io/atomhttp](https://inject3r.github.io/atomhttp)
- **Email**: tryuzr@gmail.com

## Additional Notes

### Issue and Pull Request Labels

| Label              | Description                      |
| ------------------ | -------------------------------- |
| `bug`              | Something isn't working          |
| `enhancement`      | New feature or request           |
| `documentation`    | Documentation improvements       |
| `good first issue` | Good for newcomers               |
| `help wanted`      | Extra attention needed           |
| `question`         | Further information is requested |

### Recognition

Contributors who submit accepted pull requests will be added to the README.md acknowledgments section.

---

Thank you for contributing to AtomHTTP! 🚀
