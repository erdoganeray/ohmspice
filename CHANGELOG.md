# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-01-24

### Added

**Template System**:
- `CircuitTemplate` abstract base class for circuit templates
- **12 ready-to-use circuit templates**:
  - **Filters** (4): `rc_lowpass()`, `rc_highpass()`, `rlc_bandpass()`, `rlc_notch()`
  - **Amplifiers** (2): `inverting()`, `noninverting()` (simplified models)
  - **Oscillators** (3): `wien_bridge()`, `phase_shift()`, `colpitts()`
  - **Power** (3): `voltage_divider()`, `half_wave_rectifier()`, `full_wave_rectifier()`
- Template metadata system (`TemplateInfo`, `TemplateParameter`)
- Automatic component value calculation from specifications
- Template registry and discovery (`list_all_templates()`, `get_template()`)

**CLI with Click**:
- `ohmspice templates` - List available templates with filtering and verbose mode
- `ohmspice new <template>` - Create circuits from templates with parameter support
- `ohmspice simulate <file>` - Run SPICE simulations on netlist files
- `ohmspice schematic <file>` - Schematic generation (v0.3.0 placeholder)
- `ohmspice interactive` - REPL-style interactive circuit builder
- Template aliases (e.g., `lowpass` → `rc_lowpass`)
- Engineering notation support (1k, 100n, 4.7meg, etc.)
- Comprehensive CLI help and error messages

**Interactive Mode**:
- REPL interface for step-by-step circuit building
- Commands: `new`, `add`, `analysis`, `show`, `save`, `clear`, `help`, `exit`
- Support for resistors, capacitors, inductors, voltage sources
- AC, DC, transient, and operating point analysis

**Documentation**:
- Template usage guide (`docs/templates.md`)
- CLI reference guide (`docs/cli.md`)
- Template usage examples (`examples/template_usage.py`)
- CLI demo script (`examples/cli_demo.sh`)

### Tests
- 24 template tests covering all template types and calculations
- 15 CLI tests including interactive mode
- **39 total tests, all passing**
- Test coverage: 61% overall, 90%+ for template modules

### Fixed
- Exception handling for missing CLI parameters (KeyError → user-friendly message)
- `run_file()` → `run_netlist()` method name correction in LTSpice simulator

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
| 0.2.0 | 2026-01-24 | Templates & CLI |
| 0.3.0 | TBD | Import & Visualization |
| 0.4.0 | TBD | MCP Server |
| 0.5.0 | TBD | VS Code Extension |
| 1.0.0 | TBD | Production Ready |
