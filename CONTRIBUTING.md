# Contributing to Screenshot MCP Server

Thank you for your interest in contributing!

## How to Contribute

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** (`git checkout -b feature/my-feature`)
4. **Make your changes** and commit with clear messages
5. **Push to your fork** and submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/adityachauhan0/screenshot-mcp.git
cd screenshot-mcp

# Install in development mode
pip install -e .

# Install dev dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v
```

## Code Style

- Follow PEP 8
- Use type hints where possible
- Write docstrings for public functions/classes
- Add tests for new functionality

## Reporting Issues

Please report issues on GitHub with:
- Your Linux distribution and version
- Display server (X11 or Wayland)
- Steps to reproduce
- Expected vs actual behavior

## Pull Request Guidelines

- Reference related issues in your PR description
- Ensure all tests pass
- Update documentation as needed
- Keep changes focused and atomic
