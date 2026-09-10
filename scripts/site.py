#!/usr/bin/env python3
"""Stage and check the exact reviewed public subset. Standard library only."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree
import zipfile


class PublicationError(ValueError):
    """An input or output does not meet the publication contract."""


SHA256 = re.compile(r"[0-9a-f]{64}\Z")
PRIVATE_MARKERS = {
    "local filesystem path": re.compile(r"/Users/|/private/(?:tmp|var)/|file://", re.I),
    "authenticated Basecamp address": re.compile(r"app\.basecamp\.com", re.I),
    "loopback address": re.compile(r"https?://(?:localhost|127\.0\.0\.1)(?=$|[:/\s\"'])", re.I),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub credential": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b"),
    "API credential": re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}\b"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "assigned credential": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)"
        r"\s*[=:]\s*[\"'][A-Za-z0-9_+/=-]{20,}[\"']"
    ),
}


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if result.returncode:
        raise PublicationError(f"Git command failed: {' '.join(args)}")
    return result.stdout


def relative_name(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise PublicationError(f"Invalid repository-relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ("", ".", "..") for p in value.split("/")):
        raise PublicationError(f"Path must be relative without traversal: {value!r}")
    if ".git" in path.parts or ":" in value or any(ord(c) < 32 for c in value):
        raise PublicationError(f"Unsafe publication path: {value!r}")
    return value


def local_file(root: Path, name: str) -> Path:
    path = root
    for part in PurePosixPath(relative_name(name)).parts:
        path = path / part
        if path.is_symlink():
            raise PublicationError(f"Symlinks are not permitted: {name}")
    if not path.is_file():
        raise PublicationError(f"Required file is missing: {name}")
    return path


def read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PublicationError(f"Cannot read JSON: {path.name}") from exc


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def publication_files(root: Path) -> list[dict[str, str]]:
    manifest = read_json(local_file(root, "publication-files.json"))
    if not isinstance(manifest, dict) or set(manifest) != {"files"} or not isinstance(manifest["files"], list):
        raise PublicationError("publication-files.json must contain only a files list")
    sources: set[str] = set()
    destinations: set[str] = set()
    rows = []
    for item in manifest["files"]:
        if not isinstance(item, dict) or not {"source", "destination"} <= set(item) <= {"source", "destination", "sha256"}:
            raise PublicationError("Every publication entry needs source and destination only, with optional sha256")
        source, destination = relative_name(item["source"]), relative_name(item["destination"])
        # Case-insensitive uniqueness also protects the case-insensitive authoring host.
        if source.casefold() in sources or destination.casefold() in destinations:
            raise PublicationError("Duplicate publication source or destination")
        if PurePosixPath(destination.casefold()).parts[0] == "release.json":
            raise PublicationError("release.json is generated and cannot be supplied")
        local_file(root, source)
        expected = item.get("sha256")
        if expected is not None and (not isinstance(expected, str) or not SHA256.fullmatch(expected)):
            raise PublicationError(f"Invalid SHA-256 for {source}")
        sources.add(source.casefold())
        destinations.add(destination.casefold())
        rows.append(dict(item))
    if not rows:
        raise PublicationError("The publication manifest is empty")
    for name in destinations:
        if any(str(p) in destinations for p in PurePosixPath(name).parents if str(p) != "."):
            raise PublicationError("A publication file cannot also be a destination directory")
    return sorted(rows, key=lambda row: row["destination"])


def public_git_files(root: Path, working: bool) -> list[str]:
    manifest = read_json(local_file(root, "public-git-files.json"))
    if not isinstance(manifest, dict) or set(manifest) != {"files"} or not isinstance(manifest["files"], list):
        raise PublicationError("public-git-files.json must contain only a files list")
    names = [relative_name(name) for name in manifest["files"]]
    if len({name.casefold() for name in names}) != len(names):
        raise PublicationError("Duplicate Git allowlist entry")
    expected = set(names)
    if not {"public-git-files.json", "publication-files.json"} <= expected:
        raise PublicationError("The Git allowlist must include both manifests")
    tracked = set(git(root, "ls-files", "-z").rstrip("\0").split("\0")) - {""}
    unexpected = tracked - expected
    if unexpected:
        raise PublicationError("Unexpected tracked files: " + ", ".join(sorted(unexpected)))
    if not working and expected - tracked:
        raise PublicationError("Allowlisted files are not tracked: " + ", ".join(sorted(expected - tracked)))
    for name in names:
        local_file(root, name)
    for row in git(root, "ls-files", "--stage", "-z").split("\0"):
        if row and row.split(" ", 1)[0] not in {"100644", "100755"}:
            raise PublicationError("Tracked symlink, submodule or unsupported Git file mode")
    return sorted(names)


def scan_text(name: str, text: str, allow_loopback: bool = False) -> None:
    for label, pattern in PRIVATE_MARKERS.items():
        if allow_loopback and label == "loopback address":
            continue  # Local preview instructions belong in repository documentation, not site payloads.
        if pattern.search(text):
            # Report the category and file, never the matched credential or private data.
            raise PublicationError(f"Publication content contains {label}: {name}")


def check_content(name: str, data: bytes, allow_loopback: bool = False) -> None:
    if name.lower().endswith(".docx"):
        from io import BytesIO
        try:
            with zipfile.ZipFile(BytesIO(data)) as archive:
                members = archive.namelist()
                if len(members) != len(set(members)) or not {"[Content_Types].xml", "_rels/.rels", "word/document.xml"} <= set(members):
                    raise PublicationError(f"Word package is incomplete or has duplicate entries: {name}")
                if archive.testzip() is not None:
                    raise PublicationError(f"Word ZIP integrity check failed: {name}")
                for member in members:
                    if member.endswith((".xml", ".rels")):
                        content = archive.read(member).decode("utf-8")
                        ElementTree.fromstring(content)
                        scan_text(name, content, allow_loopback)
        except (zipfile.BadZipFile, UnicodeError, OSError, RuntimeError, ElementTree.ParseError) as exc:
            raise PublicationError(f"Invalid Word package: {name}") from exc
        return
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return  # Binary assets are reviewed separately, never treated as proof of no private data.
    scan_text(name, text, allow_loopback)


class HtmlReferences(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "base":
            raise PublicationError("HTML base URLs are not supported; use portable relative links")
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "a" and values.get("name"):
            self.ids.add(values["name"])
        for attr in ("href", "src"):
            if values.get(attr):
                self.links.append(values[attr])


def check_links(files: dict[str, bytes]) -> None:
    pages = {}
    for name, data in files.items():
        if name.lower().endswith((".html", ".htm")):
            parser = HtmlReferences()
            parser.feed(data.decode("utf-8"))
            pages[name] = parser
    for name, parser in pages.items():
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme in {"https", "http", "data", "mailto", "tel"}:
                continue  # No network requests are made by this static check.
            if url.scheme or url.netloc:
                raise PublicationError(f"Unsupported URL scheme in {name}")
            path = unquote(url.path)
            if "\\" in path or "\x00" in path or path.startswith("/"):
                raise PublicationError(f"Non-portable local URL in {name}: {link}")
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), path)) if path else name
            if target == ".." or target.startswith("../"):
                raise PublicationError(f"Link escapes the published site in {name}: {link}")
            if path.endswith("/") or target == ".":
                target = posixpath.join(target, "index.html").removeprefix("./")
            if target not in files:
                raise PublicationError(f"Missing local link in {name}: {link}")
            if url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                raise PublicationError(f"Missing HTML fragment in {name}: {link}")


def without_code_fences(text: str) -> str:
    """Keep prose positions but exclude backtick and tilde fenced examples."""
    lines = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence is None and marker:
            fence = (marker[1][0], len(marker[1]))
        elif fence is not None:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
        else:
            lines.append(line)
    return "\n".join(lines)


def markdown_ids(text: str) -> set[str]:
    """Common GitHub heading anchors, including duplicate suffixes and explicit HTML IDs."""
    prose = without_code_fences(text)
    parser = HtmlReferences()
    parser.feed(prose)
    ids = set(parser.ids)
    counts: dict[str, int] = {}
    for line in prose.splitlines():
        heading = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not heading:
            continue
        label = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", heading[1])
        label = html.unescape(re.sub(r"<[^>]+>", "", label)).lower()
        slug = re.sub(r"[^\w\- ]", "", label).replace(" ", "-")
        suffix = counts.get(slug, 0)
        counts[slug] = suffix + 1
        ids.add(f"{slug}-{suffix}" if suffix else slug)
    return ids


def check_markdown_links(root: Path, names: list[str]) -> None:
    """Check inline Markdown file links against the public Git allowlist, offline."""
    allowed = set(names)
    anchors: dict[str, set[str]] = {}
    for name in names:
        if name.lower().endswith(".md"):
            anchors[name] = markdown_ids(local_file(root, name).read_text(encoding="utf-8"))
        elif name.lower().endswith((".html", ".htm")):
            parser = HtmlReferences()
            parser.feed(local_file(root, name).read_text(encoding="utf-8"))
            anchors[name] = parser.ids
    for name in names:
        if not name.lower().endswith(".md"):
            continue
        prose = without_code_fences(local_file(root, name).read_text(encoding="utf-8"))
        for match in re.finditer(r"!?\[[^\]\n]*\]\((<[^>\n]+>|[^)\n]+)\)", prose):
            value = match[1].strip()
            link = value[1:-1] if value.startswith("<") else re.split(r"\s+[\"']", value, maxsplit=1)[0]
            url = urlsplit(html.unescape(link))
            if url.scheme in {"https", "http", "mailto", "tel", "data"}:
                continue
            if url.scheme or url.netloc:
                raise PublicationError(f"Unsupported Markdown URL scheme in {name}")
            path = unquote(url.path)
            if path.startswith("/") or "\\" in path or "\x00" in path:
                raise PublicationError(f"Non-portable Markdown link in {name}: {link}")
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), path)) if path else name
            if target == ".." or target.startswith("../"):
                raise PublicationError(f"Markdown link escapes the repository in {name}: {link}")
            if target not in allowed:
                raise PublicationError(f"Missing or non-allowlisted Markdown link in {name}: {link}")
            local_file(root, target)
            if url.fragment and target in anchors and unquote(url.fragment) not in anchors[target]:
                raise PublicationError(f"Missing Markdown link fragment in {name}: {link}")


def payload(root: Path, rows: list[dict[str, str]]) -> dict[str, bytes]:
    files = {}
    for row in rows:
        data = local_file(root, row["source"]).read_bytes()
        if "sha256" in row and digest(data) != row["sha256"]:
            raise PublicationError(f"Pinned SHA-256 mismatch: {row['source']}")
        check_content(row["source"], data)
        files[row["destination"]] = data
    release = {
        "commit": git(root, "rev-parse", "--verify", "HEAD").strip(),
        "files": [{"path": name, "sha256": digest(data), "bytes": len(data)} for name, data in sorted(files.items())],
    }
    files["release.json"] = (json.dumps(release, indent=2, sort_keys=True) + "\n").encode()
    check_links(files)
    return files


def output_path(root: Path, output: str, rows: list[dict[str, str]]) -> Path:
    root = root.resolve()
    candidate = Path(output)
    candidate = candidate if candidate.is_absolute() else root / candidate
    # Check lexical components before resolving so symlinks cannot disappear.
    if ".." in candidate.parts:
        raise PublicationError("Output path must not contain traversal")
    try:
        rel = candidate.relative_to(root)
    except ValueError as exc:
        raise PublicationError("Output must remain inside the repository") from exc
    if not rel.parts or ".git" in rel.parts:
        raise PublicationError("Output cannot be the repository root or Git metadata")
    node = root
    for part in rel.parts:
        node /= part
        if node.is_symlink():
            raise PublicationError("Output path must not contain symlinks")
    protected = [row["source"] for row in rows] + ["scripts/site.py", "scripts/impact.py", "publication-files.json", "public-git-files.json"]
    allowlist = root / "public-git-files.json"
    if allowlist.is_file():
        obj = read_json(allowlist)
        if isinstance(obj, dict) and isinstance(obj.get("files"), list):
            protected.extend(relative_name(name) for name in obj["files"])
    if any((root / source).is_relative_to(candidate) for source in protected):
        raise PublicationError("Output would contain reviewed source or repository configuration")
    return candidate


def output_inventory(output: Path) -> set[str]:
    if not output.is_dir():
        raise PublicationError("Site output does not exist; run build first")
    names = set()
    for path in output.rglob("*"):
        if path.is_symlink():
            raise PublicationError("Site output contains a symlink")
        if path.is_file():
            names.add(path.relative_to(output).as_posix())
    return names


def build(root: Path, output: str = "_site") -> dict[str, object]:
    rows = publication_files(root)
    files = payload(root, rows)
    target = output_path(root, output, rows)
    if target.exists():
        existing = output_inventory(target)
        if existing:
            release = read_json(target / "release.json") if "release.json" in existing else None
            recognised = (
                isinstance(release, dict) and set(release) == {"commit", "files"}
                and isinstance(release["commit"], str) and re.fullmatch(r"[0-9a-f]{40,64}", release["commit"])
                and isinstance(release["files"], list)
            )
            if not recognised:
                raise PublicationError("Refusing to replace an output directory not generated by this tool")
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".site-stage-", dir=target.parent))
    try:
        for name, data in files.items():
            path = staging / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        if target.exists():
            shutil.rmtree(target)
        os.replace(staging, target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return {"status": "built", "files": len(files), "output": str(target.relative_to(root.resolve()))}


def check(root: Path, output: str = "_site", working: bool = False) -> dict[str, object]:
    names = public_git_files(root, working)
    rows = publication_files(root)
    if any(row["source"] not in names for row in rows):
        raise PublicationError("Every site source must be in the public Git allowlist")
    published_sources = {row["source"] for row in rows}
    for name in names:
        # The scanner and adversarial fixtures intentionally contain forbidden-pattern literals.
        if name == "scripts/site.py" or name.startswith("tests/"):
            continue
        check_content(name, local_file(root, name).read_bytes(), allow_loopback=name not in published_sources)
    check_markdown_links(root, names)
    expected = payload(root, rows)
    target = output_path(root, output, rows)
    actual = output_inventory(target)
    if actual != set(expected):
        raise PublicationError(f"Unexpected or missing output files: {sorted(actual ^ set(expected))}")
    for name, data in expected.items():
        if (target / name).read_bytes() != data:
            raise PublicationError(f"Output hash/content mismatch: {name}")
    return {"status": "passed", "tracked_allowlist": len(names), "site_files": len(expected), "working": working}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("build", "check"):
        child = commands.add_parser(command)
        child.add_argument("--output", default="_site")
        if command == "check":
            child.add_argument("--working", action="store_true", help="Permit reviewed files that are not yet tracked; never permit extra tracked files")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        result = build(root, args.output) if args.command == "build" else check(root, args.output, args.working)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (PublicationError, OSError, UnicodeError) as exc:
        print(f"Publication check failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
