# Working agreements

Use British English, sentence case and plain language. Preserve exact schema
identifiers, URLs, quoted source wording and filenames.

This public repository contains a reviewed synthetic release. The owner's
local checkout also holds unpublished research. Never broadly stage `docs/`,
`tools/` or all untracked files. Public Git must match `public-git-files.json`;
Pages must match `publication-files.json`. Review provenance before adding a
file to either manifest. Do not include authenticated source materials,
personal paths, credentials or internal execution receipts.

Use `uv sync --locked` and `make validate`. Use `make browser` for changes to
HTML, JavaScript, data, publishing policy, tooling or dependencies. Small prose
changes retain static checks and can skip browser installation and execution.

Use a pull request, preserve branch protection and merge only after `ftk-ci`
passes. No additional human reviewer is required for the sole developer.
Publishing is separate: dispatch Pages only following an explicit owner
request, against the current checked `main` commit. Verify the live HTTPS
URLs and the published `release.json` before claiming delivery.

Keep the September 2026 demonstration and guide as a labelled snapshot.
Their limitations are part of the teaching material. Changes require updating
their immutable hashes and reviewing the guide's screenshots and narrative.
Do not describe synthetic locality labels as real council integrations, or
the standalone projection as tested Svelte Explorer acceptance.
