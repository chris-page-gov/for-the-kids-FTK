# Contributing

Chris Page is the sole repository developer. Use a short branch and pull
request for every change. The protected `main` branch requires the `ftk-ci`
check, resolved conversations and linear history, with zero additional
approving reviewers. Protections also apply to the administrator; force pushes
and branch deletion are blocked.

For a small wording correction, edit the relevant Markdown file, run
`make validate`, and open a pull request. CI runs the static checks without
installing a browser for recognised prose-only changes. Use squash auto-merge
after reviewing the diff. The branch is deleted after merging.

HTML under `public/` is executable application content, not a prose-only
change. Data, scripts, dependencies and publication policy receive the broader
checks. Unrecognised paths receive the broader checks too. Required CI always
runs; do not use a skip-CI commit message.

Keep new public files explicit in `public-git-files.json`. Site files also
need a mapping in `publication-files.json`. Review their sources and rights;
passing a scan cannot grant publication permission.

Merging does not deploy Pages. Follow [the publication procedure](docs/publication.md)
when the owner authorises a release.
