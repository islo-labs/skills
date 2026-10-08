# Machine lifecycle

Inspect the checked-out repositories, their documentation, manifests, and CI before choosing build and start commands. Discover every component and its dependencies. Build and verify the stack, and record failures with actionable diagnostics.

Keep durable setup in `/workspace/.islo/machine/cli` and generated Machine files, outside the repositories. Its `start`, `health`, and `stop` commands should be idempotent. `health` writes `/workspace/.islo/machine/verification.json` with a result for each discovered component; `/workspace/.islo/machine/findings.md` explains failures and recovery steps. Leave repositories suitable for snapshot without temporary diagnostic edits or files.

After `cli start` and `cli health`, use [live run surfaces](surfaces.md) to publish the useful interfaces while their backing processes remain running. Continue review and verification while those interfaces are available. Run `cli stop` before the inspect stage finishes so the next stage can save the prepared sandbox snapshot. Do not save the snapshot from inspect.

The generated `/workspace/.islo/machine/skills/islo-machine/SKILL.md` must identify local components, link the findings and verification report, and record each useful Machine-specific Surface recipe: its kind, label, backing process start command, readiness check, and publication command. Future Machine-backed stage agents should run `cli start`, then `cli health`, then publish applicable surfaces when inside a line run. Outside a line run, they should start and verify the Machine without calling `islo surface`.
