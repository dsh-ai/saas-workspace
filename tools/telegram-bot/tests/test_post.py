from datetime import datetime
from pathlib import Path
import pytest
from src.post import Post

FIXTURE = Path(__file__).parent / "fixtures/2026-05-12-1000-lost-deal.md"


def test_parses_frontmatter_and_body():
    post = Post.from_file(FIXTURE)
    assert post.id == "2026-05-12-1000-lost-deal"
    assert post.publish_at == datetime.fromisoformat("2026-05-12T10:00:00+03:00")
    assert post.pillar == "pain"
    assert post.format == "text"
    assert "Вчера потерял сделку" in post.body


def test_id_matches_filename():
    post = Post.from_file(FIXTURE)
    assert post.id == FIXTURE.stem


def test_rejects_missing_publish_at(tmp_path):
    bad = tmp_path / "bad.md"
    bad.write_text("---\nid: bad\n---\nbody")
    with pytest.raises(ValueError, match="publish_at"):
        Post.from_file(bad)


def test_rejects_id_mismatch(tmp_path):
    bad = tmp_path / "actual-name.md"
    bad.write_text("---\nid: different-id\npublish_at: 2026-05-12T10:00:00+03:00\n---\nbody")
    with pytest.raises(ValueError, match="id"):
        Post.from_file(bad)


def test_defaults_for_optional_fields(tmp_path):
    f = tmp_path / "minimal.md"
    f.write_text("---\nid: minimal\npublish_at: 2026-05-12T10:00:00+03:00\n---\nbody")
    post = Post.from_file(f)
    assert post.pillar == "unknown"
    assert post.format == "text"
