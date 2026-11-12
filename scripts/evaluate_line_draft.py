"""Check draft JSON and revision contracts in a recorded, design-only chat trace.

Usage: python3 scripts/evaluate_line_draft.py path/to/trace.json
The trace is an array of {role, text, tool_calls?} turns. This checks the
contract deterministically; the LLM grader still judges blueprint quality and
post-approval tool ordering.
"""

import json
from pathlib import Path
import re
import sys

BLOCK = re.compile(r"^```islo-line-draft\s*\n(.*?)^```\s*$", re.M | re.S)
WRITE = re.compile(r"\b(create|update|deploy|send|post|delete|rm)\b")


def evaluate(turns):
    previous = {}
    approved = False
    count = 0
    for turn in turns:
        if turn["role"] == "user":
            approved = turn["text"].strip().lower() == "approve"
            continue
        if not approved:
            assert not any(WRITE.search(call) for call in turn.get("tool_calls", [])), "write before approve"
            assert "/integrations?connect=" not in turn["text"], "connect card before approve"
        blocks = BLOCK.findall(turn["text"])
        assert len(blocks) <= 1, "exactly one block per draft response"
        for block in blocks:
            draft = json.loads(block)
            assert not re.search(r"\]\(|<a\b|<button\b|https?://", block, re.I), "interactive draft"
            for key in ("factory", "machine"):
                resource = draft["runs_on"][key]
                assert resource["name"] and resource["origin"] in ("new", "existing")
            assert all(isinstance(provider, str) for provider in draft["needs"]), "Needs must contain ids only"
            assert all(step["kind"] in ("script", "decision", "prompt") and step["origin"] in ("new", "existing") for step in draft["steps"])
            assert all(step.get("model") for step in draft["steps"] if step["kind"] == "prompt")
            assert isinstance(draft["assumed"], list) and isinstance(draft["updated"], list)
            assert draft["you_get"]["writes"]
            for group in draft["shared_workspace"]:
                assert len(set(group)) == len(group) >= 2
                assert all(isinstance(n, int) and 1 <= n <= len(draft["steps"]) for n in group)
            old = previous.get(draft["line"])
            if old:
                assert draft["draft"] == old["draft"] + 1, "revision must increase by one"
                assert draft["updated"], "revision needs updated paths"
                for path in draft["updated"]:
                    def value_at(value):
                        for part in path.split("."):
                            value = value[int(part)] if isinstance(value, list) else value.get(part)
                        return value
                    assert value_at(old) != value_at(draft), f"unchanged updated path: {path}"
            else:
                assert draft["draft"] == 1
            previous[draft["line"]] = draft
            count += 1
    assert count > 0, "trace contains no draft"
    return count


if __name__ == "__main__":
    count = evaluate(json.loads(Path(sys.argv[1]).read_text()))
    print(f"Passed {count} draft contract checks. Live agent behavior requires the trace grader.")
