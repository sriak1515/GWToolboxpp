# SpeedrunScriptingTools (SST) - Documentation Index

This is the LLM-consumable reference for the **SpeedrunScriptingTools** plugin and its underlying **Scripting** library in GWToolbox++.

## Architecture

```
SpeedrunScriptingTools (plugin DLL)
├── SpeedrunScriptingTools.h/.cpp  — Plugin entry, Script/Group structs, execution engine
└── Scripting (INTERFACE library, linked into all plugins)
    ├── Action system     — 48 action types (what scripts do)
    ├── Condition system  — 63 condition types (when scripts run)
    ├── Characteristic system — 22 types (agent filtering for ChangeTarget)
    ├── ScriptVariables   — Persistent key-value store
    ├── InstanceInfo      — Runtime game state (doors, targets, names)
    └── QuestInfo         — Quest/objective state tracking
```

## Files

| File | Purpose |
|------|---------|
| [01-overview.md](01-overview.md) | Plugin concept, Script/Group structs, execution model |
| [02-triggers.md](02-triggers.md) | Trigger types and their data |
| [03-actions.md](03-actions.md) | All 48 action types with parameters |
| [04-conditions.md](04-conditions.md) | All 63 condition types with parameters |
| [05-characteristics.md](05-characteristics.md) | Agent characteristic filters for ChangeTarget |
| [06-variables.md](06-variables.md) | Script variables and persistence |
| [07-enums.md](07-enums.md) | All shared enumerations |
| [08-serialization.md](08-serialization.md) | Clipboard import/export format |

## Scripts

| Path | Purpose |
|------|---------|
| [../../scripts/sst/](../../scripts/sst/) | Example SST scripts (.sst files) |
| [../../scripts/sst/dark-aura-maintainer.sst](../../scripts/sst/dark-aura-maintainer.sst) | Maintain Dark Aura on party |
| [../../scripts/sst/dervish-attack-optimizer.sst](../../scripts/sst/dervish-attack-optimizer.sst) | Single-hotkey Dervish rotation (flash enchant + strip) |
| [../../scripts/sst/drunken-master-maintainer.sst](../../scripts/sst/drunken-master-maintainer.sst) | Maintain Drunken Master buff |
| [../../scripts/sst/flag-wide-formation.sst](../../scripts/sst/flag-wide-formation.sst) | Wide 0-5-2 hero formation (AoE-safe) |
| [../../scripts/sst/flag-narrow-formation.sst](../../scripts/sst/flag-narrow-formation.sst) | Narrow 0-5-2 hero formation (dungeons) |
| [../../scripts/sst/soh-maintainer.sst](../../scripts/sst/soh-maintainer.sst) | Maintain Strength of Honor |
| [../../scripts/sst/soul-taker-self-buff-maintainer.sst](../../scripts/sst/soul-taker-self-buff-maintainer.sst) | Maintain Soul Taker self buff |
| [../../scripts/sst/st-combat-prep.sst](../../scripts/sst/st-combat-prep.sst) | Soul Twisting combat preparation |
