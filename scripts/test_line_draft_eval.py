"""Replay the documented draft and reject representative contract violations."""

from copy import deepcopy
import json
from pathlib import Path
import re
import unittest

from evaluate_line_draft import evaluate

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "plugins/islo/skills/factory-lines/references/chat-embeds.md"


def example():
    return json.loads(re.search(r"```islo-line-draft\n(.*?)\n```", REFERENCE.read_text(), re.S)[1])


def reply(draft, calls=None):
    return {"role": "assistant", "text": "```islo-line-draft\n" + json.dumps(draft) + "\n```", "tool_calls": calls or []}


class LineDraftEvalTests(unittest.TestCase):
    def test_full_revision_replay(self):
        first = example()
        second = deepcopy(first)
        second["draft"] = 2
        second["you_get"]["max_cost_usd"] = 3
        second["runs_on"]["factory"] = {"name": "ticket-polisher", "origin": "new"}
        second["details_expanded"] = True
        second["assumed"].remove("you_get.max_cost_usd")
        second["updated"] = ["you_get.max_cost_usd", "runs_on.factory", "details_expanded"]
        trace = [reply(first, ["islo factory list"]), {"role": "user", "text": "Change the cap to $3, use a new Factory, and show Details."}, reply(second)]
        self.assertEqual(evaluate(trace), 2)

    def test_rejects_the_reviewed_incomplete_payload(self):
        draft = example()
        for field in ("title", "description", "starts_when", "manager", "on_failure", "details", "creates", "reuses"):
            del draft[field]
        with self.assertRaisesRegex(AssertionError, "Invalid draft"):
            evaluate([reply(draft)])

    def test_rejects_missing_required_fields(self):
        fields = [
            "title", "description", "starts_when", "starts_when.text", "starts_when.scope",
            "steps.0.agent", "steps.0.model", "steps.0.purpose", "manager", "on_failure",
            "creates", "reuses", "details", "details.repos", "details.environment",
            "details.gateway", "details.gateway.host", "details.gateway.auth", "details.gateway.origin",
            "details.size", "details.flow", "you_get.result", "you_get.max_cost_usd", "you_get.max_minutes",
        ]
        for field in fields:
            with self.subTest(field=field):
                draft = example()
                value = draft
                parts = field.split(".")
                for part in parts[:-1]:
                    value = value[int(part)] if isinstance(value, list) else value[part]
                del value[parts[-1]]
                with self.assertRaisesRegex(AssertionError, "Invalid draft"):
                    evaluate([reply(draft)])

    def test_rejects_incorrect_types_unknown_fields_and_empty_values(self):
        changes = [
            {"title": 123}, {"title": "   "}, {"draft": True}, {"draft": 1.5},
            {"steps": []}, {"creates": "1 agent"}, {"reuses": [3]}, {"extra": "unknown"},
            {"needs": ["Linear connected"]}, {"assumed": [3]}, {"details_expanded": "yes"},
            {"you_get": {**example()["you_get"], "max_cost_usd": -1}},
            {"you_get": {**example()["you_get"], "max_minutes": 0}},
            {"details": {**example()["details"], "repos": [False]}},
            {"steps": [{**example()["steps"][0], "model": 7}]},
            {"shared_workspace": [[True, 1]]},
        ]
        for changeset in changes:
            with self.subTest(changeset=changeset):
                with self.assertRaisesRegex(AssertionError, "Invalid draft"):
                    evaluate([reply({**example(), **changeset})])

    def test_accepts_all_step_kinds_and_optional_details(self):
        draft = example()
        draft["steps"] = [
            {"agent": kind, "kind": kind, "origin": "existing", "purpose": "Does the work"}
            for kind in ("script", "decision")
        ]
        draft["shared_workspace"] = [[1, 2]]
        draft["details"].pop("retained_resources", None)
        draft["details"]["gateway"].pop("name", None)
        draft["details"]["model"] = "No model for these stages"
        self.assertEqual(evaluate([reply(draft)]), 1)

    def test_rejects_invalid_workspace_groups(self):
        for group in ([1], [1, 1], [1, 2]):
            with self.subTest(group=group):
                with self.assertRaisesRegex(AssertionError, "Invalid draft"):
                    evaluate([reply({**example(), "shared_workspace": [group]})])

    def test_rejects_non_json_numbers(self):
        for value in (float("nan"), float("inf")):
            draft = example()
            draft["you_get"]["max_cost_usd"] = value
            with self.assertRaisesRegex(AssertionError, "Invalid draft JSON"):
                evaluate([reply(draft)])

    def test_rejects_json_number_overflow_like_the_renderer(self):
        turn = reply(example())
        turn["text"] = turn["text"].replace('"max_cost_usd": 2', '"max_cost_usd": 1e999')
        with self.assertRaisesRegex(AssertionError, "Invalid draft JSON"):
            evaluate([turn])

    def test_rejects_writes_before_approval(self):
        with self.assertRaisesRegex(AssertionError, "write before approve"):
            evaluate([reply(example(), ["islo factory create unwanted"])])

    def test_rejects_claimed_status(self):
        draft = example()
        draft["needs"] = [{"provider": "linear", "connected": True}]
        with self.assertRaisesRegex(AssertionError, "Invalid draft"):
            evaluate([reply(draft)])

    def test_rejects_duplicate_blocks(self):
        turn = reply(example())
        turn["text"] += "\n\n" + turn["text"]
        with self.assertRaisesRegex(AssertionError, "one block"):
            evaluate([turn])

    def test_rejects_missing_machine_and_bad_revision(self):
        draft = example()
        del draft["runs_on"]["machine"]
        with self.assertRaisesRegex(AssertionError, "Invalid draft"):
            evaluate([reply(draft)])
        draft = example()
        second = deepcopy(draft)
        second["draft"] = 3
        with self.assertRaisesRegex(AssertionError, "increase by one"):
            evaluate([reply(draft), reply(second)])


if __name__ == "__main__":
    unittest.main()
