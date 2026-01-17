# Support

## 📚 Documentation

- [README](README.md) - Quick start guide
- [CONTRIBUTING](CONTRIBUTING.md) - How to contribute
- [CHANGELOG](CHANGELOG.md) - Version history

## ❓ Getting Help

### Before asking for help:
1. Check the README for usage examples
2. Run `python python_framework.py --help`
3. Try `--dry-run` to preview changes
4. Search existing [Issues](https://github.com/pkeffect/internode-framework/issues)

### If you need help:
1. **Bug Report** - Open an issue with:
   - Python version (`python --version`)
   - OS (Windows/macOS/Linux)
   - Full error message
   - Steps to reproduce

2. **Feature Request** - Open an issue describing:
   - What you want to accomplish
   - Why current features don't meet your needs

## 🔧 Common Issues

### Tkinter not available
```bash
# Use web UI instead
python python_framework.py --gui2
```

### Permission denied on manage.py
```bash
chmod +x manage.py  # Unix/macOS
```

### Project already exists
```bash
# Use update mode to add missing files
python python_framework.py --name ExistingProject --update
```

## 📧 Contact

- GitHub: [@pkeffect](https://github.com/pkeffect)
