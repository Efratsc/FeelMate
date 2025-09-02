# Changelog

All notable changes to FeelMate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Open source documentation and contribution guidelines
- GitHub issue templates for bug reports and feature requests
- Pull request template for structured contributions
- Code of Conduct for community guidelines
- Comprehensive README with project overview

### Changed
- Improved UI design with full-screen ChatGPT-like interface
- Removed visual boxes around AI responses for cleaner appearance
- Enhanced emotion detection and response generation
- Updated project structure and documentation

## [1.0.0] - 2024-12-19

### Added
- Initial release of FeelMate emotional support chatbot
- LLM-free LangGraph pipeline for intelligent conversations
- Real-time emotion detection using HuggingFace models
- Crisis detection and intervention system
- In-memory conversation history for contextual responses
- Modern Next.js frontend with TypeScript
- FastAPI backend with async processing
- Full-screen chat interface with streaming responses
- Emotion labels and severity indicators
- Resource recommendations for mental health support
- Professional UI with responsive design

### Features
- **Emotion Detection**: Detects 7+ emotions (joy, sadness, anger, fear, surprise, disgust, neutral)
- **Contextual Responses**: Smart, personalized responses based on conversation history
- **Crisis Intervention**: Automatic detection of crisis situations with resource recommendations
- **Streaming UI**: Real-time response display with typewriter effect
- **Modern Design**: Clean, accessible interface inspired by ChatGPT
- **No External Dependencies**: Self-contained system without external LLM APIs

### Technical Stack
- **Frontend**: Next.js 14, React, TypeScript
- **Backend**: FastAPI, Python 3.8+
- **AI Pipeline**: LangGraph, HuggingFace Transformers
- **Styling**: Inline styles with modern design principles

### Security & Privacy
- No permanent data storage
- Local processing only
- Input validation and sanitization
- No external API dependencies

---

## Version History

### Version 1.0.0
- **Release Date**: september 1, 2025
- **Status**: Stable Release
- **Features**: Core emotional support chatbot functionality
- **Architecture**: LLM-free LangGraph pipeline with emotion detection

---

## Contributing to Changelog

When adding entries to this changelog, please follow these guidelines:

1. **Use the existing format** and structure
2. **Add entries under the appropriate section**:
   - `Added` for new features
   - `Changed` for changes in existing functionality
   - `Deprecated` for soon-to-be removed features
   - `Removed` for now removed features
   - `Fixed` for any bug fixes
   - `Security` for security-related changes

3. **Use clear, concise language** that users can understand
4. **Include issue/PR numbers** when relevant
5. **Add your entry to the [Unreleased] section** for upcoming changes

### Example Entry
```markdown
### Added
- New emotion detection feature (#123)
- Support for additional languages (#456)
```

---

## Release Process

1. **Development**: Features and fixes are added to the [Unreleased] section
2. **Release Preparation**: Create a new version section
3. **Release**: Move [Unreleased] content to the new version
4. **Tag**: Create a git tag for the release
5. **Documentation**: Update version numbers in README and other docs
