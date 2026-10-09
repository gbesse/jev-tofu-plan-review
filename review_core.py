"""Bounded Jev review: deterministic extraction, advisory decision, evidence."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

from jev import evaluate, normalize


class InputError(ValueError):
    pass


def review(payload, policy, judge, adapter):
    case = adapter(payload)
    if not isinstance(case, dict):
        raise InputError("invalid_case")
    text = case.get("text")
    subject = case.get("subject")
    evidence = case.get("evidence")
    flags = case.get("flags")
    if (
        not isinstance(text, str)
        or not 1 <= len(text) <= 16000
        or not isinstance(subject, str)
        or not 1 <= len(subject) <= 700
        or not isinstance(evidence, list)
        or len(evidence) > 200
        or not all(isinstance(item, str) and 1 <= len(item) <= 300 for item in evidence)
        or not isinstance(flags, list)
        or not all(isinstance(item, str) and item for item in flags)
    ):
        raise InputError("invalid_case")
    decision = judge(text)
    if (
        not isinstance(decision, dict)
        or decision.get("policy_version") != policy["version"]
        or decision.get("choice") not in policy["criteria"]
        or decision.get("outcome") not in {*policy["criteria"], "review"}
    ):
        raise InputError("invalid_decision")
    return {
        "subject": subject,
        "input_hash": hashlib.sha256(text.encode()).hexdigest(),
        "choice": decision["choice"],
        "probability": decision["probability"],
        "outcome": "review" if flags else decision["outcome"],
        "policy_version": policy["version"],
        "flags": sorted(set(flags)),
        "evidence": evidence,
        "automatic_action": False,
    }


def run_cli(adapter, demo_choice):
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true")
    mode.add_argument("--input", type=Path)
    args = parser.parse_args()
    try:
        with open("examples/policy.json", encoding="utf-8") as source:
            policy = json.load(source)
        if args.demo:
            with open("examples/case.json", encoding="utf-8") as source:
                payload = json.load(source)
            judge = lambda _: normalize(demo_choice, 0.97, policy)
        else:
            if str(args.input) == "-":
                raw = sys.stdin.buffer.read(10_000_001)
                if len(raw) > 10_000_000:
                    raise InputError("input_too_large")
                payload = json.loads(raw)
            else:
                if args.input.stat().st_size > 10_000_000:
                    raise InputError("input_too_large")
                with args.input.open(encoding="utf-8") as source:
                    payload = json.load(source)
            key = os.environ.get("TYPESAFE_API_KEY")
            if not key:
                raise InputError("missing_key")
            judge = lambda text: evaluate(text, policy, key)
        result = review(payload, policy, judge, adapter)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        code = str(exc) if isinstance(exc, InputError) else "invalid_input"
        parser.exit(2, code + "\n")
    except Exception:
        parser.exit(3, "decision_unavailable\n")
    result["demo"] = args.demo
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
