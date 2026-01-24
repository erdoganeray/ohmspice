# Circuit Templates

OhmSPICE provides ready-to-use circuit templates for common electronic designs. Templates automatically calculate component values based on specifications like cutoff frequency, gain, or quality factor.

## Using Templates

```python
from ohmspice.templates import filters, amplifiers, oscillators, power

# Create a 1kHz RC low-pass filter
circuit = filters.rc_lowpass(fc=1000, r=1000)

# Create an inverting amplifier with gain of -10
circuit = amplifiers.inverting(gain=10)

# Create a voltage divider: 5V → 3.3V
circuit = power.voltage_divider(vout=3.3, vin=5)
```

---

## Filter Templates

### RC Low-Pass Filter

**Function**: `filters.rc_lowpass(fc, r=None, c=None, include_source=True)`

Simple first-order low-pass filter with -20dB/decade rolloff.

**Formula**: `fc = 1 / (2π × R × C)`

**Parameters**:
- `fc` (float): Cutoff frequency in Hz (-3dB point)
- `r` (float, optional): Resistance in Ohms (default: 1kΩ)
- `c` (float, optional): Capacitance in Farads (auto-calculated if omitted)
- `include_source` (bool): Include AC voltage source (default: True)

**Example**:
```python
# Specify R, C is calculated
circuit = filters.rc_lowpass(fc=1000, r=1000)  
# C ≈ 159nF

# Specify C, R is calculated
circuit = filters.rc_lowpass(fc=1000, c=159e-9)
# R ≈ 1kΩ
```

---

### RC High-Pass Filter

**Function**: `filters.rc_highpass(fc, r=None, c=None, include_source=True)`

First-order high-pass filter (capacitor in series, resistor to ground).

**Formula**: `fc = 1 / (2π × R × C)`

**Example**:
```python
# 10kHz high-pass filter
circuit = filters.rc_highpass(fc=10000, r=10000)
```

---

### RLC Bandpass Filter

**Function**: `filters.rlc_bandpass(fc, q=10, r=100, include_source=True)`

Second-order bandpass filter with series RLC configuration.

**Formulas**:
- Center frequency: `fc = 1 / (2π × √(L×C))`
- Quality factor: `Q = (1/R) × √(L/C)`
- Bandwidth: `BW = fc / Q`

**Parameters**:
- `fc` (float): Center frequency in Hz
- `q` (float): Quality factor (default: 10)
- `r` (float): Resistance in Ohms (default: 100Ω)

**Example**:
```python
# 1kHz bandpass, Q=10 (BW=100Hz)
circuit = filters.rlc_bandpass(fc=1000, q=10)
```

---

### RLC Notch Filter

**Function**: `filters.rlc_notch(fc, q=10, r=100, include_source=True)`

Band-stop filter that attenuates frequencies around fc. Uses parallel LC tank.

**Example**:
```python
# 60Hz hum filter
circuit = filters.rlc_notch(fc=60, q=20)
```

---

## Amplifier Templates

> **Note**: Current implementations use simplified models. Full OpAmp-based templates will be added in v1.0.0.

### Inverting Amplifier

**Function**: `amplifiers.inverting(gain, r_in=10000, include_source=True)`

Op-amp inverting amplifier configuration.

**Formula**: `Gain = -Rf / Rin`

**Parameters**:
- `gain` (float): Voltage gain (positive number, will be inverted)
- `r_in` (float): Input resistance in Ohms (default: 10kΩ)

**Example**:
```python
# Gain of -10 (180° phase inversion)
circuit = amplifiers.inverting(gain=10, r_in=10000)
# Rf = 100kΩ
```

---

### Non-Inverting Amplifier

**Function**: `amplifiers.noninverting(gain, r1=10000, include_source=True)`

Op-amp non-inverting amplifier configuration.

**Formula**: `Gain = 1 + Rf / R1`

**Parameters**:
- `gain` (float): Voltage gain (must be ≥ 1)
- `r1` (float): R1 resistance in Ohms (default: 10kΩ)

**Example**:
```python
# Gain of 2 (buffer with gain)
circuit = amplifiers.noninverting(gain=2)
# Rf = 10kΩ, R1 = 10kΩ
```

---

## Oscillator Templates

> **Note**: These templates provide the passive networks. Full oscillator operation requires active components.

### Wien Bridge Oscillator

**Function**: `oscillators.wien_bridge(frequency, r=10000, include_source=True)`

