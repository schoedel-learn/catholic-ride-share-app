# Contributing to Catholic Ride Share

Thank you for your interest in contributing to Catholic Ride Share! This project serves the Catholic community by ensuring transportation is never a barrier to participating in church life.

## Code of Conduct

All interactions in this project — Issues, Discussions, Pull Requests, and beyond — are governed by our [Code of Conduct](CODE_OF_CONDUCT.md). In short: be respectful, be charitable, and remember that everyone here is volunteering their time for a worthy mission.

## Security First

This project serves a non-profit organization and handles sensitive user data. Security is our top priority.

### Before Contributing

1. **Read our [Security Policy](SECURITY.md)** - Understand our security practices
2. **Never commit secrets** - API keys, passwords, tokens must stay in `.env` files
3. **Review security checklist** below before submitting PRs
4. **Report vulnerabilities privately** - Don't create public issues for security bugs

### Security Checklist for All PRs

Before submitting your pull request, verify:

- [ ] No secrets, API keys, or credentials are committed
- [ ] All user inputs are validated and sanitized
- [ ] SQL injection prevention (use SQLAlchemy ORM, no raw SQL)
- [ ] XSS prevention (sanitize user-generated content)
- [ ] Authentication/authorization checks are in place
- [ ] Password handling uses bcrypt (never plaintext)
- [ ] Sensitive data is encrypted at rest and in transit
- [ ] Error messages don't expose sensitive information
- [ ] Rate limiting considered for public endpoints
- [ ] CORS settings are appropriate
- [ ] Dependencies are from trusted sources
- [ ] No hardcoded URLs, IPs, or configuration values

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, browser, etc.)

### Suggesting Features

1. Search existing issues for similar suggestions
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach

### Code Contributions

1. **Fork the repository**
   ```bash
   git fork https://github.com/yourusername/catholic-ride-share
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the code style guidelines
   - Write or update tests
   - Update documentation as needed

4. **Test your changes**
   ```bash
   cd backend
   pytest
   black .
   isort .
   flake8 .
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add feature: description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Describe what changes you made and why
   - Reference any related issues
   - Ensure all tests pass

## Development Setup

See README.md for detailed setup instructions.

Quick start:
```bash
# Clone your fork
git clone https://github.com/yourusername/catholic-ride-share
cd catholic-ride-share

# Set up backend
cd backend
cp .env.example .env
# Edit .env with your settings

# Run with Docker
docker-compose up -d
```

## Code Style Guidelines

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints
- Format with Black (line length 100)
- Sort imports with isort
- Maximum complexity: keep functions focused and small

### Git Commit Messages
- Use present tense ("Add feature" not "Added feature")
- Keep first line under 50 characters
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Reference issues and PRs when relevant

Example:
```
Add driver verification endpoint

- Implement document upload
- Add verification status tracking
- Create admin review interface

Closes #123
```

## Testing

- Write tests for all new features
- Ensure existing tests pass
- Aim for >80% code coverage
- Include both unit and integration tests

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_auth.py
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions and classes
- Update API documentation as needed
- Create or update docs/ files for architecture changes

## Review Process

1. Automated tests must pass
2. Code review by maintainer(s)
3. Changes requested if needed
4. Approval and merge

## Branch Protection

The `main` branch is protected with the following rules:

- **No force pushes**: Force pushes to main are disabled to preserve history
- **No deletion**: The main branch cannot be deleted
- **Required status checks**: All CI tests must pass before merging
- **Pull request reviews**: At least one approving review is required
- **Stale review dismissal**: Reviews are dismissed when new commits are pushed

These protections ensure code quality and prevent accidental or malicious changes to the production branch. All changes to `main` must go through pull requests.

Branch protection settings are documented in `.github/settings.yml`.

## Areas for Contribution

### High Priority
- AI matching algorithm improvements
- Safety and moderation features
- Mobile app development (React Native)
- Multi-language support

### Good First Issues
Look for issues tagged with `good first issue` for beginner-friendly tasks.

### Documentation
- Improve setup instructions
- Add API examples
- Create user guides
- Translate documentation

### Testing
- Add test coverage
- Create integration tests
- Performance testing

## Questions?

- **[Start a Discussion](https://github.com/schoedel-learn/catholic-ride-share-app/discussions)** — the best place to ask questions, share ideas, or introduce yourself
- Open an issue with the `question` label for bugs or feature ideas
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for helping build a tool that serves the Catholic community!
