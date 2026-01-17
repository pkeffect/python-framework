# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.3.x   | :white_check_mark: |
| 1.2.x   | :white_check_mark: |
| < 1.2   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **Do NOT** open a public issue
2. Email the maintainer at @pkeffect
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact

We will respond within 48 hours and work on a fix.

## Security Considerations

This project:
- ✅ Uses only Python standard library (no supply chain risk)
- ✅ Does not make network calls during generation
- ✅ Validates project names against dangerous patterns
- ✅ Uses `pathlib` for safe path operations
- ✅ Plugin system restricted to user directory

## Best Practices

When using this framework:
- Review plugins before installing
- Don't run with elevated privileges unless necessary
- Keep Python updated
