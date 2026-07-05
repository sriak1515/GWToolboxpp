# Task 1: AST Definitions

**Depends on:** nothing  
**Output:** dataclass definitions in the final `sst_gen.py`

## What to build

Pure data types. No logic, no parsing, no serialization. Just `@dataclass` definitions that represent every possible .sst script.

## Types

### Script-level

```python
@dataclass
class Hotkey:
    key_data: int = 0
    modifier: int = 0

@dataclass
class TriggerData:
    hotkey: Hotkey = field(default_factory=Hotkey)
    message: str = ""
    skill_id: int = 0
    hsr: int = 0          # AnyNoYes: 0=Any, 1=No, 2=Yes
    doa_zone: int = 0

@dataclass
class ScriptOptions:
    show_message_when_triggered: bool = False
    show_message_when_toggled: bool = False
    globally_exclusive: bool = False
    can_launch_in_parallel: bool = False

@dataclass
class Script:
    name: str = ""
    trigger: int = 0      # Trigger enum value
    trigger_data: TriggerData = field(default_factory=TriggerData)
    enabled: bool = True
    toggle_hotkey: Hotkey = field(default_factory=Hotkey)
    options: ScriptOptions = field(default_factory=ScriptOptions)
    conditions: list = field(default_factory=list)   # list[Condition]
    actions: list = field(default_factory=list)      # list[Action]
```

### Conditions

One dataclass per `ConditionType` value. Every dataclass inherits from a `Condition` base with a `type_id` class variable.

Cover all 63 condition types from `Condition.h:8`. The ones used in existing scripts:

- `TrueCondition`, `FalseCondition`
- `NegatedCondition(cond)`
- `ConjunctionCondition(conditions)`, `DisjunctionCondition(conditions)`
- `FoeCountCondition(count, comparison)`
- `PlayerHasBuffCondition(skill_id, has_min_duration, min_duration, has_max_duration, max_duration)`
- `PlayerHasSkillCondition(skill_id, requirement)`
- `PlayerHasSkillBySlotCondition(slot, requirement)`
- `HeroHasSkillCondition(hero_id, skill_id, requirement)`
- `ThrottleCondition(delay_ms)`
- `OnlyTriggerOnceCondition`
- `PlayerIsDrunkCondition(min_level, has_min_level)`
- `ItemInInventoryListCondition(ids)`
- `HasTerrainClearanceCondition(degree, distance)`
- `ScriptVariableIsSetCondition(name, comp)`
- `ScriptVariableValueCondition(name, value, comparison)`
- `PlayerHasCharacteristicsCondition(characteristic)`
- `TargetHasCharacteristicsCondition(characteristic)`
- `AgentWithCharacteristicsCountCondition(characteristics, count, comparison)`
- `PlayerHasEnergyCondition(energy, comparison)`
- `PlayerHasEnergyRegenCondition(regeneration, comparison)`
- `PlayerHasItemEquippedCondition(model_id)`
- `ItemInInventoryCondition(model_id)`
- `RemainingCooldownCondition(skill_id, has_min, min_cooldown, has_max, max_cooldown)`
- `InstanceTimeCondition(time_seconds, comparison)`
- `InstanceProgressCondition(required_progress, comparison)`
- `InstanceTypeCondition(instance_type)`
- `IsInMapCondition(map_id)`
- `PartyPlayerCountCondition(count, comparison)`
- `PartyHasLoadedInCondition(requirement, slot)`
- `PartyMemberStatusCondition(name, alive)`
- `HasPartyWindowAllyOfNameCondition(name)`
- `DoorStatusCondition(door_id, status, area)`
- `PlayerMoraleCondition(morale, comparison)`
- `KeyIsPressedCondition(hotkey, description, block_key)`
- `PlayerHasCharacteristicsCondition(characteristic)`
- `ObjectiveHasStateCondition(quest_name, objective_name, status, objective_type)`
- `QuestHasStateCondition(name, status)`
- `UntilCondition(cond)`, `OnceCondition(cond)`, `AfterCondition(cond)`
- `ToggleCondition(default_state, toggle_on_cond, toggle_off_cond)`
- `CanPopAgentCondition`
- `HeroHasEnergyCondition(hero_id, energy, comparison)`
- `HeroHasBuffCondition(hero_id, skill_id)`
- `PlayerAdrenalineCondition(skill_id, adrenaline, comparison)`

Plus the `Characteristics` subtypes (used by `PlayerHasCharacteristics`, `TargetHasCharacteristics`, `AgentWithCharacteristicsCount`, and `ChangeTarget` filters):

