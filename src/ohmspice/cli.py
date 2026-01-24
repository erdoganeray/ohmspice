"""Command-line interface for OhmSPICE.

This module provides the CLI for OhmSPICE using Click framework.

Commands:
    templates - List available circuit templates
    new       - Create a new circuit from template
    simulate  - Simulate a SPICE netlist
    schematic - Generate schematic diagram
    interactive - Start interactive mode

Example:
    $ ohmspice templates
    $ ohmspice new lowpass --fc 1000 --r 1k -o filter.cir
    $ ohmspice simulate filter.cir --analysis ac --plot
"""

import sys
from pathlib import Path
from typing import Any

import click

from ohmspice import __version__
from ohmspice.components.utils import parse_value


# Template registry - lazy loaded
def _get_all_templates() -> dict[str, Any]:
    """Get all available templates from all categories."""
    from ohmspice.templates import amplifiers, filters, oscillators, power

    all_templates: dict[str, Any] = {}

    # Filters
    for name, template in filters.FILTER_TEMPLATES.items():
        all_templates[name] = template

    # Amplifiers
    for name, template in amplifiers.AMPLIFIER_TEMPLATES.items():
        all_templates[name] = template

    # Oscillators
    for name, template in oscillators.OSCILLATOR_TEMPLATES.items():
        all_templates[name] = template

    # Power
    for name, template in power.POWER_TEMPLATES.items():
        all_templates[name] = template

    return all_templates


def _get_template_by_name(name: str) -> Any:
    """Get a template by name."""
    templates = _get_all_templates()
    # Handle aliases
    aliases = {
        "lowpass": "rc_lowpass",
        "highpass": "rc_highpass",
        "bandpass": "rlc_bandpass",
        "notch": "rlc_notch",
    }
    name = aliases.get(name.lower(), name.lower())
    return templates.get(name)


@click.group()
@click.version_option(version=__version__, prog_name="ohmspice")
def main() -> None:
    """OhmSPICE - SPICE circuit toolkit with AI integration.

    A hybrid toolkit for electronic circuit design that combines
    template-based circuit design with AI-powered capabilities.
    """
    pass


