# Contributing to Internode Bare Metal Framework

Thank you for your interest in contributing! This project follows a "bare metal" philosophy—no external dependencies.

## 🎯 Core Principles

1. **Single File** - All code must stay in `python_framework.py`
2. **Zero Dependencies** - Only Python standard library
3. **Python 3.11+** - Modern Python features encouraged

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/pkeffect/internode-framework.git
cd internode-framework

# Test the script
python python_framework.py --version
python python_framework.py --dry-run --name TestProject
```

## 📝 Making Changes

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-feature`
3. **Make** your changes
4. **Test** thoroughly:
   ```bash
   python python_framework.py --dry-run --name Test
   python python_framework.py --name TestProject --no-venv
   python python_framework.py --gui
   ```
5. **Commit**: `git commit -m "feat: add my feature"`
6. **Push**: `git push origin feature/my-feature`
7. **Open** a Pull Request

## 📋 Code Style

- Use type hints
- Include docstrings for all public functions
- Follow PEP 8
- Keep functions focused and readable

## 🧪 Testing

Since we have no dependencies, testing is manual:

```bash
# Test all modes
python python_framework.py --version
python python_framework.py --help
python python_framework.py --name Test --dry-run
python python_framework.py --name Test --template minimal --no-venv
python python_framework.py --gui
python python_framework.py --gui2
```

## 📜 Commit Messages

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `style:` Formatting changes

## ❓ Questions?

Open an issue or reach out to @pkeffect.
