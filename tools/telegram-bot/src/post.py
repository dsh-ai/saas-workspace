from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import frontmatter

REQUIRED_FIELDS = ("id", "publish_at")


@dataclass
class Post:
    id: str
    publish_at: datetime
    pillar: str
    format: str
    body: str
    path: Path

    @classmethod
    def from_file(cls, path: Path) -> "Post":
        path = Path(path)
        fm = frontmatter.load(path)
        for key in REQUIRED_FIELDS:
            if key not in fm.metadata:
                raise ValueError(f"missing required frontmatter field: {key}")
        if fm["id"] != path.stem:
            raise ValueError(
                f"frontmatter id '{fm['id']}' does not match filename stem '{path.stem}'"
            )
        pub = fm["publish_at"]
        if isinstance(pub, str):
            pub = datetime.fromisoformat(pub)
        return cls(
            id=fm["id"],
            publish_at=pub,
            pillar=fm.metadata.get("pillar", "unknown"),
            format=fm.metadata.get("format", "text"),
            body=fm.content,
            path=path,
        )
