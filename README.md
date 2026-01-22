# OhmSPICE

**Open-source SPICE toolkit with AI integration for electronic circuit design**

A hybrid toolkit that combines template-based circuit design with AI-powered capabilities, enabling both offline CLI usage and intelligent circuit synthesis through LLM integration.

---

## Features

### Hybrid Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                       OhmSPICE                              │
├─────────────────────────────────────────────────────────────┤
│  CORE ENGINE (LLM-agnostic)                                 │
│  ├── Component Library                                      │
│  ├── Netlist Builder                                        │
│  ├── Simulators (LTspice, ngspice, PSpice)                  │
│  └── Visualization (schemdraw, matplotlib)                  │
├─────────────────────────────────────────────────────────────┤
│  CLI (Template-based)           │  MCP (LLM-powered)        │
│  ├── ohmspice new lowpass       │  ├── Natural language     │
│  ├── ohmspice new bandpass      │  ├── Custom designs       │
│  ├── ohmspice new amplifier     │  ├── AI calculations      │
│  └── ohmspice simulate file.cir │  └── Intelligent debug    │
└─────────────────────────────────────────────────────────────┘
```

### Multiple Interfaces

| Interface | Mode | Use Case |
|-----------|------|----------|
| **CLI** | Template-based (Offline) | Quick simulations, automation, CI/CD |
| **MCP Server** | LLM-powered | AI assistants (VS Code Copilot, Antigravity) |
| **VS Code Extension** | Hybrid | Interactive development |
| **Python Library** | Core access | Scripts, custom applications |

### Core Capabilities
- **Multiple Simulators**: LTspice, ngspice, PSpice
- **Cross-Platform**: Windows, Linux, macOS
- **Circuit Visualization**: Generate schematic diagrams
- **Analysis Plots**: Transient, AC (Bode), DC sweep
- **Template Library**: Pre-built common circuits with formulas

---

## For Students: AI Assistant Integration

OhmSPICE makes it easy for electronics students to use any AI assistant (like ChatGPT, Claude, Gemini) to design circuits and then simulate them locally.

### How It Works

1. **Ask your AI Assistant** to design your circuit using our prompt template
2. **Copy the output** (OhmSPICE-formatted JSON or netlist)
3. **Run simulation** with a single command
4. **Get results** - plots, schematics, and analysis

### AI Prompt Template

Copy this prompt when asking your AI assistant to design a circuit:

```
I need you to design a circuit for me. Please output the result in OhmSPICE format.

OhmSPICE JSON Format:
{
  "name": "Circuit Name",
  "description": "What this circuit does",
  "components": [
    {"type": "resistor", "id": "R1", "node1": "in", "node2": "out", "value": "1k"},
    {"type": "capacitor", "id": "C1", "node1": "out", "node2": "gnd", "value": "159n"}
  ],
  "sources": [
    {"type": "voltage", "id": "V1", "node1": "in", "node2": "gnd", "dc": 0, "ac": 1}
  ],
  "analysis": {
    "type": "ac",
    "start": 1,
    "stop": 1000000,
    "points_per_decade": 10
  }
}

My circuit requirement:
[YOUR REQUIREMENT HERE - e.g., "Design a bandpass filter with center frequency 1kHz and Q=5"]
```

### Example Workflow

**Step 1: Ask your AI**
```
Design a low-pass RC filter with cutoff frequency 1kHz using OhmSPICE format.
```

**Step 2: The AI responds with:**
```json
{
  "name": "RC Low-Pass Filter",
  "description": "1kHz cutoff frequency low-pass filter",
  "components": [
    {"type": "resistor", "id": "R1", "node1": "in", "node2": "out", "value": "1k"},
    {"type": "capacitor", "id": "C1", "node1": "out", "node2": "gnd", "value": "159n"}
  ],
  "sources": [
    {"type": "voltage", "id": "V1", "node1": "in", "node2": "gnd", "dc": 0, "ac": 1}
  ],
  "analysis": {"type": "ac", "start": 1, "stop": 1000000, "points_per_decade": 10}
}
```

**Step 3: Save and simulate**
```bash
# Save the response to a file
# Then run:
ohmspice import circuit.json --simulate --plot
```

**Step 4: View results**
- Bode plot showing frequency response
- Schematic diagram
- Component values verified

### CLI Commands for Students

```bash
# Import from JSON
ohmspice import circuit.json

