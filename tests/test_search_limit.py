from typer.testing import CliRunner
import hncli.cli as cli

runner = CliRunner()

def test_search_limit(monkeypatch):
    # Prepare fake stories
    stories = [
        {
            "id": i,
            "type": "story",
            "title": f"Story {i}",
            "text": "",
            "score": 0,
            "kids": [],
            "time": 0,
            "url": f"https://example.com/{i}",
        }
        for i in range(10)
    ]

    monkeypatch.setattr(cli, "get_story_ids", lambda t: list(range(10)))
    monkeypatch.setattr(cli, "get_item", lambda i: stories[i])
    monkeypatch.setattr(cli, "show_navigation_menu", lambda *a, **kw: "q")
    monkeypatch.setattr(cli, "clear_screen", lambda: None)
    monkeypatch.setattr(cli, "calculate_stories_per_page", lambda: 10)

    captured = []

    def fake_display(items):
        captured.append(list(items))

    monkeypatch.setattr(cli, "display_stories", fake_display)

    result = runner.invoke(cli.app, ["search", "story", "--limit", "5"])
    assert result.exit_code == 0
    assert captured
    assert len(captured[0]) <= 5
