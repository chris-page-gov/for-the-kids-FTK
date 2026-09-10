"""Adversarial publication fixtures; no network or repository mutation outside tempdirs."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile
from io import BytesIO


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


site = load("site")
impact = load("impact")


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.run_git("init", "-q")
        self.run_git("config", "user.name", "Publication fixture")
        self.run_git("config", "user.email", "fixture@example.invalid")
        self.write("LICENSE", "Synthetic fixture licence\n")
        self.run_git("add", "LICENSE")
        self.run_git("commit", "-qm", "Initial fixture")
        self.write("public/index.html", '<!doctype html><html><body id="main"><a href="#main">Start</a></body></html>')
        self.rows = [{"source": "public/index.html", "destination": "index.html"}]
        self.names = ["LICENSE", "public/index.html", "publication-files.json", "public-git-files.json"]
        self.manifests()

    def run_git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True, text=True).stdout

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def manifests(self):
        self.write("publication-files.json", json.dumps({"files": self.rows}))
        self.write("public-git-files.json", json.dumps({"files": self.names}))

    def test_build_is_deterministic_and_working_check_passes(self):
        site.build(self.root)
        first = (self.root / "_site/release.json").read_bytes()
        site.build(self.root)
        self.assertEqual(first, (self.root / "_site/release.json").read_bytes())
        self.assertEqual(site.check(self.root, working=True)["status"], "passed")
        with self.assertRaisesRegex(site.PublicationError, "not tracked"):
            site.check(self.root)
        self.run_git("add", *self.names)
        self.assertEqual(site.check(self.root)["status"], "passed")

    def test_source_and_destination_traversal_rejected(self):
        for key in ("source", "destination"):
            with self.subTest(key=key):
                original = self.rows[0][key]
                self.rows[0][key] = "../outside.html"
                self.manifests()
                with self.assertRaisesRegex(site.PublicationError, "traversal"):
                    site.build(self.root)
                self.rows[0][key] = original

    def test_output_escape_and_root_rejected(self):
        for output in ("../outside", str(self.root), str(self.root.parent / "outside"), ".git/output"):
            with self.subTest(output=output), self.assertRaises(site.PublicationError):
                site.build(self.root, output)

    def test_unexpected_tracked_file_rejected_even_in_working_mode(self):
        site.build(self.root)
        self.write("private-note.md", "Must remain excluded")
        self.run_git("add", "private-note.md")
        with self.assertRaisesRegex(site.PublicationError, "Unexpected tracked files"):
            site.check(self.root, working=True)

    def test_missing_file_link_and_fragment_rejected(self):
        for link, error in (("absent.html", "Missing local link"), ("#absent", "Missing HTML fragment")):
            with self.subTest(link=link):
                self.write("public/index.html", f'<html><body><a href="{link}">Open</a></body></html>')
                with self.assertRaisesRegex(site.PublicationError, error):
                    site.build(self.root)

    def test_source_and_output_corruption_rejected(self):
        self.rows[0]["sha256"] = site.digest((self.root / "public/index.html").read_bytes())
        self.manifests()
        site.build(self.root)
        self.write("_site/index.html", "Changed output")
        with self.assertRaisesRegex(site.PublicationError, "Output hash"):
            site.check(self.root, working=True)
        self.write("public/index.html", "Changed source")
        with self.assertRaisesRegex(site.PublicationError, "Pinned SHA"):
            site.build(self.root)

    def test_symlinks_duplicates_and_extra_output_rejected(self):
        original = self.root / "public/index.html"
        original.rename(self.root / "real.html")
        original.symlink_to(self.root / "real.html")
        with self.assertRaisesRegex(site.PublicationError, "Symlinks"):
            site.build(self.root)
        original.unlink()
        (self.root / "real.html").rename(original)
        self.rows.append(dict(self.rows[0]))
        self.manifests()
        with self.assertRaisesRegex(site.PublicationError, "Duplicate"):
            site.build(self.root)
        self.rows.pop()
        self.manifests()
        site.build(self.root)
        self.write("_site/extra.txt", "Not in the manifest")
        with self.assertRaisesRegex(site.PublicationError, "Unexpected or missing output"):
            site.check(self.root, working=True)

    def test_missing_allowlisted_file_rejected(self):
        site.build(self.root)
        self.names.append("missing.md")
        self.manifests()
        with self.assertRaisesRegex(site.PublicationError, "Required file is missing"):
            site.check(self.root, working=True)

    def test_missing_readme_link_rejected_and_relative_links_pass(self):
        self.names.extend(["README.md", "docs/guide.md"])
        self.write("README.md", '# Overview\n[Guide](docs/guide.md#read-this-heading)\n```md\n[Example](not-a-real-file.md)\n```\n')
        self.write("docs/guide.md", '# Read this heading\n[Home](../README.md#overview)\n[Web](https://example.invalid/not-fetched)\n')
        self.manifests()
        site.build(self.root)
        self.assertEqual(site.check(self.root, working=True)["status"], "passed")
        self.write("README.md", '# Overview\n[Missing](docs/missing.md)\n')
        with self.assertRaisesRegex(site.PublicationError, "Missing or non-allowlisted Markdown link"):
            site.check(self.root, working=True)
        self.write("README.md", '# Overview\n[Guide](docs/guide.md#absent)\n')
        with self.assertRaisesRegex(site.PublicationError, "Missing Markdown link fragment"):
            site.check(self.root, working=True)

    def test_private_content_and_invalid_word_rejected(self):
        with self.assertRaisesRegex(site.PublicationError, "local filesystem"):
            site.check_content("page.html", b"/Users/fictional/private")
        with self.assertRaisesRegex(site.PublicationError, "Basecamp"):
            site.check_content("page.html", b"https://app.basecamp.com/fictional")
        with self.assertRaisesRegex(site.PublicationError, "loopback"):
            site.check_content("page.html", b"http://127.0.0.1:8000/")
        site.check_content("README.md", b"Preview at http://127.0.0.1:8000/", allow_loopback=True)
        with self.assertRaisesRegex(site.PublicationError, "local filesystem"):
            site.check_content("README.md", b"/Users/fictional/private", allow_loopback=True)
        with self.assertRaisesRegex(site.PublicationError, "Invalid Word"):
            site.check_content("guide.docx", b"not a ZIP archive")
        archive = BytesIO()
        with zipfile.ZipFile(archive, "w") as word:
            word.writestr("[Content_Types].xml", "<Types/>")
            word.writestr("_rels/.rels", "<Relationships/>")
            word.writestr("word/document.xml", "<unclosed>")
        with self.assertRaisesRegex(site.PublicationError, "Invalid Word"):
            site.check_content("guide.docx", archive.getvalue())

    def test_release_path_and_cross_page_fragments(self):
        self.rows[0]["destination"] = "release.json/child.html"
        self.manifests()
        with self.assertRaisesRegex(site.PublicationError, "release.json is generated"):
            site.build(self.root)
        site.check_links({
            "index.html": b'<a href="nested/page.html#detail">Detail</a>',
            "nested/page.html": b'<main id="detail"><a href="../index.html">Home</a></main>',
        })
        with self.assertRaisesRegex(site.PublicationError, "Missing HTML fragment"):
            site.check_links({"index.html": b'<a href="page.html#missing">Go</a>', "page.html": b'<main id="detail"/>'})

    def test_impact_only_exempts_named_prose_and_fails_closed(self):
        base = self.run_git("rev-parse", "HEAD").strip()
        self.assertTrue(impact.classify(self.root, base)[0])
        self.write("README.md", "Reviewed prose")
        self.run_git("add", "README.md")
        self.run_git("commit", "-qm", "Prose")
        self.assertFalse(impact.classify(self.root, base)[0])
        self.write("public/unknown.md", "Unknown change")
        self.run_git("add", "public/unknown.md")
        self.run_git("commit", "-qm", "Unknown path")
        self.assertTrue(impact.classify(self.root, base)[0])
        self.assertTrue(impact.classify(self.root, "missing-ref")[0])


if __name__ == "__main__":
    unittest.main()
