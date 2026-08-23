# Templates

This directory is a synced snapshot of the canonical templates in
[islo-labs/islo-agents](https://github.com/islo-labs/islo-agents), pinned to
the ref in `.pinned-ref`. Never hand-edit anything here; changes land in
islo-agents and arrive via `../scripts/sync_templates.sh`. CI fails on drift.

`.sync-map` maps islo-agents paths to template names here, one `src:dst` per
line. Current templates:

- `feature-delivery/` from `examples/feature-delivery`
- `qa-line/` from `examples/qa`
- `bug-repro/` lands once islo-agents ships it; add it to `.sync-map` and re-pin

Treat every template as a pattern to adapt, not a drop-in: names, repos,
channels, and snapshots are placeholders for your own.
