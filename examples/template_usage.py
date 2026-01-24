"""Template usage examples.

This script demonstrates how to use OhmSPICE circuit templates
to quickly create common electronic circuits.
"""

from ohmspice.templates import filters, amplifiers, oscillators, power

print("=" * 60)
print("OhmSPICE Template Usage Examples")
print("=" * 60)

# ============================================================================
# EXAMPLE 1: RC Low-Pass Filter
# ============================================================================
print("\n1. RC Low-Pass Filter (fc=1kHz)")
print("-" * 60)

# Create filter with specified R, C is auto-calculated
circuit = filters.rc_lowpass(fc=1000, r=1000)
print(circuit.to_netlist())

# Calculate what C value was used
template = filters._rc_lowpass_template
values = template.calculate_values(fc=1000, r=1000)
print(f"\nCalculated: R={values['r']}Ω, C={values['c']*1e9:.2f}nF")

# ============================================================================
# EXAMPLE 2: RLC Bandpass Filter
# ============================================================================
print("\n\n2. RLC Bandpass Filter (fc=1kHz, Q=10)")
print("-" * 60)

circuit = filters.rlc_bandpass(fc=1000, q=10, r=100)
print(circuit.to_netlist())

values = filters._rlc_bandpass_template.calculate_values(fc=1000, q=10, r=100)
print(f"\nCalculated: R={values['r']}Ω, L={values['l']*1e3:.2f}mH, C={values['c']*1e9:.2f}nF")
print(f"Bandwidth: {1000/10}Hz")

# ============================================================================
# EXAMPLE 3: Inverting Amplifier
# ============================================================================
print("\n\n3. Inverting Amplifier (Gain=-10)")
print("-" * 60)

circuit = amplifiers.inverting(gain=10, r_in=10000)
print(circuit.to_netlist())

values = amplifiers._inverting_template.calculate_values(gain=10, r_in=10000)
print(f"\nCalculated: Rin={values['r_in']/1000}kΩ, Rf={values['r_f']/1000}kΩ")
print(f"Gain: {values['gain']}")

# ============================================================================
# EXAMPLE 4: Voltage Divider
# ============================================================================
print("\n\n4. Voltage Divider (5V → 3.3V)")
print("-" * 60)

circuit = power.voltage_divider(vout=3.3, vin=5, r2=10000)
print(circuit.to_netlist())

values = power._voltage_divider_template.calculate_values(vout=3.3, vin=5, r2=10000)
print(f"\nCalculated: R1={values['r1']/1000:.2f}kΩ, R2={values['r2']/1000}kΩ")
print(f"Ratio: {(values['r2']/(values['r1']+values['r2'])):.3f} = {3.3/5:.3f}")

# ============================================================================
# EXAMPLE 5: Wien Bridge Oscillator
# ============================================================================
print("\n\n5. Wien Bridge Oscillator (1kHz)")
print("-" * 60)

circuit = oscillators.wien_bridge(frequency=1000, r=10000)
print(circuit.to_netlist())

values = oscillators._wien_bridge_template.calculate_values(frequency=1000, r=10000)
print(f"\nCalculated: R={values['r']/1000}kΩ, C={values['c']*1e9:.2f}nF")

# ============================================================================
# EXAMPLE 6: Listing All Templates
# ============================================================================
print("\n\n6. Available Templates")
print("-" * 60)

from ohmspice.templates import list_all_templates

all_templates = list_all_templates()
for category, template_list in all_templates.items():
    print(f"\n{category.upper()}:")
    for info in template_list:
        print(f"  • {info.name:20} - {info.description}")
        if info.parameters:
            params = ", ".join([p.name for p in info.parameters if p.required])
            print(f"    Required: {params}")

# ============================================================================
# EXAMPLE 7: Custom Template Usage
# ============================================================================
print("\n\n7. Custom Usage - Without Source")
print("-" * 60)

# Create filter without voltage source
circuit = filters.rc_lowpass(fc=1000, r=1000, include_source=False)

# Add custom source
circuit.add_voltage_source("Vin", "in", "0", dc=5, ac=1, sine={"amplitude": 1, "frequency": 100})

# Add custom analysis
circuit.add_transient_analysis(stop_time=0.02, step_time=0.0001)

print(circuit.to_netlist())

# ============================================================================
# EXAMPLE 8: Saving Circuits
# ============================================================================
print("\n\n8. Saving to File")
print("-" * 60)

import tempfile
from pathlib import Path

# Create and save
circuit = filters.rc_highpass(fc=10000, r=1000)

temp_dir = Path(tempfile.gettempdir())
output_file = temp_dir / "highpass_filter.cir"

circuit.save(str(output_file))
print(f"✓ Saved to: {output_file}")

# Read back
with open(output_file, "r") as f:
    print(f.read())

# Cleanup
output_file.unlink()

print("\n" + "=" * 60)
print("All examples completed successfully!")
print("=" * 60)
