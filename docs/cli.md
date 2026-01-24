# Command-Line Interface

OhmSPICE provides a powerful CLI for creating, simulating, and analyzing SPICE circuits.

## Installation

```bash
pip install ohmspice
```

## Quick Start

```bash
# List available templates
ohmspice templates

# Create a circuit from template
ohmspice new lowpass --fc 1000 --r 1k -o filter.cir

# Simulate
ohmspice simulate filter.cir --analysis ac

# Interactive mode
ohmspice interactive
```

---

## Commands

### `ohmspice templates`

List available circuit templates.

**Options**:
- `-c, --category` - Filter by category: `filters`, `amplifiers`, `oscillators`, `power`, `all` (default: `all`)
- `-v, --verbose` - Show detailed information including parameters

**Examples**:
```bash
# List all templates
ohmspice templates

# List only filter templates
ohmspice templates -c filters

# Show detailed info
ohmspice templates -v
```

**Output**:
```
╔════════════════════════════════════════╗
║     OhmSPICE Circuit Templates         ║
╚════════════════════════════════════════╝

📁 Filters
────────────────────────────────────────
  rc_lowpass
  rc_highpass
  rlc_bandpass
  rlc_notch

📁 Amplifiers
────────────────────────────────────────
  inverting
  noninverting
...
```

---

### `ohmspice new`

Create a new circuit from a template.

**Usage**: `ohmspice new TEMPLATE [OPTIONS]`

**Template Aliases**:
- `lowpass` → `rc_lowpass`
- `highpass` → `rc_highpass`
- `bandpass` → `rlc_bandpass`
- `notch` → `rlc_notch`

**Options**:
- `--fc FLOAT` - Cutoff/center frequency (Hz)
- `--r TEXT` - Resistance value (e.g., 1k, 10k)
- `--c TEXT` - Capacitance value (e.g., 100n, 1u)
- `--l TEXT` - Inductance value (e.g., 10m, 100u)
- `--q FLOAT` - Quality factor
- `--gain FLOAT` - Amplifier gain
- `--vout FLOAT` - Output voltage
- `--vin FLOAT` - Input voltage
- `--frequency FLOAT` - Oscillation frequency (Hz)
- `-o, --output PATH` - Output file (.cir)
- `--simulate` - Run simulation after creating
- `--no-source` - Don't include voltage source

**Examples**:

```bash
# Create RC low-pass filter (print to console)
ohmspice new lowpass --fc 1000 --r 1k

# Save to file
ohmspice new lowpass --fc 1000 --r 1k -o filter.cir

# Create and simulate immediately
ohmspice new lowpass --fc 1000 --r 1k -o filter.cir --simulate

# Create voltage divider
ohmspice new voltage_divider --vout 3.3 --vin 5 -o divider.cir

# Create bandpass filter with Q=10
ohmspice new bandpass --fc 1000 --q 10 -o bandpass.cir

# Create inverting amplifier
ohmspice new inverting --gain 10 -o amp.cir
```

**Output** (without `-o`):
```
─── Generated Netlist ───
* RC Low-Pass Filter (fc=1000Hz)
V1 in 0 AC 1
R1 in out 1k
C1 out 0 159.15n
.ac dec 20 10 100k
.end
```

**Error Handling**:
```bash
# Missing required parameter
ohmspice new lowpass
# Error: Missing required parameter: 'fc'
# Required parameters: fc

# Invalid template
ohmspice new nonexistent --fc 1000
# Error: Template 'nonexistent' not found.
# Use 'ohmspice templates' to see available templates.
```

---

### `ohmspice simulate`

Simulate a SPICE netlist file.

**Usage**: `ohmspice simulate FILE [OPTIONS]`

**Options**:
- `-a, --analysis` - Analysis type: `ac`, `dc`, `tran`, `op`
- `--plot` - Show plot after simulation
- `-o, --output PATH` - Save results to file

**Examples**:

```bash
# Run simulation
ohmspice simulate filter.cir

# With specific analysis type
ohmspice simulate filter.cir -a ac

# Show plot
ohmspice simulate filter.cir --plot

# Save results
ohmspice simulate filter.cir -o results.csv
```

**Output**:
```
🔧 Simulating: filter.cir
✓ Simulation completed!

Variables: 3
  • frequency
  • V(in)
  • V(out)
```

**Requirements**:
- LTspice must be installed and in PATH
- See [Installation Guide](getting-started/installation.md) for setup

---

### `ohmspice schematic`

Generate schematic diagram from netlist.

> **Note**: Available in v0.3.0. Currently shows placeholder message.

**Usage**: `ohmspice schematic FILE [OPTIONS]`

**Options**:
- `-o, --output PATH` - Output file (png, svg, pdf)
- `--style` - Schematic style: `default`, `ieee`, `european`
- `--show-values / --no-values` - Show component values (default: show)
- `--show-nodes / --no-nodes` - Show node names (default: hide)

