"""Test suite for CLI functionality."""

from unittest.mock import patch

import httpx
import pytest
from typer.testing import CliRunner

from irrexplorer_cli.irrexplorer import IrrExplorer
from irrexplorer_cli.main import app

runner = CliRunner()


def test_query_command_http_error() -> None:
    """Test HTTP error handling in query command."""
    with patch("irrexplorer_cli.irrexplorer.IrrExplorer.fetch_prefix_info") as mock_fetch:
        mock_fetch.side_effect = httpx.HTTPError("Test error")
        result = runner.invoke(app, ["prefix", "5.57.21.0/24"], catch_exceptions=True)
        assert result.exit_code


@pytest.mark.asyncio
async def test_explorer_close_error() -> None:
    """Test error handling during explorer client closure."""
    explorer = IrrExplorer()
    with patch.object(explorer.client, "aclose") as mock_close:
        mock_close.side_effect = RuntimeError("Close error")
        try:
            await explorer.close()
        except RuntimeError as e:
            assert str(e) == "Close error"


def test_callback_without_version() -> None:
    """Test callback execution without version flag."""
    result = runner.invoke(app)
    assert not result.exit_code


def test_query_empty_prefix() -> None:
    """Test query command with empty prefix"""
    result = runner.invoke(app, ["prefix", ""])
    assert not result.exit_code


def test_asn_command() -> None:
    """Test ASN query command."""
    with patch("irrexplorer_cli.irrexplorer.IrrExplorer.fetch_asn_info") as mock_fetch:
        mock_fetch.return_value = {"directOrigin": [], "overlaps": []}
        result = runner.invoke(app, ["asn", "AS202196"])
        assert not result.exit_code


def test_json_output_format() -> None:
    """Test JSON output format."""
    result = runner.invoke(app, ["prefix", "5.57.21.0/24", "--format", "json"])
    assert not result.exit_code


def test_csv_output_format() -> None:
    """Test CSV output format."""
    result = runner.invoke(app, ["prefix", "5.57.21.0/24", "--format", "csv"])
    assert not result.exit_code


def test_query_command() -> None:
    """Test prefix query command execution."""
    result = runner.invoke(app, ["prefix", "5.57.21.0/24"])
    assert not result.exit_code


def test_query_command_invalid_prefix() -> None:
    """Test query command with invalid prefix."""
    result = runner.invoke(app, ["prefix", "invalid"])
    assert "Error: Invalid prefix format" in result.stdout


def test_version_command() -> None:
    """Test version command output."""
    result = runner.invoke(app, ["--version"])
    assert not result.exit_code
    assert "IRR Explorer CLI" in result.stdout


def test_help_command() -> None:
    """Test help command display."""
    result = runner.invoke(app, ["--help"])
    assert not result.exit_code
    assert "Usage" in result.stdout
    assert "Options" in result.stdout


def test_query_without_prefix() -> None:
    """Test query command without prefix argument."""
    result = runner.invoke(app, ["query"])
    assert "Usage" in result.stdout


def test_format_option() -> None:
    """Test format option handling."""
    result = runner.invoke(app, ["prefix", "5.57.21.0/24", "--format", "json"])
    assert not result.exit_code


def test_asn_query_command() -> None:
    """Test ASN query command execution."""
    with patch("irrexplorer_cli.main.async_asn_query", return_value=None) as mock_query:
        result = runner.invoke(app, ["asn", "AS202196"])
        assert not result.exit_code
        mock_query.assert_called_once_with("AS202196", None)
