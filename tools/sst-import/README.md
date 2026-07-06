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
| `PlayerHasCharacteristics` | `(Characteristic)` — true if player matches characteristic |
| `True_` | (no parameters) — always true |
| `False_` | (no parameters) — always false |
| `not` | Wraps any condition: `not PlayerHasBuff(...)` |

### Characteristic Types

Characteristics are used by `PlayerHasCharacteristics` to filter agents. They can be combined with `And`, `Or`, `Not` logical operators.

| Characteristic | Parameters | Description |
|---------------|-----------|-------------|
| `Allegiance` | `(agentType: AgentType, comp: Is_\|IsNot)` | Agent's allegiance (Self, PartyMember, Friendly, Hostile) |
| `Status` | `(status: Status, comp: Is_\|IsNot)` | Agent's status (Alive, Attacking, Casting, etc.) |
| `HP` | `(hp: float, comp: <\|>\|<=\|>=\|==\|!=)` | Agent's HP percentage |
| `HPRegen` | `(hpRegen: int, comp: <\|>\|<=\|>=\|==\|!=)` | Agent's HP regeneration |
| `Speed` | `(speed: float, comp: <\|>\|<=\|>=\|==\|!=)` | Agent's movement speed |
| `DistanceToPlayer` | `(distance: float, comp: <\|>\|<=\|>=\|==\|!=)` | Distance to player meets comparison |
| `DistanceToTarget` | `(distance: float, comp: <\|>\|<=\|>=\|==\|!=)` | Distance to current target meets comparison |
| `DistanceToModelId` | `(modelId: int, distance: float, comp: <\|>\|<=\|>=\|==\|!=)` | Distance to agent with model ID |
| `Position` | `(x: float, y: float, distance: float, comp: <\|>\|<=\|>=\|==\|!=)` | Agent is within distance of position |
| `Class` | `(primary: Class, secondary: Class, comp: Is_\|IsNot)` | Agent's primary/secondary class |
| `Name` | `(name: string, comp: Is_\|IsNot)` | Agent's decoded name |
| `Model` | `(modelId: int, comp: Is_\|IsNot)` | Agent's model ID |
| `WeaponType` | `(weapon: WeaponType, comp: Is_\|IsNot)` | Agent's equipped weapon type |
| `Skill` | `(skill: SkillID, comp: Is_\|IsNot)` | Agent is casting/has skill active |
| `Bond` | `(skill: SkillID, comp: Is_\|IsNot)` | Agent has bond/communing skill |
| `AngleToPlayerForward` | `(angle: float, comp: <\|>\|<=\|>=\|==\|!=)` | Angle to player's forward direction |
| `AngleToCameraForward` | `(angle: float, comp: <\|>\|<=\|>=\|==\|!=)` | Angle to camera's forward direction |
| `IsStoredTarget` | `(slot: int, comp: Is_\|IsNot, idRestriction: Any\|SpecificId)` | Agent is/isn't a stored target |
| `And` | `(Characteristic, Characteristic, ...)` | All must match |
| `Or` | `(Characteristic, Characteristic, ...)` | Any must match |
| `Not` | `(Characteristic)` | Negate a characteristic |

#### Examples

```sst
// Player is attacking
PlayerHasCharacteristics(Status(Attacking))

// Player has less than 50% HP
PlayerHasCharacteristics(HP(50, <))

// Player is enchanted and has more than 100 energy
PlayerHasCharacteristics(And(Status(Enchanted), DistanceToPlayer(500, <)))
```

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
