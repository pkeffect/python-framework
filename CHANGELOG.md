# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2026-01-17

### Added
- `--gui2` flag for direct web UI access (bypasses Tkinter)
- `CONTENT_TYPE_HTML` constant for DRY compliance

### Fixed
- Fixed `NameError: http not defined` in WebGUI

## [1.3.0] - 2026-01-17

### Added
- Web-based fallback GUI when Tkinter is unavailable
- Automatic browser launch for web UI
- Matching dark gray/orange theme for web UI

## [1.2.0] - 2026-01-17

### Changed
- Rebranded to "Internode Bare Metal Framework"
- Config file path changed to `~/.internode.toml`
- Plugin directory changed to `~/.internode/plugins/`

### Added
- Scrollable GUI with section headers
- `FONT_FAMILY` constant
- Professional docstrings throughout
- Dry Run option in GUI

## [1.1.0] - 2026-01-17

### Added
- Tkinter GUI with dark gray/orange theme (`--gui`)
- All settings configurable in GUI

## [1.0.0] - 2026-01-17

### Added
- Plugin architecture (`~/.internode/plugins/`)
- Config file support (`~/.internode.toml`)
- `--update` mode to add missing files

## [0.3.0] - 2026-01-17

### Added
- GitHub Actions CI workflow generation
- Pre-commit configuration
- Dockerfile generation
- `manage.py` clean, lint, build commands

## [0.2.0] - 2026-01-17

### Added
- Interactive mode (`--interactive`)
- `--author` and `--email` CLI arguments
- Template selection (`--template`)
- `--dry-run` mode
- Python 3.11+ requirement

## [0.1.0] - 2026-01-17

### Added
- Initial release
- Project generation with configs, tests, docs
- Virtual environment creation
- `manage.py` utility script
- Multiple config format support (JSON, YAML, TOML, INI)
