# Actions

Actions are executed sequentially when a script runs. Each action has a lifecycle: `initialAction()` -> poll `isComplete()` -> `finalAction()`.

## Action Behaviours

| Flag | Meaning |
|------|---------|
| `ImmediateFinish` | Runs and completes in one frame (no polling) |
| `CanBeRunInOutpost` | Script can run in outpost areas |

## Action Types

### Movement

| ActionType | Class | Parameters | Description |
|-----------|-------|-----------|-------------|
| `MoveTo` | `MoveToAction` | `pos: GamePos`, `accuracy: float` (default Adjacent), `moveBehaviour: MoveToBehaviour` | Walk to a fixed position |
| `MoveToTargetPosition` | `MoveToTargetPositionAction` | `targetDistance: float`, `accuracy: float`, `moveBehaviour: MoveToBehaviour` | Walk to current target's position at a distance |
| `MoveInchwise` | `MoveInchwiseAction` | `forward: float`, `right: float`, `refFrame: ReferenceFrame` | Micro-movement in a direction |
| `KeyboardMove` | `KeyboardMoveAction` | `targetPosition: GamePos`, `movementDirection: MovementDirection` | Keyboard-style movement |
| `GoToTarget` | `GoToTargetAction` | `finishCondition: GoToTargetFinishCondition` | Walk to current target. `None`/`StoppedMovingNextToTarget`/`DialogOpen` |

`MoveToBehaviour`: `SendOnce` | `RepeatIfIdle` | `ImmediateFinish`

### Skills

| ActionType | Class | Parameters | Description |
|-----------|-------|-----------|-------------|
| `Cast` | `CastAction` | `id: SkillID` | Cast skill by skill ID |
| `CastBySlot` | `CastBySlotAction` | `slot: int` (1-indexed) | Cast skill by slot position |
| `DropBuff` | `DropBuffAction` | `id: SkillID` | Drop a maintained buff |
| `UseHeroSkill` | `UseHeroSkillAction` | `hero: HeroID`, `skill: SkillID` | Command a hero to use a skill |
| `Cancel` | `CancelAction` | — | Cancel current action |
| `LoadSkillbar` | `LoadSkillbarAction` | `heroId: HeroID`, `build: string` | Load a skillbar build for a hero/player |

### Targeting

| ActionType | Class | Parameters | Description |
|-----------|-------|-----------|-------------|
| `ChangeTarget` | `ChangeTargetAction` | `sorting: Sorting`, `characteristics: vector<CharacteristicPtr>`, `preferNonHexed: bool`, `requireSameModelIdAsTarget: bool`, `rotateThroughTargets: bool` | Select an agent using characteristics |
| `ClearTarget` | `ClearTargetAction` | — | Deselect current target |
| `StoreTarget` | `StoreTargetAction` | `id: int` | Save current target to slot `id` |
| `RestoreTarget` | `RestoreTargetAction` | `id: int` | Restore target from slot `id` |

`Sorting`: `AgentId` | `ClosestToPlayer` | `FurthestFromPlayer` | `ClosestToTarget` | `FurthestFromTarget` | `LowestHp` | `HighestHp` | `ModelID`

### Items

| ActionType | Class | Parameters | Description |
|-----------|-------|-----------|-------------|
| `UseItem` | `UseItemAction` | `id: int` (model ID) | Use/consume an item by model ID |
| `EquipItem` | `EquipItemAction` | `id: int`, `modstruct: int`, `hasModstruct: bool` | Equip an item by model ID |
| `EquipItemBySlot` | `EquipItemBySlotAction` | `bag: Bag`, `slot: int` | Equip item from bag/slot |
| `UnequipItem` | `UnequipItemAction` | `slot: EquippedItemSlot` | Unequip from equipment slot |
| `MoveItemToSlot` | `MoveItemToSlotAction` | `id: int`, `modstruct: int`, `hasModstruct: bool`, `bagId: Bag`, `slot: int` | Move item to bag/slot |
| `DestroyItem` | `DestroyItemAction` | `id: int` (model ID) | Destroy an item |
| `DropItem` | `DropItemAction` | `id: int` (model ID) | Drop an item on ground |

### Dialog & Communication

| ActionType | Class | Parameters | Description |
|-----------|-------|-----------|-------------|
| `SendDialog` | `SendDialogAction` | `id: int` | Send a dialog response |
| `SendChat` | `SendChatAction` | `channel: Channel`, `message: string` | Send a chat message |
| `PingHardMode` | `PingHardModeAction` | — | Send the Hard Mode ping |
| `PingTarget` | `PingTargetAction` | `onlyOncePerInstance: bool` | Ping current target |
| `AutoAttackTarget` | `AutoAttackTargetAction` | — | Toggle auto-attack on target |

### Flow Control

| ActionType | Class | Parameters | Description |
|-----------|-------|-----------|-------------|
| `Wait` | `WaitAction` | `waitTime: int` (ms) | Pause for N milliseconds |
| `WaitUntil` | `WaitUntilAction` | `condition: ConditionPtr` | Pause until condition is true |
| `Conditioned` | `ConditionedAction` | `cond: ConditionPtr`, `actionsIf: vector<ActionPtr>`, `actionsElse: vector<ActionPtr>`, `actionsElseIf: vector<pair<ConditionPtr, vector<ActionPtr>>>` | If/else-if/else branching |
| `Random` | `RandomAction` | `actions: vector<ActionPtr>` | Pick and execute a random action from the list |
| `StopScript` | `StopScriptAction` | — | Abort the current script |
| `EnterCriticalSection` | `EnterCriticalSectionAction` | — | Set `globallyExclusive = true` (blocks other scripts) |
| `LeaveCriticalSection` | `LeaveCriticalSectionAction` | — | Set `globallyExclusive = false` |

### Game State

| ActionType | Class | Parameters | Description |
|-----------|-------|-----------|-------------|
| `ChangeWeaponSet` | `ChangeWeaponSetAction` | `id: int` (1-indexed) | Switch weapon set |
| `LogOut` | `LogOutAction` | — | Log out to character select |
| `RepopMinipet` | `RepopMinipetAction` | `itemModelId: int` (default 36651), `agentModelId: uint16_t` (default 350) | Use minipet pop item |
| `GWKey` | `GWKeyAction` | `action: ControlAction` | Press a GW UI key (interact, etc.) |
| `AbandonQuest` | `AbandonQuestAction` | `name: string` | Abandon a quest by name |

### Party

| ActionType | Class | Parameters | Description |
|-----------|-------|-----------|-------------|
| `FlagHero` | `FlagHeroAction` | `hero: int` (0=all, 1-7), `degree: float`, `distance: float` | Flag a hero at a relative position from player facing (or target direction). Only works in explorable areas. |

### Variables

| ActionType | Class | Parameters | Description |
|-----------|-------|-----------|-------------|
| `SetVariable` | `SetVariableAction` | `name: string`, `value: int`, `preserveThroughInstanceLoad: bool` | Set a script variable |
| `IncrementVariable` | `IncrementVariableAction` | `name: string` | Increment variable by 1 |
| `DecrementVariable` | `DecrementVariableAction` | `name: string` | Decrement variable by 1 |
