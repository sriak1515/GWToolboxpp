# Plan: Terrain/Wall Analysis for Auto-Formation Detection

## Goal

Auto-detect whether the current area can fit the wide hero formation (944 gwinch span) or needs the narrow formation (506 gwinch span), then flag heroes accordingly.

## Current State

- `FlagHero` action exists in SST (degree, distance, hero parameters)
- Two formation scripts exist: `scripts/sst/flag-wide-formation.sst` and `scripts/sst/flag-narrow-formation.sst`
- Player must manually choose which formation to use

## Task for New Session

### Step 1: Investigate GWCA Terrain APIs

Read these files to understand available terrain/collision data:

1. `Dependencies/GWCA/include/GWCA/Context/MapContext.h` — Collision mesh, heightmap, object data
2. `Dependencies/GWCA/include/GWCA/Context/GameContext.h` — `GetGameContext()->map` accessor
3. `Dependencies/GWCA/include/GWCA/Managers/AgentMgr.h` — Any existing raycast/collision functions
4. `Dependencies/GWCA/include/GWCA/Context/AgentContext.h` — Pathfinding data

**Questions to answer:**
- Does `MapContext` expose a collision mesh or heightmap?
- Is there a raycast or point-in-polygon query?
- How does the game's pathfinding work?
- Are there existing GWCA wrappers for terrain queries?

### Step 2: Choose Implementation Approach

**Option A: New Characteristic (recommended)**

Add `TerrainClearance` characteristic:
```
CharacteristicType: TerrainClearance
Parameters: degree: float, distance: float
Returns: True if clearance exists in direction at distance
```

Pros: Reusable, composable with existing conditions, fits SST architecture
Cons: More files to modify

**Option B: New Action**

Add `FlagFormation` action that probes terrain internally:
```
ActionType: FlagFormation
Parameters: wide_coords, narrow_coords, probe_distance
Behavior: Probe terrain, pick formation, flag heroes
```

Pros: Self-contained, simpler for users
Cons: Less flexible, harder to compose

**Option C: Condition-based (simplest)**

Add `HasTerrainClearance` condition, create two scripts with complementary conditions.

Pros: No C++ changes to action/characteristic system
Cons: Requires multiple scripts, less elegant

### Step 3: Implement Terrain Query

Based on chosen approach, implement the terrain query. Files likely to modify:

| File | Change |
|------|--------|
| `plugins/Scripting/Characteristic.h` | Add new `CharacteristicType` enum value |
| `plugins/Scripting/CharacteristicImpls.h` | Add class declaration |
| `plugins/Scripting/CharacteristicImpls.cpp` | Implement terrain query using GWCA APIs |
| `plugins/Scripting/CharacteristicIO.cpp` | Register in UI |
| `docs/sst/05-characteristics.md` | Document new characteristic |

### Step 4: Create Auto-Detection Script

Create `scripts/sst/flag-formation-auto.sst` that:
1. Probes terrain in 4+ directions (cardinal) at 472 gwinch (wide formation span)
2. If all probes pass → run wide formation actions
3. If any probe fails → run narrow formation actions

### Step 5: Test

Test in:
- Wide open areas (Embell Beach, Pongmei Valley)
- Narrow corridors (Sardel Lacar, dungeon entrances)
- Transition zones (entering dungeon from open world)

## Key Files Reference

```
// Existing FlagHero implementation
plugins/Scripting/Action.h              — ActionType::FlagHero = 46
plugins/Scripting/ActionImpls.h         — FlagHeroAction class
plugins/Scripting/ActionImpls.cpp:2653  — FlagHeroAction implementation
plugins/Scripting/ActionIO.cpp:343      — Party submenu registration

// Formation scripts
scripts/sst/flag-wide-formation.sst    — Wide 0-5-2 (7 FlagHero actions)
scripts/sst/flag-narrow-formation.sst  — Narrow 0-5-2 (7 FlagHero actions)

// Spatial query patterns (for reference)
plugins/Scripting/CharacteristicImpls.cpp — DistanceToPlayer, AngleToPlayerForward
plugins/Scripting/ActionImpls.cpp:2666    — FlagHero position math

// GWCA terrain (to investigate)
Dependencies/GWCA/include/GWCA/Context/MapContext.h
Dependencies/GWCA/include/GWCA/Managers/AgentMgr.h
```

## Success Criteria

1. A single script that auto-detects terrain and flags heroes in the appropriate formation
2. Works reliably in wide, narrow, and transition areas
3. Performance acceptable (no noticeable lag when probing terrain)
4. Falls back to narrow formation when unsure (safe default)
