# Contributing to LectureLens

Thank you for your interest in contributing to LectureLens! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/suvakovan/SNAP-DRAGON-.git
   cd SNAP-DRAGON-
   ```

2. **Create a virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate
   pip install -r requirements.txt
   ```

3. **Download model assets:**
   ```powershell
   python scripts/download_models.py
   ```

## Code Standards

- **Python**: PEP 8 compliant, type hints on all public functions
- **Docstrings**: Google-style docstrings on all modules, classes, and functions
- **Tests**: All new features must include unit tests in `tests/`
- **Commits**: Use conventional commits (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`)

## Running Tests

```powershell
pytest tests/ -v --tb=short
```

## Pull Request Process

1. Fork the repository and create a feature branch
2. Make changes with clear, atomic commits
3. Ensure all tests pass locally
4. Submit a PR with a clear description of changes

## Architecture Guidelines

- All backends must implement the abstract base classes in `lecturelens/backends/base.py`
- No simulated backends may be returned from production factory functions
- All LLM outputs must be schema-validated via Pydantic models
- Audio processing must maintain 16kHz mono float32 format throughout the pipeline

## Reporting Issues

Open a GitHub Issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Hardware/OS details (especially Snapdragon model if applicable)