# Import and immediately simulate
ohmspice import circuit.json --simulate

# Import, simulate, and generate plots
ohmspice import circuit.json --simulate --plot --schematic

# Validate AI output without simulating
ohmspice validate circuit.json

# Convert JSON to standard SPICE netlist
ohmspice convert circuit.json --output circuit.cir
```

---

## Installation

```bash
# Install from PyPI
pip install ohmspice

# Or install from source
git clone https://github.com/erdoganeray/ohmspice.git
cd ohmspice
pip install -e .
```

### Prerequisites
At least one SPICE simulator:

| Simulator | Platform | Download |
|-----------|----------|----------|
| LTspice | Windows, macOS, Linux (Wine) | [analog.com](https://www.analog.com/ltspice) |
| ngspice | Windows, Linux, macOS | [ngspice.sourceforge.io](https://ngspice.sourceforge.io/) |
| PSpice | Windows | [orcad.com](https://www.orcad.com/pspice) |

---

## Quick Start

### CLI Usage (Template-Based, Offline)

```bash
# List available circuit templates
ohmspice templates

# Create circuits with automatic component calculation
ohmspice new lowpass --type rc --fc 1kHz --r 1k
ohmspice new highpass --type rc --fc 10kHz --c 100n
ohmspice new bandpass --fc 1kHz --q 10 --r 10k
ohmspice new amplifier --type inverting --gain 10
ohmspice new oscillator --type wien --freq 1kHz
ohmspice new voltage-divider --vin 12 --vout 5

# Simulate existing netlist
ohmspice simulate circuit.cir --analysis ac

# Generate schematic
ohmspice schematic circuit.cir --output schematic.png

# Interactive mode
ohmspice interactive
```

### Python Library

```python
from ohmspice import Circuit, Simulator, templates

# Use a template with auto-calculation
circuit = templates.lowpass_rc(fc=1000, r=1000)  # fc=1kHz, R=1kΩ → C calculated

# Or build manually
circuit = Circuit("Custom Filter")
circuit.add_voltage_source("V1", "in", "gnd", ac=1)
circuit.add_resistor("R1", "in", "out", "1k")
circuit.add_capacitor("C1", "out", "gnd", "159n")

