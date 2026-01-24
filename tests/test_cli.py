"""Tests for CLI commands."""

from click.testing import CliRunner

from ohmspice.cli import main


class TestCLI:
    """Tests for CLI commands."""

    def test_main_help(self) -> None:
        """Test main help command."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "OhmSPICE" in result.output
        assert "templates" in result.output
        assert "new" in result.output
        assert "simulate" in result.output

    def test_version(self) -> None:
        """Test version option."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "ohmspice" in result.output.lower()

    def test_templates_command(self) -> None:
        """Test templates listing command."""
        runner = CliRunner()
        result = runner.invoke(main, ["templates"])
        assert result.exit_code == 0
        assert "Filters" in result.output
        assert "rc_lowpass" in result.output

    def test_templates_verbose(self) -> None:
        """Test templates with verbose flag."""
        runner = CliRunner()
        result = runner.invoke(main, ["templates", "-v"])
        assert result.exit_code == 0
        assert "Parameters" in result.output

    def test_templates_category_filter(self) -> None:
        """Test filtering templates by category."""
        runner = CliRunner()
        result = runner.invoke(main, ["templates", "-c", "filters"])
        assert result.exit_code == 0
        assert "Filters" in result.output
        assert "Amplifiers" not in result.output

    def test_new_lowpass(self) -> None:
        """Test creating lowpass filter."""
        runner = CliRunner()
        result = runner.invoke(main, ["new", "lowpass", "--fc", "1000", "--r", "1k"])
        assert result.exit_code == 0
        assert "RC Low-Pass Filter" in result.output
        assert "R1" in result.output
        assert "C1" in result.output

    def test_new_with_output_file(self) -> None:
        """Test creating circuit with output file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["new", "lowpass", "--fc", "1000", "-o", "test.cir"])
            assert result.exit_code == 0
            assert "Created" in result.output
            # Check file exists
            with open("test.cir") as f:
                content = f.read()
                assert "RC Low-Pass Filter" in content

    def test_new_missing_params(self) -> None:
        """Test new command with missing required parameters."""
        runner = CliRunner()
        result = runner.invoke(main, ["new", "lowpass"])
        assert result.exit_code != 0
        assert "Error" in result.output or "Missing" in result.output

    def test_new_invalid_template(self) -> None:
        """Test new command with invalid template name."""
        runner = CliRunner()
        result = runner.invoke(main, ["new", "nonexistent", "--fc", "1000"])
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_new_voltage_divider(self) -> None:
        """Test creating voltage divider."""
        runner = CliRunner()
        result = runner.invoke(main, ["new", "voltage_divider", "--vout", "3.3", "--vin", "5"])
        assert result.exit_code == 0
        assert "Voltage Divider" in result.output

    def test_schematic_not_implemented(self) -> None:
        """Test schematic command shows not implemented message."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a test file
            with open("test.cir", "w") as f:
                f.write("* Test\n.end")

            result = runner.invoke(main, ["schematic", "test.cir"])
            assert result.exit_code == 0
            assert "v0.3.0" in result.output


class TestInteractiveMode:
    """Tests for interactive mode."""

    def test_interactive_exit(self) -> None:
        """Test exiting interactive mode."""
        runner = CliRunner()
        result = runner.invoke(main, ["interactive"], input="exit\n")
        assert result.exit_code == 0
        assert "Goodbye" in result.output

    def test_interactive_help(self) -> None:
        """Test help command in interactive mode."""
        runner = CliRunner()
        result = runner.invoke(main, ["interactive"], input="help\nexit\n")
        assert result.exit_code == 0
        assert "Commands" in result.output

    def test_interactive_new_circuit(self) -> None:
        """Test creating circuit in interactive mode."""
        runner = CliRunner()
        commands = "new My Circuit\nadd resistor R1 in out 1k\nshow\nexit\n"
        result = runner.invoke(main, ["interactive"], input=commands)
        assert result.exit_code == 0
        assert "Created circuit" in result.output
        assert "Added resistor R1" in result.output
        assert "R1 in out 1k" in result.output

    def test_interactive_full_circuit(self) -> None:
        """Test building complete circuit in interactive mode."""
        runner = CliRunner()
        commands = """new RC Filter
add vsource V1 in 0 ac=1
add resistor R1 in out 1k
add capacitor C1 out 0 159n
analysis ac 1 1000000 20
show
exit
"""
        result = runner.invoke(main, ["interactive"], input=commands)
        assert result.exit_code == 0
        assert "RC Filter" in result.output
        assert ".ac" in result.output
