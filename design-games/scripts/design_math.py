#!/usr/bin/env python3
"""Deterministic, dependency-free helpers for game numerical design."""

import argparse
import json
import math
from typing import Any, Dict, List, Optional


def _probability(value: float, name: str) -> float:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return value


def _nonnegative(value: float, name: str) -> float:
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def expected_dps(
    damage: float,
    interval: float,
    accuracy: float = 1.0,
    crit_chance: float = 0.0,
    crit_multiplier: float = 2.0,
) -> Dict[str, float]:
    """Expected DPS; misses deal zero and crits are rolled only on hits."""
    _nonnegative(damage, "damage")
    if interval <= 0:
        raise ValueError("interval must be greater than zero")
    _probability(accuracy, "accuracy")
    _probability(crit_chance, "crit_chance")
    if crit_multiplier < 1:
        raise ValueError("crit_multiplier must be at least 1")
    expected_on_hit = damage * (1 + crit_chance * (crit_multiplier - 1))
    expected_per_attack = accuracy * expected_on_hit
    return {
        "expected_damage_on_hit": expected_on_hit,
        "expected_damage_per_attack": expected_per_attack,
        "expected_dps": expected_per_attack / interval,
        "assumption": "independent attacks; misses deal zero; no reload, mitigation, overkill or downtime",
    }


def effective_hp(hp: float, armor: float, armor_k: float) -> Dict[str, float]:
    """EHP for multiplier K/(K+armor), with non-negative armor."""
    _nonnegative(hp, "hp")
    _nonnegative(armor, "armor")
    if armor_k <= 0:
        raise ValueError("armor_k must be greater than zero")
    damage_multiplier = armor_k / (armor_k + armor)
    return {
        "damage_multiplier": damage_multiplier,
        "mitigation": 1.0 - damage_multiplier,
        "effective_hp": hp / damage_multiplier,
        "assumption": "non-negative armor and damage multiplier K/(K+armor)",
    }


def time_to_kill(hp: float, dps: float) -> Dict[str, Any]:
    """Continuous approximation; not a discrete or stochastic TTK simulation."""
    _nonnegative(hp, "hp")
    if dps <= 0:
        raise ValueError("dps must be greater than zero")
    return {
        "time_to_kill_seconds": hp / dps,
        "assumption": "continuous constant DPS; excludes first-hit timing, overkill, phases and downtime",
    }


def drop_probability(p: float, attempts: int, confidence: float = 0.95) -> Dict[str, Any]:
    """Independent constant-probability drops."""
    _probability(p, "p")
    _probability(confidence, "confidence")
    if attempts < 0:
        raise ValueError("attempts must be non-negative")
    at_least_once = 1.0 - (1.0 - p) ** attempts
    expected_attempts: Optional[float] = 1.0 / p if p > 0 else None
    attempts_for_confidence: Optional[int]
    if confidence == 0:
        attempts_for_confidence = 0
    elif p == 1:
        attempts_for_confidence = 1
    elif p == 0:
        attempts_for_confidence = None
    else:
        attempts_for_confidence = math.ceil(math.log1p(-confidence) / math.log1p(-p))
    return {
        "at_least_once_probability": at_least_once,
        "no_drop_probability": (1.0 - p) ** attempts,
        "expected_attempts": expected_attempts,
        "attempts_for_confidence": attempts_for_confidence,
        "confidence": confidence,
        "assumption": "independent attempts with constant probability",
    }


def pity_distribution(
    base_p: float,
    hard_pity: int,
    soft_start: int,
    soft_step: float,
) -> Dict[str, Any]:
    """Linear soft pity; soft_start is the first increased pull."""
    _probability(base_p, "base_p")
    _probability(soft_step, "soft_step")
    if hard_pity < 1:
        raise ValueError("hard_pity must be at least 1")
    if not 1 <= soft_start <= hard_pity:
        raise ValueError("soft_start must be between 1 and hard_pity")

    probabilities: List[float] = []
    for pull in range(1, hard_pity + 1):
        if pull == hard_pity:
            probability = 1.0
        else:
            increased_pulls = max(0, pull - soft_start + 1)
            probability = min(1.0, base_p + increased_pulls * soft_step)
        probabilities.append(probability)

    distribution: List[float] = []
    survival = 1.0
    expected = 0.0
    for pull, probability in enumerate(probabilities, start=1):
        success_mass = survival * probability
        distribution.append(success_mass)
        expected += pull * success_mass
        survival *= 1.0 - probability

    def quantile(q: float) -> int:
        cumulative = 0.0
        for pull, mass in enumerate(distribution, start=1):
            cumulative += mass
            if cumulative + 1e-15 >= q:
                return pull
        return hard_pity

    return {
        "expected_pulls": expected,
        "median_pulls": quantile(0.5),
        "p90_pulls": quantile(0.9),
        "p99_pulls": quantile(0.99),
        "hard_pity_probability": distribution[-1],
        "probabilities_by_pull": probabilities,
        "success_mass_by_pull": distribution,
        "assumption": "soft_start is the first increased pull; hard pity guarantees success; success resets before any next cycle",
    }


def damping(half_life: float, dt: float) -> Dict[str, float]:
    """Frame-rate-independent first-order response from a half-life."""
    if half_life <= 0:
        raise ValueError("half_life must be greater than zero")
    _nonnegative(dt, "dt")
    retention = 0.5 ** (dt / half_life)
    return {
        "retention": retention,
        "response": 1.0 - retention,
        "usage": "new_value = target + (old_value - target) * retention",
        "assumption": "constant target during dt",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    command = subparsers.add_parser("expected-dps")
    command.add_argument("--damage", type=float, required=True)
    command.add_argument("--interval", type=float, required=True)
    command.add_argument("--accuracy", type=float, default=1.0)
    command.add_argument("--crit-chance", type=float, default=0.0)
    command.add_argument("--crit-multiplier", type=float, default=2.0)

    command = subparsers.add_parser("effective-hp")
    command.add_argument("--hp", type=float, required=True)
    command.add_argument("--armor", type=float, required=True)
    command.add_argument("--armor-k", type=float, required=True)

    command = subparsers.add_parser("time-to-kill")
    command.add_argument("--hp", type=float, required=True)
    command.add_argument("--dps", type=float, required=True)

    command = subparsers.add_parser("drop")
    command.add_argument("--p", type=float, required=True)
    command.add_argument("--attempts", type=int, required=True)
    command.add_argument("--confidence", type=float, default=0.95)

    command = subparsers.add_parser("pity")
    command.add_argument("--base-p", type=float, required=True)
    command.add_argument("--hard-pity", type=int, required=True)
    command.add_argument("--soft-start", type=int, required=True)
    command.add_argument("--soft-step", type=float, required=True)

    command = subparsers.add_parser("damping")
    command.add_argument("--half-life", type=float, required=True)
    command.add_argument("--dt", type=float, required=True)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "expected-dps":
            result = expected_dps(args.damage, args.interval, args.accuracy, args.crit_chance, args.crit_multiplier)
        elif args.command == "effective-hp":
            result = effective_hp(args.hp, args.armor, args.armor_k)
        elif args.command == "time-to-kill":
            result = time_to_kill(args.hp, args.dps)
        elif args.command == "drop":
            result = drop_probability(args.p, args.attempts, args.confidence)
        elif args.command == "pity":
            result = pity_distribution(args.base_p, args.hard_pity, args.soft_start, args.soft_step)
        else:
            result = damping(args.half_life, args.dt)
    except ValueError as error:
        parser.error(str(error))
        return
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