RC network for Wien bridge oscillator.

**Formula**: `f = 1 / (2π × R × C)`

**Requires**: R1 = R2 = R and C1 = C2 = C for oscillation

**Example**:
```python
# 1kHz Wien bridge
circuit = oscillators.wien_bridge(frequency=1000)
```

---

### Phase Shift Oscillator

**Function**: `oscillators.phase_shift(frequency, r=10000, include_source=True)`

3-stage RC phase shift network (180° total phase shift).

**Formula**: `f = 1 / (2π × R × C × √6)`

**Example**:
```python
# 1kHz phase shift oscillator
circuit = oscillators.phase_shift(frequency=1000)
```

---

### Colpitts Oscillator

**Function**: `oscillators.colpitts(frequency, l=None, c_ratio=1, include_source=True)`

LC tank circuit with capacitive voltage divider.

**Formula**: `f = 1 / (2π × √(L × Ceq))` where `Ceq = C1×C2/(C1+C2)`

**Parameters**:
- `frequency` (float): Oscillation frequency in Hz
- `l` (float, optional): Inductance in Henries (auto-calculated based on frequency if omitted)
- `c_ratio` (float): C1/C2 ratio (default: 1 for equal capacitors)

**Example**:
```python
# 1 MHz RF oscillator
circuit = oscillators.colpitts(frequency=1e6)
```

---

## Power Circuit Templates

### Voltage Divider

**Function**: `power.voltage_divider(vout, vin, r2=10000, include_source=True)`

Resistive voltage divider.

**Formula**: `Vout = Vin × R2 / (R1 + R2)`

**Parameters**:
- `vout` (float): Desired output voltage
- `vin` (float): Input voltage
- `r2` (float): Bottom resistor in Ohms (default: 10kΩ)

**Example**:
```python
# 5V → 3.3V divider
circuit = power.voltage_divider(vout=3.3, vin=5)
# R1 ≈ 5.15kΩ, R2 = 10kΩ
```

---

### Half Wave Rectifier

**Function**: `power.half_wave_rectifier(frequency=60, load_r=1000, filter_c=None, include_source=True)`

Simple half-wave rectifier with optional filter capacitor.

**Parameters**:
- `frequency` (float): AC input frequency in Hz (default: 60Hz)
- `load_r` (float): Load resistance in Ohms (default: 1kΩ)
- `filter_c` (float, optional): Filter capacitor in Farads (auto-calculated for 10% ripple)

> **Note**: Diode component will be added in future version. Current implementation shows load and filter only.

---

### Full Wave Rectifier

**Function**: `power.full_wave_rectifier(frequency=60, load_r=1000, filter_c=None, include_source=True)`

Full-wave bridge rectifier with filter capacitor.

> **Note**: Diode bridge will be added when Diode component is implemented.

---

## Advanced Usage

### Listing Available Templates

```python
from ohmspice.templates import list_all_templates

templates = list_all_templates()
# {'filters': [...], 'amplifiers': [...], 'oscillators': [...], 'power': [...]}

for category, template_list in templates.items():
    print(f"\n{category}:")
    for info in template_list:
        print(f"  - {info.name}: {info.description}")
```

### Getting Template by Name

```python
from ohmspice.templates import get_template

template = get_template("rc_lowpass")
if template:
    circuit = template.create(fc=1000, r=1000)
```

### Customizing Templates

```python
# Create circuit without voltage source
circuit = filters.rc_lowpass(fc=1000, r=1000, include_source=False)

# Add your own source
circuit.add_voltage_source("Vin", "in", "0", dc=5, ac=1)

# Modify analysis
circuit.add_transient_analysis(stop_time=0.01)
```

---

## Future Templates

The following templates are planned for future releases:

**v1.0.0 (Requires OpAmp component)**:
- `filters.butterworth()` - Multi-order Butterworth filter
- `filters.sallen_key_lowpass()` - Active Sallen-Key topology
- `amplifiers.differential()` - Differential amplifier
- `amplifiers.instrumentation()` - 3-OpAmp instrumentation amplifier

See [Implementation Plan - Phase 6](https://github.com/erdoganeray/ohmspice/blob/main/implementation_plan.md#65-phase-2den-ertelenen-templates) for details.

---

## See Also

- [CLI Documentation](cli.md) - Using templates from command line
- [API Reference](api-reference.md) - Full API documentation
- [Examples](../examples/) - More template usage examples