@main.command("templates")
@click.option(
    "--category",
    "-c",
    type=click.Choice(["filters", "amplifiers", "oscillators", "power", "all"]),
    default="all",
    help="Filter templates by category",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed info")
def list_templates(category: str, verbose: bool) -> None:
    """List available circuit templates."""
    from ohmspice.templates import amplifiers, filters, oscillators, power

    categories = {
        "filters": ("Filters", filters.list_templates()),
        "amplifiers": ("Amplifiers", amplifiers.list_templates()),
        "oscillators": ("Oscillators", oscillators.list_templates()),
        "power": ("Power", power.list_templates()),
    }

    cats_to_show = list(categories.keys()) if category == "all" else [category]

    click.echo("\n" + click.style("╔════════════════════════════════════════╗", fg="cyan"))
    click.echo(click.style("║     OhmSPICE Circuit Templates         ║", fg="cyan", bold=True))
    click.echo(click.style("╚════════════════════════════════════════╝", fg="cyan"))

    for cat in cats_to_show:
        title, templates = categories[cat]
        click.echo(f"\n{click.style(f'📁 {title}', fg='yellow', bold=True)}")
        click.echo("─" * 40)

        for info in templates:
            click.echo(f"  {click.style(info.name, fg='green', bold=True)}")
            if verbose:
                click.echo(f"    {info.description}")
                if info.parameters:
                    params_str = ", ".join(
                        [f"{p.name}" + (f" ({p.unit})" if p.unit else "") for p in info.parameters]
                    )
                    click.echo(f"    Parameters: {params_str}")
                click.echo()

    click.echo(
        f"\n{click.style('Usage:', fg='blue', bold=True)} ohmspice new <template> [options]\n"
    )


@main.command("new")
@click.argument("template")
@click.option("--fc", type=float, help="Cutoff/center frequency (Hz)")
@click.option("--r", "resistance", type=str, help="Resistance value (e.g., 1k, 10k)")
@click.option("--c", "capacitance", type=str, help="Capacitance value (e.g., 100n, 1u)")
@click.option("--l", "inductance", type=str, help="Inductance value (e.g., 10m, 100u)")
@click.option("--q", type=float, help="Quality factor")
@click.option("--gain", type=float, help="Gain value")
@click.option("--vout", type=float, help="Output voltage")
@click.option("--vin", type=float, help="Input voltage")
@click.option("--frequency", type=float, help="Oscillation frequency (Hz)")
@click.option("--output", "-o", type=click.Path(), help="Output file (.cir)")
@click.option("--simulate", is_flag=True, help="Run simulation after creating")
@click.option("--no-source", is_flag=True, help="Don't include voltage source")
def new_circuit(
    template: str,
    fc: float | None,
    resistance: str | None,
    capacitance: str | None,
    inductance: str | None,
    q: float | None,
    gain: float | None,
    vout: float | None,
    vin: float | None,
    frequency: float | None,
    output: str | None,
    simulate: bool,
    no_source: bool,
) -> None:
    """Create a new circuit from template.

    TEMPLATE is the name of the template to use (e.g., lowpass, rc_lowpass).

    Examples:

        ohmspice new lowpass --fc 1000 --r 1k

        ohmspice new voltage_divider --vout 3.3 --vin 5 -o divider.cir
    """
    tmpl = _get_template_by_name(template)
    if tmpl is None:
        click.echo(click.style(f"Error: Template '{template}' not found.", fg="red"))
        click.echo("Use 'ohmspice templates' to see available templates.")
        sys.exit(1)

    # Build parameters
    params: dict[str, Any] = {"include_source": not no_source}

    if fc is not None:
        params["fc"] = fc
    if frequency is not None:
        params["frequency"] = frequency
    if resistance is not None:
        params["r"] = parse_value(resistance)
    if capacitance is not None:
        params["c"] = parse_value(capacitance)
    if inductance is not None:
        params["l"] = parse_value(inductance)
    if q is not None:
        params["q"] = q
    if gain is not None:
        params["gain"] = gain
    if vout is not None:
        params["vout"] = vout
    if vin is not None:
        params["vin"] = vin

    try:
        circuit = tmpl.create(**params)
    except TypeError as e:
        click.echo(click.style("Error: Missing required parameter.", fg="red"))
        click.echo(f"Details: {e}")
        info = tmpl.info()
        required = [p.name for p in info.parameters if p.required]
        if required:
            click.echo(f"Required parameters: {', '.join(required)}")
        sys.exit(1)
    except KeyError as e:
        click.echo(click.style(f"Error: Missing required parameter: {e}", fg="red"))
        info = tmpl.info()
        required = [p.name for p in info.parameters if p.required]
        if required:
            click.echo(f"Required parameters: {', '.join(required)}")
        sys.exit(1)
    except ValueError as e:
        click.echo(click.style("Error: Invalid parameter value.", fg="red"))
        click.echo(f"Details: {e}")
        sys.exit(1)

    netlist = circuit.to_netlist()

    if output:
        output_path = Path(output)
        circuit.save(str(output_path))
        click.echo(click.style(f"✓ Created: {output_path}", fg="green"))
    else:
        click.echo(click.style("\n─── Generated Netlist ───", fg="cyan"))
        click.echo(netlist)

    if simulate:
        click.echo(click.style("\n🔧 Running simulation...", fg="yellow"))
        try:
            from ohmspice.simulators import LTSpice

            sim = LTSpice()
            if output:
                sim.run_netlist(str(output_path))
            else:
                # Save to temp file
                import tempfile

                with tempfile.NamedTemporaryFile(mode="w", suffix=".cir", delete=False) as f:
                    f.write(netlist)
                    temp_path = f.name
                sim.run_netlist(temp_path)
                Path(temp_path).unlink()

            click.echo(click.style("✓ Simulation completed!", fg="green"))
        except ImportError:
            click.echo(click.style("Warning: Simulator not available.", fg="yellow"))
        except Exception as e:
            click.echo(click.style(f"Simulation error: {e}", fg="red"))


@main.command("simulate")
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--analysis", "-a", type=click.Choice(["ac", "dc", "tran", "op"]), help="Analysis type"
)
@click.option("--plot", is_flag=True, help="Show plot after simulation")
@click.option("--output", "-o", type=click.Path(), help="Save results to file")
def simulate_circuit(file: str, analysis: str | None, plot: bool, output: str | None) -> None:
    """Simulate a SPICE netlist.

    FILE is the path to the netlist file (.cir, .net, .sp).

    Examples:

        ohmspice simulate filter.cir --plot

        ohmspice simulate circuit.net -a ac -o results.csv
    """
    file_path = Path(file)

    try:
        from ohmspice.simulators import LTSpice

        click.echo(click.style(f"🔧 Simulating: {file_path.name}", fg="yellow"))

        sim = LTSpice()
        results = sim.run_netlist(str(file_path))

        click.echo(click.style("✓ Simulation completed!", fg="green"))

        if results:
            # Show available data
            click.echo(f"\nVariables: {len(results.variables)}")
            for var in results.variables[:10]:  # First 10
                click.echo(f"  • {var}")
            if len(results.variables) > 10:
                click.echo(f"  ... and {len(results.variables) - 10} more")

        if plot:
            click.echo(click.style("\n📊 Plotting results...", fg="cyan"))
            # TODO: Implement plotting

        if output:
            click.echo(click.style(f"\n💾 Saving results to: {output}", fg="cyan"))
            # TODO: Implement result saving

    except ImportError:
        click.echo(click.style("Error: Simulator not installed.", fg="red"))
        click.echo("Install LTspice or ensure it's in your PATH.")
        sys.exit(1)
    except FileNotFoundError:
        click.echo(click.style("Error: LTspice not found.", fg="red"))
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Simulation error: {e}", fg="red"))
        sys.exit(1)


