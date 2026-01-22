#!/usr/bin/env python3
"""
Basic RC Low-Pass Filter Example

This example demonstrates how to create a simple RC low-pass filter
circuit, generate its netlist, and simulate it using OhmSPICE.

The filter has a cutoff frequency of 1kHz using:
- R = 1kΩ
- C = 159nF (calculated from fc = 1/(2*pi*R*C))
"""

from ohmspice import Circuit, LTSpice


def main():
    # Create circuit
    circuit = Circuit("RC Low-Pass Filter")

    # Add voltage source (1V AC)
    circuit.add_voltage_source("V1", "in", "0", ac=1)

    # Add resistor (1kΩ)
    circuit.add_resistor("R1", "in", "out", "1k")

    # Add capacitor (159nF for ~1kHz cutoff)
    circuit.add_capacitor("C1", "out", "0", "159n")

    # Add AC analysis from 1Hz to 1MHz
    circuit.add_ac_analysis(start=1, stop=1e6, points_per_decade=10)

    # Print netlist
    print("Generated SPICE Netlist:")
    print("=" * 40)
    print(circuit.to_netlist())
    print("=" * 40)

    # Save netlist to file
    circuit.save("rc_lowpass.cir")
    print("\nNetlist saved to: rc_lowpass.cir")

    # Run simulation if LTspice is available
    if LTSpice.is_available():
        print("\nLTspice detected! Running simulation...")
        sim = LTSpice()
        results = sim.run(circuit)

        # Get frequency and output voltage
        freq = results.get_frequency()
        vout = results.get_voltage("out")

        print(f"\nSimulation completed!")
        print(f"  Points: {len(freq)}")
        print(f"  Frequency range: {freq[0]:.1f} Hz to {freq[-1]:.0f} Hz")

        # Find -3dB point (cutoff frequency)
        import numpy as np
        vout_db = 20 * np.log10(vout)
        idx_3db = np.argmin(np.abs(vout_db - (-3)))
        fc_measured = freq[idx_3db]
        print(f"  Measured -3dB frequency: {fc_measured:.0f} Hz")
        print(f"  Theoretical cutoff: 1000 Hz")
    else:
        print("\nLTspice not found. Install LTspice to run simulation.")
        print("The netlist has been saved and can be simulated manually.")


if __name__ == "__main__":
    main()
