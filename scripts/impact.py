#!/usr/bin/env python3
"""Classify a diff conservatively; static publication checks always run."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


PROSE_ONLY = frozenset({
    "README.md", "CONTRIBUTING.md", "docs/maintenance.md",
    "docs/publication.md", "docs/linkedin-post.md",
})


def classify(root: Path, base: str) -> tuple[bool, list[str], str]:
    result = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", "-z", "--no-renames", f"{base}...HEAD", "--"],
        text=True, capture_output=True,
    )
    if result.returncode:
        return True, [], "Base comparison unavailable; browser checks required"
    changed = sorted(set(result.stdout.rstrip("\0").split("\0")) - {""})
    if not changed:
        return True, [], "Empty comparison; browser checks required"
    required = any(name not in PROSE_ONLY for name in changed)
    return required, changed, "Only explicitly exempt prose paths changed" if not required else "Published content, tooling or an unclassified path changed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    browser, _changed, reason = classify(root, args.base)
    print("static=true")
    print(f"browser={str(browser).lower()}")
    print(f"reason={reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
