"""Safety and methodology gates for the PROPOSED Emergence Lab Study 09.

This does not simulate cognition, provide statistical power or preregister a study.
It ensures a draft is not mistaken for an authorized confirmatory run.
Python standard library only.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
from typing import Iterable

REQUIRED_BASELINES = frozenset({
    "random_policy", "reactive_policy", "one_step_comparator",
    "bayesian_system_identifier", "nearest_neighbor_memory",
    "history_feedforward", "fixed_recurrent", "topology_evolving",
    "random_fitness", "no_inheritance",
})
REQUIRED_ABLATIONS = frozenset({
    "motor_copy_scramble_preserve_rng", "latent_state_lesion_matched_compute",
    "environment_only_disturbance", "sensor_bias_intervention",
    "action_history_without_recurrence", "indistinguishable_cause_abstention",
})


class ProtocolError(ValueError):
    pass


def check_draft(plan: dict) -> list[str]:
    """Return structural problems in a *draft*, not missing registration gates."""
    errors = []
    if plan.get("status") != "DRAFT_NOT_PREREGISTERED":
        errors.append("Study 09 must remain explicitly DRAFT before external registration.")
    if plan.get("confirmatory_data_collected") is not False:
        errors.append("Confirmatory data must be marked uncollected.")
    if plan.get("claims_consciousness") is not False:
        errors.append("No phenomenological consciousness claim or measurement is defined.")
    if plan.get("independent_unit") != "independent_evolutionary_population":
        errors.append("Analysis unit must be independent evolving populations, not episodes.")
    envs = plan.get("environments", [])
    if len(envs) != 2 or len(set(x.get("id") for x in envs)) != 2:
        errors.append("Specify two different prospective environment families.")
    missing = REQUIRED_BASELINES - set(plan.get("baselines", []))
    if missing:
        errors.append("Missing baseline classes: " + ", ".join(sorted(missing)))
    missing = REQUIRED_ABLATIONS - set(plan.get("ablations", []))
    if missing:
        errors.append("Missing causal ablation classes: " + ", ".join(sorted(missing)))
    if plan.get("confirmatory_seed_list") not in (None, []):
        errors.append("Do not prepare confirmatory seeds in a draft.")
    return errors


def confirmatory_blockers(plan: dict) -> list[str]:
    """Fail closed. These checks are necessary but *not sufficient* for science."""
    issues = check_draft(plan)
    for label, key in [
        ("independent methods reviewer signature", "reviewer_signoff_record"),
        ("external immutable preregistration URL", "preregistration_url"),
        ("development-only sample-size justification", "sample_size_justification"),
        ("fully frozen primary estimand and inferential method", "frozen_analysis_plan_hash"),
        ("frozen source/environment commit", "frozen_code_commit"),
        ("budget-matching audit", "compute_and_sensor_budget_audit"),
        ("separate independent environment implementation", "independent_environment_review"),
        ("recorded prior-art and novelty assessment", "prior_art_review_signoff"),
    ]:
        if not plan.get(key):
            issues.append("Missing " + label + ".")
    if not any(e.get("implemented_by_independent_reviewer") is True for e in plan.get("environments", [])):
        issues.append("No environment has been independently authored and audited.")
    if plan.get("confirmatory_data_collected") is not False:
        issues.append("Confirmatory results already accessed: registration cannot be prospective.")
    return issues


def require_confirmatory_ready(plan: dict) -> None:
    blockers = confirmatory_blockers(plan)
    if blockers:
        raise ProtocolError("CONFIRMATORY RUN BLOCKED:\n" + "\n".join(" - " + s for s in blockers))
    # Even complete paperwork needs an affirmative human permission before opening seeds.
    raise ProtocolError("CONFIRMATORY RUN BLOCKED: explicit study-owner approval required outside this tool.")


def validate_paired_population_results(rows: Iterable[dict]) -> list[float]:
    """One difference per independently evolved population. Not per episode.

    Required row fields: population_id, candidate, comparator. Also forbids
    hidden oracle labels being surfaced through the result interface.
    """
    rows = list(rows)
    if len(rows) < 2:
        raise ProtocolError("At least two independent population clusters required.")
    ids = [str(x.get("population_id", "")) for x in rows]
    if any(not x or x == "None" for x in ids):
        raise ProtocolError("Missing independent population ID")
    duplicates = sorted(k for k, c in Counter(ids).items() if c > 1)
    if duplicates:
        raise ProtocolError("Pseudoreplication: duplicate population IDs: " + str(duplicates))
    differences = []
    for r in rows:
        if any(x in r for x in ("hidden_motor_mapping", "true_cause", "test_oracle_state")):
            raise ProtocolError("Privileged simulator truth leaked into model score rows.")
        try:
            candidate, baseline = float(r["candidate"]), float(r["comparator"])
        except (KeyError, ValueError, TypeError) as exc:
            raise ProtocolError("Malformed paired score") from exc
        if not math.isfinite(candidate) or not math.isfinite(baseline):
            raise ProtocolError("Nonfinite population-level score")
        differences.append(candidate-baseline)
    return differences


def validate_agent_observation(obs: dict) -> None:
    """Conservative boundary check for an agent-facing observation packet.

    Agent receives raw anonymous sensor array plus its own last action.
    Do not expose cause labels, world seeds, precise physics, or oracle map.
    Additional observation semantics require external review before changing.
    """
    if set(obs) != {"sensor_values", "last_action"}:
        raise ProtocolError("Agent API must contain ONLY sensor_values and last_action.")
    data = obs["sensor_values"]
    if not isinstance(data, (list, tuple)) or not data:
        raise ProtocolError("Sensor array is empty or invalid")
    if any(isinstance(v, bool) or not isinstance(v, (int,float)) or not math.isfinite(v) for v in data):
        raise ProtocolError("Sensor array must contain finite numeric scalars")
    last = obs["last_action"]
    if last is not None and (not isinstance(last, int) or isinstance(last, bool) or last < 0):
        raise ProtocolError("Action must be a nonnegative integer or None")


def main() -> int:
    parser = argparse.ArgumentParser(description="Study 09 research governance preflight")
    parser.add_argument("--plan", default=str(Path(__file__).with_name("study_plan.json")))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--draft-check", action="store_true")
    group.add_argument("--confirmatory-check", action="store_true")
    args = parser.parse_args()
    plan = json.loads(Path(args.plan).read_text())
    if args.draft_check:
        problems = check_draft(plan)
        if problems:
            print("DRAFT INVALID:\n"+"\n".join(problems)); return 1
        print("DRAFT STRUCTURE VALID. Confirmatory study NOT authorized or executed.")
        return 0
    blockers = confirmatory_blockers(plan)
    for b in blockers: print("BLOCKER:", b)
    if not blockers: print("BLOCKER: human owner authorization is still required")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
