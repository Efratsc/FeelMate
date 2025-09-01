# Contributing to FeelMate 🤝

Thank you for your interest in contributing to FeelMate! This document provides guidelines and information for contributors.

## What is FeelMate? 💙

FeelMate is an AI-powered emotional support chatbot that provides personalized mental health assistance using advanced emotion detection and contextual response generation. It's built with a modern tech stack including Next.js, FastAPI, and LangGraph.

## How Can I Contribute? 🚀

We welcome contributions of all kinds! Here are some ways you can help:

### 🐛 Bug Reports
- Check existing issues first
- Provide detailed reproduction steps
- Include system information and error logs
- Use the bug report template

### 💡 Feature Requests
- Describe the feature clearly
- Explain the use case and benefits
- Consider implementation complexity
- Use the feature request template

### 🔧 Code Contributions
- Fix bugs
- Add new features
- Improve documentation
- Enhance UI/UX
- Optimize performance
- Add tests

### 📚 Documentation
- Improve README
- Add code comments
- Create tutorials
- Update API documentation

## Development Setup 🛠️

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- Git

### Frontend Setup (Next.js)
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python start_production.py
```

### Environment Configuration
1. Copy `backend/env.template` to `backend/.env`
2. Set `USE_LANGRAPH=true` for LLM-free mode
3. Configure any additional environment variables

## Code Style Guidelines 📝

### Frontend (TypeScript/React)
- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Maintain consistent formatting with Prettier
- Add proper JSDoc comments

### Backend (Python)
- Follow PEP 8 style guide
- Use type hints
- Add docstrings for functions
- Keep functions small and focused
- Use meaningful variable names

### General
- Write clear commit messages
- Keep PRs focused and small
- Add tests for new features
- Update documentation as needed

## Pull Request Process 🔄

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow the code style guidelines
   - Add tests if applicable
   - Update documentation
4. **Test your changes**
   - Run frontend tests: `npm test`
   - Run backend tests: `python -m pytest`
   - Test manually in both environments
5. **Commit your changes**
   ```bash
   git commit -m "feat: add new emotion detection feature"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**
   - Use the PR template
   - Describe changes clearly
   - Link related issues
   - Request reviews from maintainers

## Commit Message Convention 📋

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

## Issue Templates 📋

### Bug Report
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. Windows, macOS, Linux]
- Browser: [e.g. Chrome, Safari, Firefox]
- Version: [e.g. 22]

**Additional context**
Add any other context about the problem here.
```

### Feature Request
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions.

**Additional context**
Add any other context or screenshots about the feature request.
```

## Project Structure 📁

```
FeelMate/
├── frontend/                 # Next.js frontend application
│   ├── components/          # React components
│   ├── app/                # Next.js app directory
│   ├── styles/             # CSS and styling
│   └── package.json        # Frontend dependencies
├── backend/                # FastAPI backend application
│   ├── app/               # Main application code
│   │   ├── ml/           # Machine learning modules
│   │   └── api/          # API endpoints
│   ├── requirements.txt   # Python dependencies
│   └── server.py         # Main server file
├── docs/                  # Documentation
├── tests/                 # Test files
├── LICENSE               # MIT License
├── CONTRIBUTING.md       # This file
└── README.md            # Project overview
```

## Getting Help 💬

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Documentation**: Check the README and docs folder

## Code of Conduct 🤝

We are committed to providing a welcoming and inspiring community for all. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) to understand our community standards.

## Recognition 🏆

Contributors will be recognized in:
- GitHub contributors list
- Project README
- Release notes
- Community shoutouts

## License 📄

By contributing to FeelMate, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to FeelMate! Your help makes this project better for everyone. 💙
