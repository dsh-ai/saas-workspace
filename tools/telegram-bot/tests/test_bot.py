from datetime import datetime, timezone
from pathlib import Path
from src.bot import approval_keyboard, format_approval_card
from src.post import Post


def make_post(tmp_path):
    f = tmp_path / "2026-05-12-1000-test.md"
    f.write_text(
        "---\nid: 2026-05-12-1000-test\n"
        "publish_at: 2026-05-12T10:00:00+03:00\n"
        "pillar: pain\nformat: text\n---\n"
        "Hello body"
    )
    return Post.from_file(f)


def test_approval_keyboard_has_three_buttons():
    kb = approval_keyboard("post-1")
    row = kb.inline_keyboard[0]
    assert len(row) == 3
    assert row[0].callback_data == "approve:post-1"
    assert row[1].callback_data == "reject:post-1"
    assert row[2].callback_data == "snooze:post-1"


def test_format_approval_card_includes_id_and_body(tmp_path):
    post = make_post(tmp_path)
    text = format_approval_card(post)
    assert "2026-05-12-1000-test" in text
    assert "Hello body" in text
    assert "pain" in text