**Example**:
```bash
ohmspice schematic filter.cir -o schematic.png
```

---

### `ohmspice interactive`

Start interactive circuit builder mode.

**Usage**: `ohmspice interactive`

Provides a REPL-style interface for building circuits step by step.

**Available Commands**:
- `new [name]` - Create new circuit
- `add resistor <name> <node1> <node2> <value>` - Add resistor
- `add capacitor <name> <node1> <node2> <value>` - Add capacitor
- `add inductor <name> <node1> <node2> <value>` - Add inductor
- `add vsource <name> <n+> <n-> [dc=V] [ac=V]` - Add voltage source
- `analysis ac <start> <stop> [points]` - Add AC analysis
- `analysis dc <source> <start> <stop> <step>` - Add DC analysis
- `analysis tran <stop_time>` - Add transient analysis
- `analysis op` - Add operating point analysis
- `show` - Display current netlist
- `save <filename>` - Save netlist to file
- `clear` - Clear circuit
- `help` - Show help
- `exit` - Exit interactive mode

**Example Session**:

```
╔════════════════════════════════════════╗
║   OhmSPICE Interactive Mode            ║
╚════════════════════════════════════════╝
Type 'help' for commands, 'exit' to quit.

ohmspice> new RC Filter
✓ Created circuit: RC Filter

ohmspice> add vsource V1 in 0 ac=1
✓ Added vsource V1

ohmspice> add resistor R1 in out 1k
✓ Added resistor R1

ohmspice> add capacitor C1 out 0 159n
✓ Added capacitor C1

ohmspice> analysis ac 1 1000000 20
✓ Added AC analysis

ohmspice> show

─── Netlist ───
* RC Filter
V1 in 0 AC 1
R1 in out 1k
C1 out 0 159n
.ac dec 20 1 1meg
.end

ohmspice> save filter.cir
✓ Saved to: filter.cir

ohmspice> exit
Goodbye!
```

---

## Global Options

All commands support:
- `--help` - Show help for the command
- `--version` - Show OhmSPICE version

**Examples**:
```bash
# Show version
ohmspice --version

# Show help for a command
ohmspice new --help
ohmspice simulate --help
```

---

## Value Notation

OhmSPICE supports engineering notation for component values:

| Suffix | Multiplier | Example |
|--------|------------|---------|
| `T` | 10¹² | `1T` = 1,000,000,000,000 |
| `G` | 10⁹ | `1G` = 1,000,000,000 |
| `Meg` | 10⁶ | `4.7Meg` = 4,700,000 |
| `k` | 10³ | `1k` = 1,000 |
| `m` | 10⁻³ | `10m` = 0.01 |
| `u` | 10⁻⁶ | `100u` = 0.0001 |
| `n` | 10⁻⁹ | `159n` = 0.000000159 |
| `p` | 10⁻¹² | `10p` = 0.00000000001 |

**Examples**:
```bash
--r 1k          # 1,000 Ω
--r 4.7meg      # 4,700,000 Ω
--c 100n        # 100 nF = 0.0000001 F
--c 1u          # 1 µF = 0.000001 F
--l 10m         # 10 mH = 0.01 H
```

---

## Integration with Python API

CLI commands can be replicated in Python:

```python
# CLI: ohmspice new lowpass --fc 1000 --r 1k
from ohmspice.templates import filters
circuit = filters.rc_lowpass(fc=1000, r=1000)

# CLI: ohmspice simulate filter.cir
from ohmspice.simulators import LTSpice
sim = LTSpice()
results = sim.run_netlist("filter.cir")
```

See [API Reference](api-reference.md) for more details.

---

## Tips & Tricks

### Batch Processing

```bash
# Create multiple filters
for fc in 100 1000 10000; do
    ohmspice new lowpass --fc $fc -o "filter_${fc}hz.cir"
done
```

### Pipeline with Other Tools

```bash
# Create circuit, simulate, and process results
ohmspice new lowpass --fc 1000 -o filter.cir
ohmspice simulate filter.cir -o results.csv
python analyze_results.py results.csv
```

### Quick Testing

```bash
# Create and test immediately
ohmspice new lowpass --fc 1000 --r 1k --simulate
```

---

## Troubleshooting

### "LTspice not found"

Ensure LTspice is installed and in your PATH:
- Windows: Install from [Analog Devices](https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html)
- macOS: Install LTspice.app
- Linux: Use Wine

### "Template not found"

Use `ohmspice templates` to see available template names. Remember to use the exact name or alias.

### Missing Parameters

Check template requirements:
```bash
ohmspice templates -v -c filters
```

---

## See Also

- [Templates Documentation](templates.md) - Available circuit templates
- [Getting Started](getting-started/quickstart.md) - Quickstart guide
- [Examples](../examples/) - CLI usage examples
