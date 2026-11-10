"""Regression tests for the real Hermes plugin handler dispatch contract."""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "shipwrit_plugin",
    ROOT / "__init__.py",
    submodule_search_locations=[str(ROOT)],
)
PLUGIN = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PLUGIN
SPEC.loader.exec_module(PLUGIN)


class PluginDispatchTests(unittest.TestCase):
    @patch.object(PLUGIN, "mark_receipt")
    @patch.object(PLUGIN, "run_contract")
    def test_dispatch_dict_and_task_context_are_accepted(self, run_contract, mark_receipt):
        receipt = {"verdict": "PASS", "sha256": "abc123"}
        run_contract.return_value = receipt
        args = {
            "base_url": "https://staging.example.com",
            "contract_path": "staging-contract.json",
            "allow_writes": False,
        }

        result = PLUGIN.handle_check(
            args,
            task_id="hermes-task-123",
            session_id="hermes-session-456",
            tool_call_id="call-789",
        )

        self.assertIsInstance(result, str)
        self.assertEqual(json.loads(result), receipt)
        run_contract.assert_called_once_with(
            "https://staging.example.com",
            contract_path="staging-contract.json",
            allow_writes=False,
        )
        mark_receipt.assert_called_once_with(
            receipt, "https://staging.example.com"
        )

    @patch.object(PLUGIN, "mark_receipt")
    @patch.object(PLUGIN, "run_contract")
    def test_defaults_are_preserved(self, run_contract, mark_receipt):
        receipt = {"verdict": "BLOCK", "sha256": "def456"}
        run_contract.return_value = receipt

        result = PLUGIN.handle_check(
            {"base_url": "https://staging.example.com"},
            task_id="hermes-task-123",
        )

        self.assertEqual(json.loads(result), receipt)
        run_contract.assert_called_once_with(
            "https://staging.example.com",
            contract_path="release-witness.json",
            allow_writes=False,
        )
        mark_receipt.assert_called_once_with(
            receipt, "https://staging.example.com"
        )

    @patch.object(PLUGIN, "run_contract")
    def test_missing_base_url_is_rejected(self, run_contract):
        with self.assertRaisesRegex(ValueError, "base_url is required"):
            PLUGIN.handle_check({"contract_path": "contract.json"})
        run_contract.assert_not_called()

    @patch.object(PLUGIN, "run_contract")
    def test_non_boolean_write_opt_in_is_rejected(self, run_contract):
        with self.assertRaisesRegex(ValueError, "allow_writes must be a boolean"):
            PLUGIN.handle_check(
                {"base_url": "https://staging.example.com", "allow_writes": "true"}
            )
        run_contract.assert_not_called()


if __name__ == "__main__":
    unittest.main()
