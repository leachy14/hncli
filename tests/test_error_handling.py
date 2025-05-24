from typer.testing import CliRunner
import pytest
import hncli.cli as cli
from hncli.errors import APIRequestError
import requests

runner = CliRunner()


def test_get_story_ids_network_error(monkeypatch):
    def raise_error(*args, **kwargs):
        raise requests.RequestException("boom")
    monkeypatch.setattr(cli.requests, "get", raise_error)
    with pytest.raises(APIRequestError):
        cli.get_story_ids("top")


def test_cli_handles_api_error(monkeypatch):
    monkeypatch.setattr(cli, "get_story_ids", lambda t: (_ for _ in ()).throw(APIRequestError("fail")))
    result = runner.invoke(cli.app, ["top"])
    assert result.exit_code == 0
    assert "Error fetching top stories" in result.output

