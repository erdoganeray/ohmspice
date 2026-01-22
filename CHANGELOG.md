# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-01-23

### Added
- **Component System**: Resistor, Capacitor, Inductor, VoltageSource, CurrentSource
- **Circuit Builder**: Fluent API for building SPICE circuits
- **Value Parser**: Support for engineering notation (1k, 100n, 4.7meg)
- **Netlist Generator**: Generate and save SPICE netlist files
- **LTspice Backend**: Auto-detect and run LTspice simulations
- **Result Parser**: Parse LTspice `.raw` files for AC, DC, and transient analysis
- **Analysis Methods**: get_frequency(), get_time(), get_voltage(), get_current(), get_phase()
- **Comprehensive tests**: 67 tests covering components, circuit, netlist, and simulator

### Project Setup (Phase 0)
- Initial project structure with `src/ohmspice/` layout
- `pyproject.toml` with hatchling build system
- GitHub Actions CI/CD workflows (test, release, docs)
- Issue and PR templates
- Pre-commit hooks (ruff, mypy)
- MIT License

---

## Version History

| Version | Date | Milestone |
|---------|------|-----------|
| 0.1.0 | 2026-01-23 | Core Foundation |
| 0.2.0 | TBD | Templates & CLI |
| 0.3.0 | TBD | Import & Visualization |
| 0.4.0 | TBD | MCP Server |
| 0.5.0 | TBD | VS Code Extension |
| 1.0.0 | TBD | Production Ready |
