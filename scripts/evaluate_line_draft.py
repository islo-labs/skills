"""Check draft JSON and revision contracts in a recorded, design-only chat trace.

Usage: python3 scripts/evaluate_line_draft.py path/to/trace.json
The trace is an array of {role, text, tool_calls?} turns. This checks the
contract deterministically; the LLM grader still judges blueprint quality and
post-approval tool ordering.
Install dependencies with python3 -m pip install -r scripts/requirements-line-draft-eval.txt.
"""

import json
import math
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator, ValidationError

BLOCK = re.compile(r"^```islo-line-draft\s*\n(.*?)^```\s*$", re.M | re.S)
WRITE = re.compile(r"\b(create|update|deploy|send|post|delete|rm)\b")


SCHEMA = Path(__file__).resolve().parents[1] / "plugins/islo/evals/line-draft-card/schema.json"
VALIDATOR = Draft202012Validator(json.loads(SCHEMA.read_text()))
Draft202012Validator.check_schema(VALIDATOR.schema)


def validate_draft(draft):
    """Validate the exported zod shape, then its workspace refinement."""
    try:
        VALIDATOR.validate(draft)
    except ValidationError as error:
        path = ".".join(map(str, error.absolute_path)) or "root"
        raise AssertionError(f"Invalid draft at {path}: {error.message}") from error
    for group in draft["shared_workspace"]:
        assert len(set(group)) == len(group), "Invalid draft: workspace steps must be distinct"
        assert all(n <= len(draft["steps"]) for n in group), "Invalid draft: workspace step out of range"


def parse_number(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"Non-finite number: {value}")
    return number


def reject_nonfinite(value):
    raise ValueError(f"Non-JSON number: {value}")


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
            try:
                draft = json.loads(block, parse_constant=reject_nonfinite, parse_int=parse_number, parse_float=parse_number)
            except ValueError as error:
                raise AssertionError(f"Invalid draft JSON: {error}") from error
            validate_draft(draft)
            assert not re.search(r"\]\(|<a\b|<button\b|https?://", block, re.I), "interactive draft"
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
