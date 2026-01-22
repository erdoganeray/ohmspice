#!/usr/bin/env python3
"""
Basic RC Low-Pass Filter Example

This example demonstrates how to create a simple RC low-pass filter
circuit, generate its netlist, and simulate it using OhmSPICE.

The filter has a cutoff frequency of 1kHz using:
- R = 1kΩ
- C = 159nF (calculated from fc = 1/(2*pi*R*C))
"""

# Note: This is a placeholder example that will be fully functional
# after the core library is implemented in Phase 1.

# Future usage:
# from ohmspice import Circuit, Simulator, templates
#
# # Use a template with auto-calculation
# circuit = templates.lowpass_rc(fc=1000, r=1000)  # fc=1kHz, R=1kΩ → C calculated
#
# # Or build manually
# circuit = Circuit("RC Low-Pass Filter")
# circuit.add_voltage_source("V1", "in", "gnd", ac=1)
# circuit.add_resistor("R1", "in", "out", "1k")
# circuit.add_capacitor("C1", "out", "gnd", "159n")
#
# # Add AC analysis
# circuit.add_ac_analysis(start=1, stop=1e6, points_per_decade=10)
#
# # Generate and print netlist
# print(circuit.to_netlist())
#
# # Simulate
# sim = Simulator("ltspice")
# results = sim.run(circuit)
# results.bode_plot(output="bode.png")

if __name__ == "__main__":
    print("OhmSPICE Basic RC Filter Example")
    print("=" * 40)
    print()
    print("This example will be fully functional after Phase 1 implementation.")
    print()
    print("Expected circuit:")
    print("  * RC Low-Pass Filter")
    print("  R1 in out 1k")
    print("  C1 out 0 159n")
    print("  V1 in 0 AC 1")
    print("  .ac dec 10 1 1meg")
    print("  .end")
