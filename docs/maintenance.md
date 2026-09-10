# Maintenance

The root `pyproject.toml` and `uv.lock` define the reproducible publication
toolchain. The reviewed standalone artefacts are preserved under `public/`.
`scripts/site.py` builds `_site/` from the explicit manifest and checks its
links, file integrity and public Git inventory. `scripts/browser_check.py`
exercises the actual URLs, guide controls, synthetic evidence check and
downloads. `scripts/impact.py` selects the smaller prose-only CI path.

```sh
uv sync --locked
make validate
uv run --locked playwright install chromium
make browser
```

The browser command starts and stops its own loopback server. To check an
already hosted release, pass `--url https://chris-page-gov.github.io/for-the-kids-FTK/`
and `--expected-sha` followed by the authorised commit SHA.
Receipts and screenshots go into ignored `output/`. Do not publish local paths
or execution transcripts. GitHub Actions retains CI and Pages test receipts.

The guide and demonstration are a frozen teaching snapshot, not a generated
view of a live service. Their source hashes are pinned in the publication
manifest. Review the illustrated narrative before replacing either file.
The original wider authoring and research workspace remains local; it is not
needed to run or validate the published pack.

The nested child-view research toolchain in the owner's private local working
files is outside this release. Its schema and additional locality fixtures
can be reviewed for a later publication without importing the whole folder.
