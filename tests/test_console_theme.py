import importlib
import types

from hncli import themes


def test_console_uses_configured_theme(monkeypatch):
    captured = {}

    def fake_console(*args, **kwargs):
        captured["theme"] = kwargs.get("theme")
        return types.SimpleNamespace(print=lambda *a, **kw: None)

    import hncli.cli as cli
    monkeypatch.setattr(cli, "Console", fake_console)
    monkeypatch.setattr(cli.config, "get_setting", lambda k: "dark" if k == "color_theme" else cli.config.DEFAULT_CONFIG.get(k))

    cli = importlib.reload(cli)
    assert captured["theme"] is themes.get_theme("dark")

