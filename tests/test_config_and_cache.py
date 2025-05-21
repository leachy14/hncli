import types
from typer.testing import CliRunner
import hncli.cli as cli

runner = CliRunner()

def test_config_set_boolean(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.config, "update_setting", lambda k, v: calls.append((k, v)))
    result = runner.invoke(cli.app, ["config-set", "open_links_in_browser", "false"])
    assert result.exit_code == 0
    assert calls == [("open_links_in_browser", False)]


def test_config_set_int(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.config, "update_setting", lambda k, v: calls.append((k, v)))
    result = runner.invoke(cli.app, ["config-set", "stories_per_page", "15"])
    assert result.exit_code == 0
    assert calls == [("stories_per_page", 15)]


def test_config_get_single_key(monkeypatch):
    monkeypatch.setattr(cli.config, "get_setting", lambda k: "value")
    result = runner.invoke(cli.app, ["config-get", "--key", "foo"])
    assert result.exit_code == 0
    assert "foo: value" in result.output


def test_config_get_all(monkeypatch):
    called = []
    def load_config():
        called.append(True)
        return {"foo": "bar"}
    monkeypatch.setattr(cli.config, "load_config", load_config)
    monkeypatch.setattr(cli, "calculate_stories_per_page", lambda: 10)
    monkeypatch.setattr(cli, "shutil", types.SimpleNamespace(get_terminal_size=lambda: (80, 24)), raising=False)
    result = runner.invoke(cli.app, ["config-get"])
    assert result.exit_code == 0
    assert called == [True]
    assert "foo" in result.output


def test_config_reset(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.config, "save_config", lambda val: calls.append(val))
    result = runner.invoke(cli.app, ["config-reset"])
    assert result.exit_code == 0
    assert calls == [cli.config.DEFAULT_CONFIG]


def test_cache_clear(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.cache, "clear", lambda: calls.append(True))
    result = runner.invoke(cli.app, ["cache-clear"])
    assert result.exit_code == 0
    assert calls == [True]
    assert "Cache cleared" in result.output
