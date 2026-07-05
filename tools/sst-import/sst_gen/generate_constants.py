#!/usr/bin/env python3
"""Parse C++ enum headers and generate Python constant dicts.

Reads Skills.h and Constants.h from GWCA and writes constants_generated.py
with SKILL_IDS and HERO_IDS mappings.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Default paths relative to this script's location
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
SKILLS_H = REPO_ROOT / "Dependencies" / "GWCA" / "include" / "GWCA" / "Constants" / "Skills.h"
CONSTANTS_H = REPO_ROOT / "Dependencies" / "GWCA" / "include" / "GWCA" / "Constants" / "Constants.h"
OUTPUT = SCRIPT_DIR / "constants_generated.py"


def parse_enum(text: str, enum_name: str) -> dict[str, int]:
    """Parse a C++ enum block and return {name: value} mapping.

    Handles auto-increment, explicit = N and = 0xN assignments.
    """
    # Find the enum block
    pattern = rf'enum\s+(?:class\s+)?{enum_name}\s*:\s*\w+\s*\{{(.*?)\}};'
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        raise ValueError(f"Could not find enum {enum_name}")

    block = m.group(1)
    result: dict[str, int] = {}
    current_value = 0

    # Normalize: collapse newlines into a flat comma-separated stream,
    # then split on commas.  This handles multi-entry lines like
    # "NoHero, Norgu, Goren, Tahlkora," correctly.
    flat = re.sub(r'//.*', '', block)       # strip comments
    flat = re.sub(r'\s+', ' ', flat)         # collapse whitespace
    for entry in flat.split(','):
        entry = entry.strip()
        if not entry:
            continue

        # Check for explicit value assignment: Name = value
        assign_match = re.match(r'(\w+)\s*=\s*(0[xX][0-9a-fA-F]+|\d+)', entry)
        if assign_match:
            name = assign_match.group(1)
            val_str = assign_match.group(2)
            current_value = int(val_str, 0)
            result[name] = current_value
            current_value += 1
            continue

        # Simple name (auto-increment)
        name_match = re.match(r'(\w+)', entry)
        if name_match:
            name = name_match.group(1)
            result[name] = current_value
            current_value += 1

    return result


def generate_python(skill_ids: dict[str, int], hero_ids: dict[str, int]) -> str:
    lines = [
        '"""Auto-generated from C++ enum headers. Do not edit manually.',
        'Run: python -m sst_gen.generate_constants',
        '"""',
        '',
        'SKILL_IDS = {',
    ]
    for name, value in skill_ids.items():
        lines.append(f'    "{name}": {value},')
    lines.append('}')
    lines.append('')
    lines.append('HERO_IDS = {')
    for name, value in hero_ids.items():
        lines.append(f'    "{name}": {value},')
    lines.append('}')
    lines.append('')
    return '\n'.join(lines)


def main() -> None:
    for path in [SKILLS_H, CONSTANTS_H]:
        if not path.exists():
            print(f"Error: {path} not found", file=sys.stderr)
            sys.exit(1)

    skills_text = SKILLS_H.read_text(encoding="utf-8", errors="replace")
    constants_text = CONSTANTS_H.read_text(encoding="utf-8", errors="replace")

    skill_ids = parse_enum(skills_text, "SkillID")
    hero_ids = parse_enum(constants_text, "HeroID")

    # Remove Count sentinel — not a real skill/hero
    skill_ids.pop("Count", None)
    hero_ids.pop("Count", None)

    output = generate_python(skill_ids, hero_ids)
    OUTPUT.write_text(output, encoding="utf-8")

    print(f"Wrote {len(skill_ids)} skills and {len(hero_ids)} heroes to {OUTPUT}")
    print(f"Skill range: 0..{max(skill_ids.values())}")
    print(f"Hero range: 0..{max(hero_ids.values())}")


if __name__ == "__main__":
    main()
