# Catholic Ride Share Documentation

Welcome to the comprehensive documentation for Catholic Ride Share, a community-driven ride-sharing application for the Catholic community.

Catholic Ride Share is open source and intended to be installed, operated, and customized by parishes, dioceses, and Catholic organizations running their own local instances.

## 📚 Documentation Index

### Getting Started
- [Main README](../README.md) - Project overview and quick start
- [CONTRIBUTING](../CONTRIBUTING.md) - How to contribute to the project
- [LICENSE](../LICENSE) - Project license information

### Architecture & Design
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design decisions
- Project roadmap in [braingrid-improvements](../braingrid-improvements)

### Security Documentation
- [SECURITY.md](../SECURITY.md) - Security policy and vulnerability reporting
- [REPOSITORY_SECURITY_SETTINGS.md](REPOSITORY_SECURITY_SETTINGS.md) - Complete security configuration guide
- [BRANCH_PROTECTION_SETUP.md](BRANCH_PROTECTION_SETUP.md) - Branch protection rules setup

### Configuration
- [Backend .env.example](../backend/.env.example) - Environment variables template
- [Docker Compose](../docker-compose.yml) - Container orchestration setup

## 🔐 Security & Governance

### For Repository Administrators

If you have admin access to this repository, please review and implement:

1. **Immediate Actions** (Critical):
   - [ ] Set up branch protection on `main` branch → [Setup Guide](BRANCH_PROTECTION_SETUP.md)
   - [ ] Enable secret scanning with push protection → [Security Settings](REPOSITORY_SECURITY_SETTINGS.md#security-features)
   - [ ] Enable private vulnerability reporting → [Security Settings](REPOSITORY_SECURITY_SETTINGS.md#security-features)
   - [ ] Review and configure all security features → [Complete Guide](REPOSITORY_SECURITY_SETTINGS.md)

2. **Short-term Actions** (Within 1 week):
   - [ ] Review collaborator access levels
   - [ ] Configure repository settings per recommendations
   - [ ] Set up notification preferences for security alerts
   - [ ] Verify CodeQL and Dependabot are running correctly

3. **Ongoing Maintenance**:
   - [ ] Review security alerts weekly
   - [ ] Audit access permissions monthly
   - [ ] Update security documentation quarterly
   - [ ] Conduct security reviews quarterly

### For Contributors

Before contributing:
1. Read the [Security Policy](../SECURITY.md)
2. Review the [Contributing Guidelines](../CONTRIBUTING.md)
3. Understand [branch protection requirements](BRANCH_PROTECTION_SETUP.md)
4. Never commit secrets or credentials

## 🏗️ Architecture Overview

Catholic Ride Share is built with:
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with PostGIS
- **Cache**: Redis
- **Task Queue**: Celery
- **Container**: Docker & Docker Compose

For detailed architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 🔧 Development Workflow

### Standard Development Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow code style guidelines
   - Write/update tests
   - Update documentation

3. **Test locally**
   ```bash
   cd backend
   pytest
   black .
   isort .
   flake8 .
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Add feature: description"
   git push origin feature/your-feature-name
   ```

5. **Open a pull request**
   - Use the PR template
   - Request review
   - Address feedback
   - Wait for CI checks to pass

6. **Merge**
   - At least 1 approval required
   - All status checks must pass
   - Squash and merge (recommended)

## 🧪 Testing

### Running Tests

```bash
cd backend
pytest --cov=app --cov-report=html
```

### Test Coverage

- Target: >80% coverage
- Coverage reports in `backend/htmlcov/`

### Testing Guidelines

- Write unit tests for all new features
- Include integration tests for API endpoints
- Test security features thoroughly
- Mock external services (Stripe, AWS, etc.)

## 🚀 Deployment

### Environment Setup

1. **Development**: Use Docker Compose
2. **Staging**: (To be configured)
3. **Production**: (To be configured)

### Pre-deployment Checklist

- [ ] All tests pass
- [ ] Security scans complete
- [ ] Environment variables configured
- [ ] Database migrations tested
- [ ] Backup strategy in place

## 📊 Monitoring & Maintenance

### Daily
- Automated via GitHub notifications
- Review Dependabot PRs

### Weekly
- Review open PRs
- Check CodeQL results
- Update dependencies

### Monthly
- Audit access permissions
- Review security alerts
- Check application performance

### Quarterly
- Full security audit
- Update documentation
- Review and update policies

## 🆘 Support & Resources

### Getting Help

1. **Issues**: Check existing issues or open a new one
2. **Discussions**: Use GitHub Discussions for questions
3. **Security**: Follow [SECURITY.md](../SECURITY.md) for vulnerability reports

### External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

### Community

- **Mission**: Strengthen Catholic communities by ensuring transportation is never a barrier
- **Values**: Charity, service, community, security, transparency
- **Code of Conduct**: Be respectful, charitable, and collaborative

## 📝 Documentation Standards

### When to Update Documentation

Update documentation when you:
- Add new features
- Change architecture
- Modify security practices
- Update configuration requirements
- Fix significant bugs

### Documentation Checklist

When adding documentation:
- [ ] Clear and concise
- [ ] Examples included
- [ ] Screenshots for UI changes
- [ ] Links to related docs
- [ ] Date of last update noted

## 🔄 Version Control

### Branching Strategy

- `main`: Production-ready code (protected)
- `develop`: Active development (protected)
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical production fixes
- `release/*`: Release preparation

### Commit Message Format

```
type(scope): subject

body (optional)

footer (optional)
```

**Types**: feat, fix, docs, style, refactor, test, chore, security

**Examples**:
```
feat(auth): add email verification
fix(rides): resolve distance calculation bug
docs(security): update vulnerability reporting process
security(api): add rate limiting to auth endpoints
```

## 📅 Release Process

(To be defined as project matures)

1. Create release branch
2. Update version numbers
3. Update CHANGELOG
4. Run full test suite
5. Security review
6. Merge to main
7. Tag release
8. Deploy to production

## 🎯 Project Goals

### Short-term (Q1 2025)
- Complete driver verification system
- Implement ride matching algorithm
- Launch mobile app MVP
- Achieve 80%+ test coverage

### Medium-term (Q2-Q3 2025)
- Real-time messaging
- Payment integration
- Multi-language support
- 1000+ active users

### Long-term (2026+)
- Nationwide coverage
- AI-powered matching
- Partner with parishes
- Sustainable funding model

## 🤝 Contributing Areas

### High Priority
- Driver verification workflow
- Mobile app development
- Security improvements
- Test coverage

### Good First Issues
Look for issues tagged `good first issue` for beginner-friendly tasks.

### Ongoing Needs
- Documentation improvements
- Translation (i18n)
- Bug fixes
- Performance optimization

## 📞 Contact

- **Repository**: https://github.com/schoedel-learn/catholic-ride-share
- **Issues**: https://github.com/schoedel-learn/catholic-ride-share/issues
- **Security**: See [SECURITY.md](../SECURITY.md)

---

## Quick Links

### For Developers
- [Setup Instructions](../README.md#getting-started)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Architecture Guide](ARCHITECTURE.md)
- [Contributing Guide](../CONTRIBUTING.md)

### For Administrators
- [Branch Protection Setup](BRANCH_PROTECTION_SETUP.md) ⚠️ **Action Required**
- [Security Settings](REPOSITORY_SECURITY_SETTINGS.md) ⚠️ **Action Required**
- [Security Policy](../SECURITY.md)

### For Contributors
- [Security Checklist](../CONTRIBUTING.md#security-checklist-for-all-prs)
- [Code Style Guide](../CONTRIBUTING.md#code-style-guidelines)
- [Testing Guidelines](#testing)

---

**Last Updated**: 2025-11-22  
**Maintained By**: Catholic Ride Share Community

*This documentation is a living document. Please keep it updated as the project evolves.*
