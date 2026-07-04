# Conditions

Conditions gate script execution. A script runs only when ALL its conditions are true. Conditions are evaluated before a script starts, not during execution.

## Condition Types

### Logical

| ConditionType | Parameters | Description |
|--------------|-----------|-------------|
| `Not` | `cond: ConditionPtr` | Negate a condition |
| `Or` | `conditions: vector<ConditionPtr>` | True if any sub-condition is true |
| `And` | `conditions: vector<ConditionPtr>` | True if all sub-conditions are true |

### Game State

| ConditionType | Parameters | Description |
|--------------|-----------|-------------|
| `IsInMap` | `id: MapID` | True if in the specified map |
| `InstanceType` | `instanceType: InstanceType` | True if Explorable or Area (Quest/Mission) |
| `InstanceTime` | `timeInSeconds: int`, `comp: ComparisonOperator` | True if instance time meets comparison |
| `InstanceProgress` | `requiredProgress: float`, `comp: ComparisonOperator` | True if instance progress % meets comparison |
| `FoeCount` | `count: int`, `comp: ComparisonOperator` | True if number of foes meets comparison |
| `PlayerMorale` | `morale: int`, `comp: ComparisonOperator` | True if morale percentage meets comparison |
| `DoorStatus` | `id: DoorID`, `status: DoorStatus`, `area: Area` | True if door is open/closed |

### Party

| ConditionType | Parameters | Description |
|--------------|-----------|-------------|
| `PartyPlayerCount` | `count: int`, `comp: ComparisonOperator` | True if party player count meets comparison |
| `PartyHasLoadedIn` | `req: PlayerConnectednessRequirement`, `slot: int` | True if party members loaded (All or specific slot) |
| `PartyMemberStatus` | `name: string`, `alive: AnyNoYes` | True if named member is alive/dead/any |
| `HasPartyWindowAllyOfName` | `name: string` | True if party window has ally with name |

### Player

| ConditionType | Parameters | Description |
|--------------|-----------|-------------|
| `PlayerHasBuff` | `id: SkillID`, `minDuration/maxDuration: int`, `hasMin/hasMax: bool` | True if player has buff with duration range |
| `PlayerHasSkill` | `id: SkillID`, `requirement: HasSkillRequirement` | True if player has skill |
| `PlayerHasSkillBySlot` | `slot: int`, `requirement: HasSkillRequirement` | True if skill in slot meets requirement |
| `PlayerHasEnergy` | `energy: int`, `comp: ComparisonOperator` | True if energy meets comparison |
| `PlayerHasEnergyRegen` | `regeneration: int`, `comp: ComparisonOperator` | True if energy regen meets comparison |
| `PlayerHasItemEquipped` | `modelId: int` | True if player has item equipped |
| `PlayerHasCharacteristics` | `characteristic: CharacteristicPtr` | True if player matches characteristic |
| `RemainingCooldown` | `id: SkillID`, `hasMin/hasMax: bool`, `minCooldown/maxCooldown: int` | True if skill cooldown is in range |

### Hero

| ConditionType | Parameters | Description |
|--------------|-----------|-------------|
| `HeroHasSkill` | `heroId: HeroID`, `skillId: SkillID`, `requirement: HasSkillRequirement` | True if hero has skill |

### Items

| ConditionType | Parameters | Description |
|--------------|-----------|-------------|
| `ItemInInventory` | `modelId: int` | True if item with model ID is in inventory |

### Agent

| ConditionType | Parameters | Description |
|--------------|-----------|-------------|
| `CanPopAgent` | — | True if an agent can be spawned (minipet cooldown) |
| `TargetHasCharacteristics` | `characteristic: CharacteristicPtr` | True if current target matches characteristic |
| `AgentWithCharacteristicsCount` | `characteristics: vector<CharacteristicPtr>`, `count: int`, `comp: ComparisonOperator` | True if number of matching agents meets comparison |

### Terrain

| ConditionType | Parameters | Description |
|--------------|-----------|-------------|
| `HasTerrainClearance` | `degree: float`, `distance: float` | True if the point at degree (relative to player facing) and distance (gwinch) is on walkable terrain |

### Variables

| ConditionType | Parameters | Description |
|--------------|-----------|-------------|
| `ScriptVariableValue` | `name: string`, `value: int`, `comp: ComparisonOperator` | True if variable value meets comparison |
| `ScriptVariableIsSet` | `name: string`, `comp: IsIsNot` | True if variable is/is not set |

### Quests

| ConditionType | Parameters | Description |
|--------------|-----------|-------------|
| `QuestHasState` | `name: string`, `status: QuestStatus` | True if quest has specific status |
| `ObjectiveHasState` | `questName: string`, `objectiveName: string`, `status: QuestStatus`, `objectiveType: ObjectiveType` | True if quest objective has status |

### Control Flow

| ConditionType | Parameters | Description |
|--------------|-----------|-------------|
| `True` | — | Always true |
| `False` | — | Always false |
| `OnlyTriggerOncePerInstance` | — | True only the first time per instance |
| `Once` | `cond: ConditionPtr` | True once per instance when inner condition is true |
| `Until` | `cond: ConditionPtr` | True until inner condition becomes true, then stays true |
| `After` | `cond: ConditionPtr` | False until inner condition becomes true, then stays true |
| `Toggle` | `defaultState: TrueFalse`, `toggleOnCond: ConditionPtr`, `toggleOffCond: ConditionPtr` | Toggles between states on conditions |
| `Throttle` | `delayInMs: int` | True at most once per delay period |

### Input

| ConditionType | Parameters | Description |
|--------------|-----------|-------------|
| `KeyIsPressed` | `shortcut: Hotkey`, `description: string`, `blockKey: bool` | True while key is held. If `blockKey`, prevents GW from receiving the keypress |

## HasSkillRequirement

| Value | Meaning |
|-------|---------|
| `OnBar` | Skill is on the skill bar |
| `OffCooldown` | Skill is off cooldown |
| `ReadyToUse` | Skill is on bar and off cooldown |

## ComparisonOperator

| Value | Meaning |
|-------|---------|
| `Equals` | `==` |
| `Less` | `<` |
| `Greater` | `>` |
| `LessOrEqual` | `<=` |
| `GreaterOrEqual` | `>=` |
| `NotEquals` | `!=` |
