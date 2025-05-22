# Development Guide

## Development Environment Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker and Docker Compose
- Git

### Backend Setup (hermes-ingestor)

1. **Create Virtual Environment**
   ```bash
   cd hermes-ingestor
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Environment Configuration**
   Create a `.env` file:
   ```bash
   DEBUG=true
   API_KEY=dev-key
   ALLOWED_ORIGINS=http://localhost:3000
   QDRANT_HOST=localhost
   QDRANT_PORT=6333
   ```

4. **Start Qdrant**
   ```bash
   docker-compose up -d qdrant
   ```

5. **Run Development Server**
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

### Frontend Setup (hermes-ui)

1. **Install Dependencies**
   ```bash
   cd hermes-ui
   npm install
   ```

2. **Environment Configuration**
   Create a `.env` file:
   ```bash
   REACT_APP_API_URL=http://localhost:8000/api
   ```

3. **Run Development Server**
   ```bash
   npm start
   ```

## Code Style

### Python
- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Use flake8 for linting

```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
```

### JavaScript/React
- Use ESLint for linting
- Use Prettier for code formatting
- Follow Airbnb style guide

```bash
# Format code
npm run format

# Lint code
npm run lint
```

## Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=src tests/
```

### Frontend Tests
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage
```

## Git Workflow

1. **Branch Naming**
   - Feature: `feature/description`
   - Bugfix: `fix/description`
   - Hotfix: `hotfix/description`
   - Release: `release/version`

2. **Commit Messages**
   ```
   type(scope): description

   [optional body]

   [optional footer]
   ```

   Types:
   - feat: New feature
   - fix: Bug fix
   - docs: Documentation
   - style: Formatting
   - refactor: Code restructuring
   - test: Testing
   - chore: Maintenance

3. **Pull Request Process**
   - Create feature branch
   - Write tests
   - Update documentation
   - Submit PR
   - Address review comments
   - Merge after approval

## Debugging

### Backend Debugging
1. **Logging**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.debug("Debug message")
   logger.info("Info message")
   logger.error("Error message")
   ```

2. **Debug Mode**
   ```bash
   uvicorn src.main:app --reload --debug
   ```

### Frontend Debugging
1. **React Developer Tools**
   - Install Chrome extension
   - Use Components and Profiler tabs

2. **Redux DevTools**
   - Install Chrome extension
   - Monitor state changes

## Performance Optimization

### Backend
1. **Caching**
   - Use Redis for caching
   - Implement cache decorators

2. **Database**
   - Optimize queries
   - Use indexes
   - Monitor query performance

### Frontend
1. **Code Splitting**
   ```javascript
   const Component = React.lazy(() => import('./Component'));
   ```

2. **Memoization**
   ```javascript
   const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);
   ```

## Security Best Practices

1. **Input Validation**
   - Validate all user input
   - Use Pydantic models
   - Sanitize file uploads

2. **Authentication**
   - Use secure API keys
   - Implement rate limiting
   - Validate CORS origins

3. **Dependencies**
   - Regular security audits
   - Update dependencies
   - Use security scanning tools

## Documentation

### Code Documentation
- Use docstrings (Google style)
- Document all public APIs
- Include examples

### API Documentation
- Keep OpenAPI spec updated
- Document all endpoints
- Include request/response examples

## Release Process

1. **Version Bumping**
   ```bash
   # Backend
   bump2version patch  # or minor/major

   # Frontend
   npm version patch  # or minor/major
   ```

2. **Changelog**
   - Update CHANGELOG.md
   - Include all changes
   - Categorize changes

3. **Release Steps**
   - Create release branch
   - Update version numbers
   - Update documentation
   - Run all tests
   - Create release tag
   - Deploy to staging
   - Deploy to production

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines. 