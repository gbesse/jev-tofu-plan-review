"""Review OpenTofu plan intent using only a value-free plan summary."""

import json

from review_core import InputError, run_cli

ALLOWED_ACTIONS = {"create", "update", "delete", "no-op", "read"}


def adapt(payload):
    if not isinstance(payload, dict):
        raise InputError("invalid_case")
    intent, plan = payload.get("intent"), payload.get("plan")
    if not isinstance(intent, str) or not 1 <= len(intent.strip()) <= 2000:
        raise InputError("invalid_intent")
    if not isinstance(plan, dict):
        raise InputError("invalid_plan")
    version = plan.get("format_version")
    if not isinstance(version, str) or not version.startswith("1."):
        raise InputError("unsupported_plan_format")
    resources = plan.get("resource_changes")
    if not isinstance(resources, list) or not 1 <= len(resources) <= 50:
        raise InputError("invalid_resource_count")
    changes, evidence, flags = [], [], []
    for index, resource in enumerate(resources):
        if not isinstance(resource, dict) or not isinstance(
            resource.get("change"), dict
        ):
            raise InputError("invalid_resource")
        address, kind = resource.get("address"), resource.get("type")
        actions = resource["change"].get("actions")
        if (
            not isinstance(address, str)
            or not 1 <= len(address) <= 250
            or not isinstance(kind, str)
            or not 1 <= len(kind) <= 120
            or not isinstance(actions, list)
            or not 1 <= len(actions) <= 2
            or any(
                not isinstance(action, str) or action not in ALLOWED_ACTIONS
                for action in actions
            )
        ):
            raise InputError("invalid_resource")
        if actions == ["no-op"]:
            continue
        before, after = (
            resource["change"].get("before"),
            resource["change"].get("after"),
        )
        if isinstance(before, dict) and isinstance(after, dict):
            keys = sorted(
                key
                for key in set(before) | set(after)
                if before.get(key) != after.get(key)
            )
        else:
            visible = (
                before
                if isinstance(before, dict)
                else after
                if isinstance(after, dict)
                else {}
            )
            keys = sorted(visible)
        keys = [key for key in keys if isinstance(key, str) and len(key) <= 100]
        sensitive = bool(resource["change"].get("before_sensitive")) or bool(
            resource["change"].get("after_sensitive")
        )
        changes.append(
            {
                "address": address,
                "type": kind,
                "actions": actions,
                "attribute_names": keys[:30],
                "sensitive_values_present": sensitive,
            }
        )
        evidence.append(f"plan.resource_changes[{index}]")
        if "delete" in actions:
            flags.append("destructive_change")
        if any(
            word in kind.lower()
            for word in ("iam", "policy", "security_group", "firewall")
        ):
            flags.append("access_control_change")
    if not changes:
        raise InputError("no_changes")
    text = (
        "Declared intent: "
        + intent.strip()
        + "\nPlanned resource changes (values excluded): "
        + json.dumps(changes, sort_keys=True)
    )
    return {
        "subject": "OpenTofu plan",
        "text": text,
        "evidence": evidence,
        "flags": flags,
    }


if __name__ == "__main__":
    run_cli(adapt, "mismatch")
