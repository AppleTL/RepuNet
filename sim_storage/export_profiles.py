"""
Export persona learned fields from one or more seed folders into a reusable JSON file.

Example:
    python sim_storage/export_profiles.py ^
        --seeds sim_storage/invest_seed sim_storage/pd_game_seed sim_storage/sign_seed ^
        --out sim_storage/profiles.json
"""

import argparse
import json
from pathlib import Path


SCENARIO_ALIASES = {
    "invest": "investment",
    "investment": "investment",
    "invest_seed": "investment",
    "pd": "pd_game",
    "pd_game": "pd_game",
    "pd_game_seed": "pd_game",
    "sign": "sign_up",
    "sign_up": "sign_up",
    "sign_seed": "sign_up",
}


def normalize_seed_path(seed: str) -> Path:
    path = Path(seed).expanduser()
    if path.name != "step_0":
        path = path / "step_0"
    if not path.exists():
        raise FileNotFoundError(f"Seed path does not exist: {path}")
    return path


def infer_treatment(seed_step: Path) -> str:
    candidates = [seed_step.parent.name.lower(), seed_step.parent.parent.name.lower()]
    for candidate in candidates:
        if candidate in SCENARIO_ALIASES:
            return SCENARIO_ALIASES[candidate]
        for alias, treatment in SCENARIO_ALIASES.items():
            if alias in candidate:
                return treatment
    raise ValueError(f"Could not infer treatment from seed path: {seed_step}")


def export_seed(seed_step: Path) -> dict:
    personas_dir = seed_step / "personas"
    meta_path = seed_step / "reverie" / "meta.json"

    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            persona_names = json.load(f).get("persona_names", [])
    else:
        persona_names = [p.name for p in personas_dir.iterdir() if p.is_dir()]

    learned_map = {}
    for persona_name in persona_names:
        scratch_path = personas_dir / persona_name / "memory" / "scratch.json"
        if not scratch_path.exists():
            continue
        with open(scratch_path, "r", encoding="utf-8") as f:
            scratch = json.load(f)
        learned_map[persona_name] = scratch.get("learned", "")
    return learned_map


def parse_args():
    parser = argparse.ArgumentParser(description="Export learned persona descriptions from seeds to JSON.")
    parser.add_argument("--seeds", nargs="+", required=True, help="Seed directories such as sim_storage/invest_seed or sim_storage/invest_seed/step_0")
    parser.add_argument("--out", required=True, help="Output JSON path")
    return parser.parse_args()


def main():
    args = parse_args()
    result = {}

    for seed in args.seeds:
        seed_step = normalize_seed_path(seed)
        treatment = infer_treatment(seed_step)
        result[treatment] = export_seed(seed_step)

    output_path = Path(args.out).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Exported profiles to: {output_path}")


if __name__ == "__main__":
    main()
