"""Test cases for main module."""

from unittest.mock import MagicMock, patch

import pytest
import typer
from click.core import Command
from typer.testing import CliRunner

from irrexplorer_cli.main import app, asn, prefix

runner = CliRunner()


def test_exit_with_version() -> None:
    """Test exit with version flag."""
    result = runner.invoke(app, ["--version"])
    assert not result.exit_code


def test_exit_with_help() -> None:
    """Test exit with help display."""
    result = runner.invoke(app, ["prefix"])
    assert "Usage" in result.stdout
    assert not result.exit_code


def test_prefix_command_without_context() -> None:
    """Test prefix command without context."""
    with patch("typer.Context", return_value=None):
        result = runner.invoke(app, ["prefix", ""])
        assert not result.exit_code


def test_invalid_asn_format() -> None:
    """Test exit with invalid ASN format."""
    result = runner.invoke(app, ["asn", "invalid-asn"])
    assert "Error: Invalid ASN format" in result.stdout
    assert result.exit_code == 1


def test_asn_format_conversion() -> None:
    """Test ASN format conversion."""
    result = runner.invoke(app, ["asn", "12345"])
    assert not result.exit_code


def test_prefix_command_with_context() -> None:
    """Test prefix command with context."""
    result = runner.invoke(app, ["prefix"])
    assert not result.exit_code
    assert "Usage" in result.stdout


def test_asn_command_with_context() -> None:
    """Test ASN command with context."""
    result = runner.invoke(app, ["asn"])
    assert not result.exit_code
    assert "Usage" in result.stdout


def test_asn_command_without_context() -> None:
    """Test ASN command without context."""
    with patch("typer.Context", return_value=None):
        result = runner.invoke(app, ["asn", ""])
        assert not result.exit_code


def test_prefix_direct_no_args() -> None:
    """Test prefix function directly with no arguments."""
    with pytest.raises(typer.Exit):
        ctx = typer.Context(Command("test"))
        ctx.obj = {"base_url": "http://example.com"}
        prefix(ctx)


def test_asn_direct_no_args() -> None:
    """Test asn function directly with no arguments."""
    with pytest.raises(typer.Exit):
        ctx = typer.Context(Command("test"))
        ctx.obj = {"base_url": "http://example.com"}
        asn(ctx)


@patch("irrexplorer_cli.main.validate_url_format")
def test_prefix_invalid_url_format(mock_validate_url: MagicMock) -> None:
    """Test prefix command with invalid URL format."""
    mock_validate_url.return_value = False
    ctx = typer.Context(Command("test"))
    ctx.obj = {"base_url": "http://example.com"}
    with pytest.raises(typer.Exit) as exc_info:
        prefix(ctx, "192.0.2.0/24")
    assert exc_info.value.exit_code == 1


@patch("irrexplorer_cli.main.validate_url_format")
def test_asn_invalid_url_format(mock_validate_url: MagicMock) -> None:
    """Test ASN command with invalid URL format."""
    mock_validate_url.return_value = False
    ctx = typer.Context(Command("test"))
    ctx.obj = {"base_url": "http://example.com"}
    with pytest.raises(typer.Exit) as exc_info:
        asn(ctx, "AS12345")
    assert exc_info.value.exit_code == 1
