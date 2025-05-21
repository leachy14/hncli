from typer.testing import CliRunner
import hncli.cli as cli

runner = CliRunner()

def test_open_auto(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "get_config_value", lambda key, default=None: True)
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: calls.append(url))
    result = runner.invoke(cli.app, ["open", "123"])
    assert result.exit_code == 0
    assert calls == [f"{cli.HN_WEB_URL}/item?id=123"]

def test_open_prompt(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "get_config_value", lambda key, default=None: False)
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: calls.append(url))
    monkeypatch.setattr(cli.typer, "confirm", lambda *a, **kw: True)
    result = runner.invoke(cli.app, ["open", "456"])
    assert result.exit_code == 0
    assert calls == [f"{cli.HN_WEB_URL}/item?id=456"]

def test_user_auto(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "get_config_value", lambda key, default=None: True)
    monkeypatch.setattr(cli, "get_user", lambda u: {"created": 0, "karma": 1, "about": ""})
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: calls.append(url))
    monkeypatch.setattr(cli.typer, "confirm", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("confirm called")))
    result = runner.invoke(cli.app, ["user", "alice"])
    assert result.exit_code == 0
    assert calls == [f"{cli.HN_WEB_URL}/user?id=alice"]

def test_user_prompt(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "get_config_value", lambda key, default=None: False)
    monkeypatch.setattr(cli, "get_user", lambda u: {"created": 0, "karma": 1, "about": ""})
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: calls.append(url))
    monkeypatch.setattr(cli.typer, "confirm", lambda *a, **kw: True)
    result = runner.invoke(cli.app, ["user", "bob"])
    assert result.exit_code == 0
    assert calls == [f"{cli.HN_WEB_URL}/user?id=bob"]
