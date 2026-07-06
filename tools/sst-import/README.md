# SST Script Generator

Converts human-readable `.sst` script files into clipboard-importable strings for the SpeedrunScriptingTools (SST) plugin in GWToolbox++.

## Usage

```bash
# Print the import string to stdout
python3 tools/sst-import/sst_script_gen.py scripts/sst/dark-aura-maintainer.sst --dry-run

# Copy the import string to clipboard (uses termux-clipboard-set)
python3 tools/sst-import/sst_script_gen.py scripts/sst/dark-aura-maintainer.sst
```

## .sst File Format

```
// Comments start with //

script "Script Name" {
    trigger: None
    canLaunchInParallel: true

    when {
        // Conditions — all must pass for the script to run
        FoeCount >= 1
        not PlayerHasBuff(Dark_Aura)
        HeroHasSkill(hero: NoHero, skill: Dark_Aura, requirement: ReadyToUse)
        Throttle(5000ms)
    }

    then {
        // Actions — executed in order
        EnterCriticalSection
        ChangeTarget(sorting: AgentId, filter: Allegiance(Self))
        UseHeroSkill(hero: NoHero, skill: Dark_Aura)
        LeaveCriticalSection
    }
}
```

### Supported Conditions

| Condition | Parameters |
|-----------|-----------|
| `FoeCount` | `>= N`, `<= N`, `== N`, etc. |
| `PlayerHasBuff` | `(SkillName)` or `(id: SkillName, hasMax: true, maxDuration: N)` |
| `PlayerHasSkill` | `(skill: SkillName, requirement: OnBar\|OffCooldown\|ReadyToUse)` |
| `PlayerHasSkillBySlot` | `(slot: N, requirement: OnBar\|OffCooldown\|ReadyToUse)` |
| `HeroHasSkill` | `(hero: HeroID, skill: SkillName, requirement: OnBar\|OffCooldown\|ReadyToUse)` |
| `HeroHasEnergy` | `(hero: HeroID, energy: N, comp: >=\|<=\|==\|!=\|>\|<)` |
| `HeroHasBuff` | `(hero: HeroID, skill: SkillName)` |
| `PlayerHasEnergy` | `(energy: N, comp: >=\|<=\|==\|!=\|>\|<)` |
| `PlayerAdrenaline` | `(skill: SkillName, adrenaline: N, comp: >=\|<=\|==\|!=\|>\|<)` |
| `RemainingCooldown` | `(skill: SkillName)` |
| `OnlyTriggerOncePerInstance` | (no parameters) |
| `PlayerIsDrunk` | `(minLevel: N)` |
| `HasCalledTarget` | (no parameters) |
| `HasTerrainClearance` | `(degree: N, distance: N)` |
| `ItemInInventoryList` | `(ids: N, M, ...)` |
| `ScriptVariableIsSet` | `(name: X)` |
| `Throttle` | `(Nms)` |
| `IsInCombat` | `(range: N)` — true if any hostile agent within range (default 1012 gwinches) |
| `True_` | (no parameters) — always true |
| `False_` | (no parameters) — always false |
| `not` | Wraps any condition: `not PlayerHasBuff(...)` |

### Supported Actions

| Action | Parameters |
|--------|-----------|
| `EnterCriticalSection` | none |
| `LeaveCriticalSection` | none |
| `ChangeTarget` | `(sorting: Sorting, filter: Filter)` |
| `UseHeroSkill` | `(hero: HeroID, skill: SkillName)` |
| `Cast` | `(skill: SkillName)` or `(id: SkillName)` |
| `Wait` | `(Nms)` |
| `ChangeWeaponSet` | `(id: N)` |
| `StoreTarget` | `(id: N)` |
| `RestoreTarget` | `(id: N)` |
| `UseItem` | `(id: N)` |
| `UseItemList` | `(ids: N, M, ...)` |
| `SendChat` | `(channel: Channel, message: string)` |
| `FlagHero` | `(degree: X, distance: Y, hero: Z)` |
| `SetVariable` | `(name: X, value: Y, preserve: Z)` |
| `ClearTarget` | none |
| `Cancel` | none |
| `StopScript` | none |
| `PingHardMode` | none |
| `Conditioned` | `(cond: Condition, then: {...}, else: {...})` |

### Regenerating Constants

Skill and hero ID mappings are auto-generated from the C++ headers in `Dependencies/GWCA/`. If those headers change, regenerate:

```bash
python3 -m sst_gen.generate_constants
```

This produces `sst_gen/constants_generated.py` which is imported at parse time.

### Supported Values

- **SkillName**: `No_Skill`, `Dark_Aura`, `Strength_of_Honor`, `Soul_Twisting`, `Shelter`, `Union`, `Armor_of_Unfeeling`, `Displacement`, `Drunken_Master`, `Masochism`, `Soul_Taker`, ... (numeric IDs like `2218` also work)
- **HeroID**: `NoHero`, `Norgu`, `Goren`, `Tahlkora`, `MasterOfWhispers`, ..., `Ogden`, `Merc1`..`Merc8`, `Miku`, `ZeiRi`, `Devona`, `GhostOfAlthea`
- **Sorting**: `AgentId`, `ClosestToPlayer`, `FurthestFromPlayer`, `ClosestToTarget`, `FurthestFromTarget`, `LowestHp`, `HighestHp`, `ModelID`
- **Filter**: `Allegiance(Self)`, `Allegiance(PartyMember)`, `Allegiance(Hostile)`
- **Trigger**: `None`, `InstanceLoad`, `HardModePing`, `Hotkey`, `ChatMessage`