- `AllegianceCharacteristic(agent_type, comparison)`
- `StatusCharacteristic(status, comparison, skill_type)`
- `DistanceToPlayerCharacteristic(value, comparison)`
- `DistanceToTargetCharacteristic(value, comparison)`
- `PositionCharacteristic(x, y, accuracy)`
- `PositionPolygonCharacteristic(positions)`
- `HPCharacteristic(hp, comparison)`
- `HPRegenCharacteristic(regen, comparison)`
- `SpeedCharacteristic(speed, comparison)`
- `ClassCharacteristic(primary, secondary)`
- `NameCharacteristic(name, comparison)`
- `ModelCharacteristic(model_id, comparison)`
- `WeaponTypeCharacteristic(weapon_type, comparison)`
- `SkillCharacteristic(skill_id, comparison)`
- `BondCharacteristic(bond, comparison)`
- `AngleToPlayerForwardCharacteristic(angle, comparison)`
- `AngleToCameraForwardCharacteristic(angle, comparison)`
- `IsStoredTargetCharacteristic(slot, comparison)`
- `NegationCharacteristic(characteristic)`
- `ConjunctionCharacteristic(characteristics)`
- `DisjunctionCharacteristic(characteristics)`

### Actions

One dataclass per `ActionType` value. All 48 from `Action.h:7`:

- `MoveToAction(pos_x, pos_y, accuracy, move_behaviour)`
- `MoveToTargetPositionAction(target_distance, accuracy, move_behaviour)`
- `MoveInchwiseAction(forward, right, reference_frame)`
- `KeyboardMoveAction(target_x, target_y, movement_direction)`
- `GoToTargetAction(finish_condition)`
- `CastAction(skill_id)`
- `CastBySlotAction(slot)`
- `DropBuffAction(skill_id)`
- `UseHeroSkillAction(hero_id, skill_id)`
- `LoadSkillbarAction(hero_id, build)`
- `CancelAction`
- `ChangeTargetAction(sorting, prefer_non_hexed, require_same_model_id, rotate_through, characteristics)`
- `ClearTargetAction`
- `StoreTargetAction(id)`
- `RestoreTargetAction(id)`
- `UseItemAction(id)`
- `UseItemListAction(ids)`
- `EquipItemAction(id, modstruct, has_modstruct)`
- `EquipItemBySlotAction(bag, slot)`
- `UnequipItemAction(slot)`
- `MoveItemToSlotAction(id, modstruct, has_modstruct, bag_id, slot)`
- `DestroyItemAction(id)`
- `DropItemAction(id)`
- `ChangeWeaponSetAction(id)`
- `SendDialogAction(id)`
- `SendChatAction(channel, message)`
- `PingHardModeAction`
- `PingTargetAction(only_once)`
- `AutoAttackTargetAction`
- `GoToTargetAction(finish_condition)`
- `WaitAction(ms)`
- `WaitUntilAction(condition)`
- `ConditionedAction(condition, actions_if, actions_else, actions_else_if)`
- `RandomAction(actions)`
- `StopScriptAction`
- `EnterCriticalSectionAction`
- `LeaveCriticalSectionAction`
- `SetVariableAction(name, value, preserve)`
- `IncrementVariableAction(name)`
- `DecrementVariableAction(name)`
- `AbandonQuestAction(name)`
- `RepopMinipetAction(item_model_id, agent_model_id)`
- `LogOutAction`
- `GWKeyAction(action)`
- `FlagHeroAction(hero, degree, distance)`
- `AddHeroAction(hero_id)`
- `KickHeroAction(hero_id)`

### Enums (as Python IntEnum or plain dicts)

Map from string names to integer values for all enums used above. Reference: `Enums.h`, `Condition.h`, `Action.h`.

Key enums:
- `Trigger`: None=0, InstanceLoad=1, HardModePing=2, Hotkey=3, ChatMessage=4, ...
- `ActionType`: MoveTo=0, Cast=2, ... (gaps at 1 and 38)
- `ConditionType`: Not=0, Or=1, And=2, ... (gaps at 12, 15-16, 18, 21-27, 30-32, 43, 45)
- `Sorting`, `Channel`, `AgentType`, `IsIsNot`, `ComparisonOperator`, `HasSkillRequirement`
- `CharacteristicType`: Position=0, ... (see `Characteristic.h`)
- `SkillID`, `HeroID` — the known IDs from `SkillID.Skills` and `HeroID.Heroes` in the existing script

## Reference

Read these files to get exact enum values and field names:
- `plugins/Scripting/Condition.h:8-55` — ConditionType enum
- `plugins/Scripting/Action.h:7-58` — ActionType enum
- `plugins/Scripting/Enums.h:11-36` — all shared enums
- `plugins/Scripting/Characteristic.h` — CharacteristicType enum
- `plugins/Scripting/ConditionImpls.h` — constructor signatures for each condition
- `plugins/Scripting/ActionImpls.h` — constructor signatures for each action
- `plugins/Scripting/CharacteristicImpls.h` — constructor signatures for each characteristic