# Simulate
sim = Simulator("ltspice")
results = sim.ac_analysis(circuit, start=1, stop=1e6)
results.bode_plot(output="bode.png")
```

### MCP Server (LLM-Powered)

```bash
# Start MCP server for AI assistants
ohmspice mcp-server
```

When connected to an AI assistant (VS Code Copilot, Antigravity, etc.):
```
User: "Design a bandpass filter centered at 1kHz with Q=5"
AI: Uses ohmspice tools → Calculates components → Creates netlist → Simulates → Returns results
```

**MCP Tools:**
| Tool | Description |
|------|-------------|
| `list_components` | Available SPICE components |
| `list_templates` | Pre-built circuit templates |
| `create_circuit` | Build circuit from components |
| `calculate_values` | Calculate component values for specs |
| `run_simulation` | Execute SPICE simulation |
| `generate_schematic` | Create circuit diagram |
| `generate_plot` | Bode, transient, DC plots |
| `import_json` | Import AI-formatted circuit |

---

## Built-in Circuit Templates

### Filters
| Template | Command | Parameters |
|----------|---------|------------|
| RC Low-Pass | `new lowpass --type rc` | `--fc`, `--r` or `--c` |
| RC High-Pass | `new highpass --type rc` | `--fc`, `--r` or `--c` |
| RLC Bandpass | `new bandpass` | `--fc`, `--q`, `--r` |
| RLC Notch | `new notch` | `--fc`, `--q` |
| Butterworth | `new butterworth` | `--fc`, `--order` |
| Sallen-Key | `new sallen-key` | `--fc`, `--q`, `--type` |

### Amplifiers
| Template | Command | Parameters |
|----------|---------|------------|
| Inverting | `new amplifier --type inverting` | `--gain`, `--r1` |
| Non-Inverting | `new amplifier --type noninverting` | `--gain`, `--r1` |
| Differential | `new amplifier --type diff` | `--gain` |
| Instrumentation | `new amplifier --type inst` | `--gain` |

### Oscillators
| Template | Command | Parameters |
|----------|---------|------------|
| Wien Bridge | `new oscillator --type wien` | `--freq` |
| Phase Shift | `new oscillator --type phase` | `--freq` |
| Colpitts | `new oscillator --type colpitts` | `--freq` |

### Power
| Template | Command | Parameters |
|----------|---------|------------|
| Voltage Divider | `new voltage-divider` | `--vin`, `--vout`, `--iload` |
| Half-Wave Rectifier | `new rectifier --type half` | `--vac` |
| Full-Wave Rectifier | `new rectifier --type full` | `--vac` |
| Voltage Regulator | `new regulator` | `--vin`, `--vout` |

---

## Project Structure

```
ohmspice/
├── ohmspice_core/           # Core library (LLM-agnostic)
│   ├── circuit.py           # Circuit builder
│   ├── netlist.py           # Netlist generator/parser
│   ├── components.py        # Component definitions
│   ├── importer.py          # JSON format importer
│   ├── templates/           # Circuit templates with formulas
│   │   ├── filters.py       # Filter circuits
│   │   ├── amplifiers.py    # Amplifier circuits
│   │   └── oscillators.py   # Oscillator circuits
│   ├── simulators/          # Simulator backends
│   │   ├── base.py
│   │   ├── ltspice.py
│   │   ├── ngspice.py
│   │   └── pspice.py
│   ├── analysis/            # Analysis types
│   └── visualization/       # Schematic & plots
│
├── interfaces/
│   ├── cli/                 # CLI (Template-based)
│   ├── mcp/                 # MCP Server (LLM-powered)
│   └── vscode/              # VS Code Extension
│
├── tests/
├── docs/
├── examples/
└── pyproject.toml
```

---

## Development Roadmap

### Phase 1: Core Foundation
- [ ] Project structure setup
- [ ] Circuit builder class
- [ ] Netlist generator
- [ ] Basic component library
- [ ] LTspice backend integration
- [ ] Result parser (.raw files)

### Phase 2: Templates & CLI
- [ ] Template system with formulas
- [ ] Filter templates (LP, HP, BP, Notch)
- [ ] Amplifier templates
- [ ] CLI with Click framework
- [ ] Interactive mode

### Phase 3: Import & Visualization
- [ ] JSON/AI format importer
- [ ] Validation system
- [ ] Schematic generation (schemdraw)
- [ ] Bode plots
- [ ] Transient plots

### Phase 4: MCP Server
- [ ] MCP protocol implementation
- [ ] Tool definitions for AI
- [ ] Natural language to circuit
- [ ] Integration testing with AI assistants

### Phase 5: VS Code Extension
- [ ] Extension scaffolding
- [ ] Syntax highlighting for .cir files
- [ ] Inline simulation
- [ ] Schematic preview panel

### Phase 6: Extended Support
- [ ] ngspice backend
- [ ] PSpice backend
- [ ] Advanced templates
- [ ] Cross-platform testing

---

## Supported Components

| Category | Components |
|----------|------------|
| **Passive** | Resistor, Capacitor, Inductor, Potentiometer |
| **Sources** | Voltage (DC/AC/Pulse/Sine/PWL), Current |
| **Semiconductors** | Diode, Zener, LED, BJT, MOSFET, JFET |
| **Amplifiers** | Op-Amp (ideal + real models) |
| **Other** | Transformer, Switch, Transmission Line |

---

## Supported Analyses

| Analysis | SPICE Command | Description |
|----------|---------------|-------------|
| **Operating Point** | `.op` | DC bias point |
| **DC Sweep** | `.dc` | Sweep DC source |
| **AC Analysis** | `.ac` | Frequency response |
| **Transient** | `.tran` | Time-domain |
| **Noise** | `.noise` | Noise analysis |
| **Parameter Sweep** | `.step` | Component sweep |

---

## Contributing

```bash
git clone https://github.com/erdoganeray/ohmspice.git
cd ohmspice
pip install -e ".[dev]"
pytest
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [LTspice](https://www.analog.com/ltspice) - Analog Devices
- [ngspice](https://ngspice.sourceforge.io/) - Open source SPICE
- [SchemDraw](https://schemdraw.readthedocs.io/) - Circuit drawing
- [PyLTSpice](https://pypi.org/project/PyLTSpice/) - Python LTspice interface

---

<p align="center">
  <strong>OhmSPICE</strong> - Where circuits meet intelligence
</p>
