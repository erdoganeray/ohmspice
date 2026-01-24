#!/bin/bash
# CLI Demo Script for OhmSPICE
# Demonstrates all major CLI commands

echo "=================================================="
echo "  OhmSPICE CLI Demo"
echo "=================================================="

# Check if ohmspice is installed
if ! command -v ohmspice &> /dev/null; then
    echo "Error: ohmspice not found. Install with: pip install ohmspice"
    exit 1
fi

echo ""
echo "1. Show version"
echo "--------------------------------------------------"
ohmspice --version

echo ""
echo "2. List all templates"
echo "--------------------------------------------------"
ohmspice templates

echo ""
echo "3. List filter templates (verbose)"
echo "--------------------------------------------------"
ohmspice templates -c filters -v

echo ""
echo "4. Create RC low-pass filter (print to console)"
echo "--------------------------------------------------"
ohmspice new lowpass --fc 1000 --r 1k

echo ""
echo "5. Create and save to file"
echo "--------------------------------------------------"
ohmspice new lowpass --fc 1000 --r 1k -o demo_filter.cir
cat demo_filter.cir

echo ""
echo "6. Create voltage divider"
echo "--------------------------------------------------"
ohmspice new voltage_divider --vout 3.3 --vin 5 -o divider.cir
cat divider.cir

echo ""
echo "7. Create bandpass filter"
echo "--------------------------------------------------"
ohmspice new bandpass --fc 1000 --q 10 -o bandpass.cir

echo ""
echo "8. Create inverting amplifier"
echo "--------------------------------------------------"
ohmspice new inverting --gain 10 -o amp.cir

echo ""
echo "9. Simulate circuit (if LTspice is available)"
echo "--------------------------------------------------"
if command -v ltspice &> /dev/null || command -v LTspice &> /dev/null; then
    ohmspice simulate demo_filter.cir
else
    echo "LTspice not found. Skipping simulation."
    echo "Install LTspice from: https://www.analog.com/ltspice"
fi

echo ""
echo "10. Interactive mode help"
echo "--------------------------------------------------"
echo "To start interactive mode, run:"
echo "  ohmspice interactive"
echo ""
echo "Example interactive session:"
echo "  ohmspice> new My Circuit"
echo "  ohmspice> add vsource V1 in 0 ac=1"
echo "  ohmspice> add resistor R1 in out 1k"
echo "  ohmspice> add capacitor C1 out 0 159n"
echo "  ohmspice> analysis ac 1 1000000 20"
echo "  ohmspice> show"
echo "  ohmspice> save circuit.cir"
echo "  ohmspice> exit"

echo ""
echo "11. Cleanup"
echo "--------------------------------------------------"
rm -f demo_filter.cir divider.cir bandpass.cir amp.cir
echo "✓ Cleaned up demo files"

echo ""
echo "=================================================="
echo "  Demo completed!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  • Try: ohmspice interactive"
echo "  • Read docs: https://erdoganeray.github.io/ohmspice"
echo "  • Explore templates: ohmspice templates -v"
