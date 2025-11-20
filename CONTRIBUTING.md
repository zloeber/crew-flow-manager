# Contributing to CrewAI Flow Manager

Thank you for your interest in contributing to CrewAI Flow Manager! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone. Be kind, considerate, and professional in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/crew-flow-manager.git
   cd crew-flow-manager
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/zloeber/crew-flow-manager.git
   ```

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+
- Docker (optional)

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up database
export DATABASE_URL="postgresql://user:pass@localhost:5432/crewai_flows"

# Run migrations (if any)
# alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install

# Set up environment
cp .env.example .env

# Start development server
npm run dev
```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix issues in existing code
- **New features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Performance**: Optimize existing code
- **UI/UX**: Improve user interface and experience

### Before You Start

1. **Check existing issues** to avoid duplicate work
2. **Create an issue** if one doesn't exist for your contribution
3. **Discuss major changes** in the issue before implementing
4. **Keep changes focused** - one feature/fix per PR

## Coding Standards

### Python (Backend)

Follow PEP 8 style guide:

```bash
# Format code
black app/

# Check style
flake8 app/

# Type checking
mypy app/
```

**Guidelines:**
- Use type hints for function parameters and return values
- Write docstrings for classes and functions
- Keep functions small and focused
- Use meaningful variable names
- Add comments for complex logic

**Example:**
```python
def create_flow(
    db: Session,
    flow_data: FlowCreate
) -> Flow:
    """
    Create a new flow in the database.
    
    Args:
        db: Database session
        flow_data: Flow creation data
        
    Returns:
        Created flow instance
        
    Raises:
        ValueError: If flow with same name exists
    """
    # Implementation here
    pass
```

### TypeScript/React (Frontend)

Follow standard TypeScript practices:

```bash
# Lint code
npm run lint

# Type check
npx tsc --noEmit
```

**Guidelines:**
- Use TypeScript for type safety
- Use functional components with hooks
- Keep components small and reusable
- Use meaningful component and variable names
- Extract complex logic into custom hooks
- Use proper prop types

**Example:**
```typescript
interface FlowCardProps {
  flow: Flow
  onEdit: (flow: Flow) => void
  onDelete: (id: number) => void
}

const FlowCard: React.FC<FlowCardProps> = ({ flow, onEdit, onDelete }) => {
  // Component implementation
}
```

### General Guidelines

- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It
- Write self-documenting code
- Add comments only when necessary
- Keep code modular and testable

## Testing Guidelines

### Backend Tests

```bash
cd backend
pytest tests/

# With coverage
pytest --cov=app tests/
```

**Test Structure:**
```python
def test_create_flow():
    """Test flow creation with valid data"""
    # Arrange
    flow_data = {...}
    
    # Act
    result = create_flow(db, flow_data)
    
    # Assert
    assert result.name == flow_data.name
```

### Frontend Tests

```bash
cd frontend
npm test
```

**Test Structure:**
```typescript
describe('FlowCard', () => {
  it('should render flow name', () => {
    // Test implementation
  })
  
  it('should call onEdit when edit button is clicked', () => {
    // Test implementation
  })
})
```

### Test Coverage Goals

- Aim for 80%+ code coverage
- Test all business logic
- Test error cases
- Test edge cases
- Integration tests for APIs

## Pull Request Process

### 1. Create a Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write code following the coding standards
- Add tests for new functionality
- Update documentation if needed
- Commit regularly with clear messages

### 3. Commit Your Changes

Follow conventional commit format:

```bash
git commit -m "feat: add flow export functionality"
git commit -m "fix: resolve websocket connection issue"
git commit -m "docs: update API documentation"
git commit -m "test: add tests for flow validation"
git commit -m "refactor: improve execution service"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting)
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### 4. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 5. Create Pull Request

1. Go to GitHub and create a pull request
2. Fill in the PR template with:
   - Description of changes
   - Related issue number
   - Testing performed
   - Screenshots (for UI changes)
3. Wait for review

### 6. Address Review Comments

- Respond to all comments
- Make requested changes
- Push updates to the same branch
- Request re-review when ready

### 7. Merge

Once approved, a maintainer will merge your PR.

## Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] PR description is complete
- [ ] Screenshots included (for UI changes)

## Issue Guidelines

### Creating Issues

**Bug Reports:**
```markdown
**Description**
Clear description of the bug

**To Reproduce**
1. Step one
2. Step two
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: Ubuntu 22.04
- Browser: Chrome 120
- Version: 1.0.0

**Screenshots**
If applicable
```

**Feature Requests:**
```markdown
**Problem**
What problem does this solve?

**Proposed Solution**
How should it work?

**Alternatives**
Other solutions considered

**Additional Context**
Any other information
```

## Project Structure

Understanding the project structure helps with contributions:

```
crew-flow-manager/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Configuration
│   │   ├── db/           # Database
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   └── tests/            # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── types/        # TypeScript types
│   └── tests/            # Frontend tests
├── examples/             # Example flows
└── docs/                 # Documentation
```

## Communication

- **Issues**: For bug reports and feature requests
- **Pull Requests**: For code contributions
- **Discussions**: For questions and ideas

## Recognition

Contributors will be:
- Listed in the README
- Mentioned in release notes
- Thanked in the community

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## Getting Help

If you need help:
1. Check existing documentation
2. Search closed issues
3. Ask in GitHub Discussions
4. Create a new issue with your question

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to CrewAI Flow Manager! 🚀