@main.command("schematic")
@click.argument("file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file (png, svg, pdf)")
@click.option(
    "--style",
    type=click.Choice(["default", "ieee", "european"]),
    default="default",
    help="Schematic style",
)
@click.option("--show-values/--no-values", default=True, help="Show component values")
@click.option("--show-nodes/--no-nodes", default=False, help="Show node names")
def generate_schematic(
    file: str,
    output: str | None,
    style: str,
    show_values: bool,
    show_nodes: bool,
) -> None:
    """Generate schematic diagram from netlist.

    FILE is the path to the netlist file (.cir, .net, .sp).

    Examples:

        ohmspice schematic filter.cir -o schematic.png

        ohmspice schematic circuit.net --style ieee -o circuit.svg
    """
    click.echo(click.style("⚠️  Schematic generation will be available in v0.3.0", fg="yellow"))
    click.echo("This feature requires the visualization module (Phase 3).")


@main.command("interactive")
def interactive_mode() -> None:
    """Start interactive circuit builder mode.

    Provides a REPL-style interface for building circuits interactively.

    Commands:
        add <type> <name> <node1> <node2> <value>
        analysis <type> [params...]
        simulate
        plot <type>
        save <filename>
        help
        exit
    """
    click.echo(click.style("\n╔════════════════════════════════════════╗", fg="cyan"))
    click.echo(click.style("║   OhmSPICE Interactive Mode            ║", fg="cyan", bold=True))
    click.echo(click.style("╚════════════════════════════════════════╝", fg="cyan"))
    click.echo("Type 'help' for commands, 'exit' to quit.\n")

    from ohmspice import Circuit

    circuit: Circuit | None = None
    circuit_name = "Interactive Circuit"

    def show_help() -> None:
        click.echo("""
Commands:
  new [name]                     - Create new circuit
  add resistor <name> <n1> <n2> <value>
  add capacitor <name> <n1> <n2> <value>
  add inductor <name> <n1> <n2> <value>
  add vsource <name> <n+> <n-> [dc=V] [ac=V]
  analysis ac <start> <stop> [points]
  analysis dc <source> <start> <stop> <step>
  analysis tran <stop_time>
  show                           - Show current netlist
  simulate                       - Run simulation
  save <filename>                - Save netlist to file
  clear                          - Clear circuit
  help                           - Show this help
  exit                           - Exit interactive mode
        """)

    def parse_add(args: list[str]) -> None:
        nonlocal circuit
        if circuit is None:
            circuit = Circuit(circuit_name)

        if len(args) < 5:
            click.echo(click.style("Error: add requires type, name, node1, node2, value", fg="red"))
            return

        comp_type, name, n1, n2, value = args[0], args[1], args[2], args[3], args[4]

        try:
            if comp_type == "resistor":
                circuit.add_resistor(name, n1, n2, value)
            elif comp_type == "capacitor":
                circuit.add_capacitor(name, n1, n2, value)
            elif comp_type == "inductor":
                circuit.add_inductor(name, n1, n2, value)
            elif comp_type in ("vsource", "voltage"):
                # Parse dc/ac values
                dc_val = None
                ac_val = None
                for arg in args[4:]:
                    if arg.startswith("dc="):
                        dc_val = float(arg[3:])
                    elif arg.startswith("ac="):
                        ac_val = float(arg[3:])
                circuit.add_voltage_source(name, n1, n2, dc=dc_val, ac=ac_val)
            else:
                click.echo(click.style(f"Unknown component type: {comp_type}", fg="red"))
                return

            click.echo(click.style(f"✓ Added {comp_type} {name}", fg="green"))
        except Exception as e:
            click.echo(click.style(f"Error: {e}", fg="red"))

    def parse_analysis(args: list[str]) -> None:
        nonlocal circuit
        if circuit is None:
            click.echo(click.style("Error: Create circuit first with 'new'", fg="red"))
            return

        if not args:
            click.echo(click.style("Error: Specify analysis type (ac, dc, tran)", fg="red"))
            return

        anal_type = args[0]
        try:
            if anal_type == "ac" and len(args) >= 3:
                start, stop = float(args[1]), float(args[2])
                points = int(args[3]) if len(args) > 3 else 10
                circuit.add_ac_analysis(start=start, stop=stop, points_per_decade=points)
                click.echo(click.style("✓ Added AC analysis", fg="green"))
            elif anal_type == "dc" and len(args) >= 5:
                source, start, stop, step = args[1], float(args[2]), float(args[3]), float(args[4])
                circuit.add_dc_analysis(source, start, stop, step)
                click.echo(click.style("✓ Added DC analysis", fg="green"))
            elif anal_type == "tran" and len(args) >= 2:
                stop_time = float(args[1])
                circuit.add_transient_analysis(stop_time=stop_time)
                click.echo(click.style("✓ Added transient analysis", fg="green"))
            elif anal_type == "op":
                circuit.add_op_analysis()
                click.echo(click.style("✓ Added OP analysis", fg="green"))
            else:
                click.echo(click.style("Invalid analysis command", fg="red"))
        except Exception as e:
            click.echo(click.style(f"Error: {e}", fg="red"))

    while True:
        try:
            prompt = click.style("ohmspice> ", fg="cyan", bold=True)
            line = click.prompt(prompt, prompt_suffix="", default="", show_default=False)
            line = line.strip()

            if not line:
                continue

            parts = line.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "exit" or cmd == "quit":
                click.echo("Goodbye!")
                break
            elif cmd == "help":
                show_help()
            elif cmd == "new":
                circuit_name = " ".join(args) if args else "Interactive Circuit"
                circuit = Circuit(circuit_name)
                click.echo(click.style(f"✓ Created circuit: {circuit_name}", fg="green"))
            elif cmd == "add":
                parse_add(args)
            elif cmd == "analysis":
                parse_analysis(args)
            elif cmd == "show":
                if circuit:
                    click.echo(click.style("\n─── Netlist ───", fg="cyan"))
                    click.echo(circuit.to_netlist())
                else:
                    click.echo("No circuit created. Use 'new' first.")
            elif cmd == "save":
                if circuit and args:
                    circuit.save(args[0])
                    click.echo(click.style(f"✓ Saved to: {args[0]}", fg="green"))
                else:
                    click.echo("Usage: save <filename>")
            elif cmd == "clear":
                circuit = None
                click.echo("Circuit cleared.")
            elif cmd == "simulate":
                click.echo(click.style("Simulation requires saving first.", fg="yellow"))
            else:
                click.echo(click.style(f"Unknown command: {cmd}", fg="red"))
                click.echo("Type 'help' for available commands.")

        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye!")
            break
        except Exception as e:
            click.echo(click.style(f"Error: {e}", fg="red"))


if __name__ == "__main__":
    main()
