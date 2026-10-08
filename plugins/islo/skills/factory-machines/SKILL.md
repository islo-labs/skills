---
name: factory-machines
description: Build, inspect, verify, and prepare Islo Factory Machines for snapshots; publish useful live run surfaces from Machine stage sandboxes.
---

# Factory Machines

Use this skill when working inside a Factory Machine build or a stage backed by a Machine snapshot, or when acting as the Line Manager for a Machine line. The Machine CLI and discovered stack determine what can run. Read [Machine lifecycle](references/lifecycle.md) for build, inspection, verification, and snapshot preparation. Read [Live run surfaces](references/surfaces.md) when a line run should show useful interfaces.

The Line Manager uses the Surface guidance to direct a stage agent to publish or repair an interface. Manager agents do not invoke `islo surface` themselves; the stage agent owns the stage sandbox and its Surface environment.

For creating, updating, or deleting a Machine resource, use the `factory-lines` skill's Machine commands.
