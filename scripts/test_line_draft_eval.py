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

    def test_rejects_writes_before_approval(self):
        with self.assertRaisesRegex(AssertionError, "write before approve"):
            evaluate([reply(example(), ["islo factory create unwanted"])])

    def test_rejects_claimed_status(self):
        draft = example()
        draft["needs"] = [{"provider": "linear", "connected": True}]
        with self.assertRaisesRegex(AssertionError, "ids only"):
            evaluate([reply(draft)])

    def test_rejects_duplicate_blocks(self):
        turn = reply(example())
        turn["text"] += "\n\n" + turn["text"]
        with self.assertRaisesRegex(AssertionError, "one block"):
            evaluate([turn])

    def test_rejects_missing_machine_and_bad_revision(self):
        draft = example()
        del draft["runs_on"]["machine"]
        with self.assertRaises(KeyError):
            evaluate([reply(draft)])
        draft = example()
        second = deepcopy(draft)
        second["draft"] = 3
        with self.assertRaisesRegex(AssertionError, "increase by one"):
            evaluate([reply(draft), reply(second)])


if __name__ == "__main__":
    unittest.main()
