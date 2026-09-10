# Publication

## Scope

The owner authorised this reviewed synthetic release on 10 September 2026.
`public-git-files.json` lists every file permitted in public Git;
`publication-files.json` lists the smaller Pages artifact. The build adds
`release.json`, identifying the source commit and hashes of the published files.
The two HTML artefacts and restored Word document retain their reviewed bytes.

Do not publish the broader local `docs/` tree. It includes authenticated
collaboration materials, organiser documents, third-party sources and local
execution history. Local possession is not evidence of redistribution rights.
Do not put these files in public Git even if they are excluded from Pages.

The website offers the demonstration, illustrated guide, Word guide and three
synthetic downloads. It is a static educational site with no child lookup,
accounts, live council connection, AI backend or paid API calls. Use the
[limitations page](../public/limits.html) alongside the demonstration.

## Release procedure

1. Obtain an explicit owner request to publish. Ordinary PR merges do not deploy.
2. Merge a reviewed PR after `ftk-ci` succeeds; confirm `main` is protected.
3. Dispatch **Publish reviewed Pages** on `main`, supplying its complete commit
   SHA as `expected_sha`. The workflow rejects another branch or a changed head.
4. The workflow rebuilds and validates that commit, runs the actual browser
   checks and uploads only `_site/`. Deployment uses the `github-pages`
   environment restricted to protected branches.
5. Check the deployed `release.json` against the requested SHA. Run the browser
   check with the live URL and `--expected-sha` and verify the guide, demonstration and Word/JSON
   downloads. Keep the workflow and browser receipts with the release evidence.

The first release is a snapshot of the 9 September demonstration and the
10 September illustrated guide. The landing page links both and explains the
boundary between authored reference answers and a separately supplied AI chat.

## Known limitations

The existing guide records incomplete comparison evidence in the compact JSON,
a parent-card source-pointer limitation, literal relationship-search wording
and keyboard-focus issues in the demonstration. These are disclosed teaching
limitations, not proof of production readiness. The browser's narrow corruption
check tests completion-evidence references; it does not establish real-world
truth, service delivery or lawful access.
