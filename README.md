# For the kids: a reusable early-years handover

A tangible output from Squad 11, Challenge 3, at the early-years innovation
hackathon on 9 September 2026. Explore how a family priority, a handover,
an owned action and its evidence can travel together in a reusable bundle.

**All child and family records are fictional.** Bristol and Wigan are labels
on synthetic variants, not sources of real child data or working integrations.

- [Start here](https://chris-page-gov.github.io/for-the-kids-FTK/)
- [Try the demonstration](https://chris-page-gov.github.io/for-the-kids-FTK/FTK_OKF_handover.html)
- [Follow the illustrated walkthrough](https://chris-page-gov.github.io/for-the-kids-FTK/FTK_OKF_illustrated_walkthrough.html)
- [Download the Word guide](public/FTK_OKF_illustrated_walkthrough.docx)
- [Read the scope and limitations](https://chris-page-gov.github.io/for-the-kids-FTK/limits.html)

The standalone demonstration has 13 concepts and 17 directed relationships.
The guide has 22 steps with 32 actual browser screenshots and parallel accounts
for a complete novice and a senior manager. Both HTML files work offline;
keep them together to follow the guide's link to the demonstration.

## Try the bundle with AI

Download [the OKF JSON](public/downloads/okf-bundle.json), attach it to your
chosen AI chat and use the prompt under **Use the bundle with AI** on the
[start page](https://chris-page-gov.github.io/for-the-kids-FTK/#ai).
Ask for the next action, owner, due date and unresolved information, with
concept routes and source pointers. Check the answer against the records.
The demonstration's reference answers are authored examples; it calls no AI.

This is an independent experimental OKF 0.2 projection. Import into the Svelte
Explorer has not been tested for this standalone release. An identifier,
schema check or AI answer does not establish identity, information-sharing
permission or a real-world outcome.

## Maintain and publish

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```sh
uv sync --locked
make validate
uv run --locked playwright install chromium
make browser
```

Serve a local preview with `uv run --locked python -m http.server 4176
--bind 127.0.0.1 --directory _site` (on one line). Open
`http://127.0.0.1:4176/` in a local browser.

- [Contributing](CONTRIBUTING.md): the protected solo-developer workflow.
- [Maintenance](docs/maintenance.md): commands, checks and source layout.
- [Publication](docs/publication.md): file selection, release and verification.

Only the explicitly reviewed public files are included. Wider research,
organiser documents and local execution records are not part of this release.
The [MIT licence](LICENSE) applies to this repository's published material.
