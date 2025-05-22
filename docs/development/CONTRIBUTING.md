# Contributing to Hermes

Thank you for your interest in contributing to Hermes! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read it before contributing.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in the Issues section
2. Use the bug report template
3. Include detailed steps to reproduce
4. Include expected and actual behavior
5. Include relevant logs and screenshots

### Suggesting Features

1. Check if the feature has already been suggested
2. Use the feature request template
3. Describe the feature in detail
4. Explain why it would be useful
5. Include any relevant examples

### Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write or update tests
5. Update documentation
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- Docker and Docker Compose
- Git

### Setup Steps

1. Fork and clone the repository
2. Set up the development environment:
   ```bash
   # Backend
   cd hermes-ingestor
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt

   # Frontend
   cd ../hermes-ui
   npm install
   ```

3. Create a `.env` file in both directories
4. Start the development servers

## Coding Standards

### Python

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Use Black for formatting
- Use isort for import sorting
- Use flake8 for linting

### JavaScript/React

- Follow Airbnb style guide
- Use ESLint
- Use Prettier
- Write JSDoc comments
- Use TypeScript where possible

### Git

- Write clear commit messages
- Use conventional commits
- Keep commits focused and atomic
- Rebase before submitting PR

## Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_api.py

# Run with coverage
pytest --cov=src tests/
```

### Frontend Tests

```bash
# Run all tests
npm test

# Run specific test
npm test -- -t "test name"

# Run with coverage
npm test -- --coverage
```

## Documentation

### Code Documentation

- Document all public APIs
- Include examples
- Keep docstrings up to date
- Document configuration options

### API Documentation

- Keep OpenAPI spec updated
- Document all endpoints
- Include request/response examples
- Document error responses

## Review Process

1. All PRs require at least one review
2. CI must pass
3. Code coverage must not decrease
4. Documentation must be updated
5. Tests must be added/updated

## Release Process

1. Version bump
2. Update changelog
3. Create release branch
4. Run all tests
5. Create release tag
6. Deploy to staging
7. Deploy to production

## Communication

- Use GitHub Issues for bugs and features
- Use GitHub Discussions for questions
- Use GitHub Projects for tracking
- Join our Slack channel

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License. 