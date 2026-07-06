"""AST definitions for the SST script generator.

Pure data types — no logic, no parsing, no serialization.
Every class maps 1:1 to a type in the C++ scripting engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Union


# === Enums ===


class Trigger(IntEnum):
    None_ = 0
    InstanceLoad = 1
    HardModePing = 2
    Hotkey = 3
    ChatMessage = 4
    BeginSkillCast = 5
    BeginCooldown = 6
    SkillCastInterrupt = 7
    DisplayDialog = 8
    DungeonReward = 9
    DoaZoneComplete = 10


class ConditionType(IntEnum):
    Not = 0
    Or = 1
    And = 2
    IsInMap = 3
    Deprecated_QuestObjectiveHasState = 4
    PartyPlayerCount = 5
    PartyMemberStatus = 6
    HasPartyWindowAllyOfName = 7
    InstanceProgress = 8
    InstanceTime = 9
    OnlyTriggerOncePerInstance = 10
    CanPopAgent = 11
    PlayerHasBuff = 13
    PlayerHasSkill = 14
    PlayerHasEnergy = 17
    PlayerHasItemEquipped = 19
    KeyIsPressed = 20
    PartyHasLoadedIn = 28
    ItemInInventory = 29
    InstanceType = 33
    RemainingCooldown = 34
    FoeCount = 35
    PlayerMorale = 36
    False_ = 37
    True_ = 38
    Until = 39
    Once = 40
    Toggle = 41
    After = 42
    Throttle = 44
    PlayerHasCharacteristics = 46
    TargetHasCharacteristics = 47
    AgentWithCharacteristicsCount = 48
    ScriptVariableValue = 49
    PlayerHasSkillBySlot = 50
    ScriptVariableIsSet = 51
    DoorStatus = 52
    PlayerHasEnergyRegen = 53
    QuestHasState = 54
    ObjectiveHasState = 55
    HeroHasSkill = 56
    HasTerrainClearance = 57
    PlayerIsDrunk = 58
    ItemInInventoryList = 59
    PlayerAdrenaline = 60
    HasCalledTarget = 61


class ActionType(IntEnum):
    MoveTo = 0
    Cast = 2
    CastBySlot = 3
    DropBuff = 4
    ChangeTarget = 5
    UseItem = 6
    EquipItem = 7
    RepopMinipet = 8
    PingHardMode = 9
    PingTarget = 10
    AutoAttackTarget = 11
    SendDialog = 12
    GoToTarget = 13
    Wait = 14
    SendChat = 15
    Cancel = 16
    Conditioned = 17
    ChangeWeaponSet = 18
    StoreTarget = 19
    RestoreTarget = 20
    StopScript = 21
    LogOut = 22
    UseHeroSkill = 23
    UnequipItem = 24
    ClearTarget = 25
    WaitUntil = 26
    MoveToTargetPosition = 27
    MoveInchwise = 28
    GWKey = 29
    EquipItemBySlot = 30
    EnterCriticalSection = 31
    LeaveCriticalSection = 32
    SetVariable = 33
    AbandonQuest = 34
    IncrementVariable = 35
    DecrementVariable = 36
    MoveItemToSlot = 37
    KeyboardMove = 39
    Random = 40
    AddHero = 41
    KickHero = 42
    LoadSkillbar = 43
    DestroyItem = 44
    DropItem = 45
    FlagHero = 46
    UseItemList = 47


class Sorting(IntEnum):
    AgentId = 0
    ClosestToPlayer = 1
    FurthestFromPlayer = 2
    ClosestToTarget = 3
    FurthestFromTarget = 4
    LowestHp = 5
    HighestHp = 6
    ModelID = 7


class Channel(IntEnum):
    All = 0
    Guild = 1
    Team = 2
    Trade = 3
    Alliance = 4
    Whisper = 5
    Emote = 6
    Log = 7


class AgentType(IntEnum):
    Any = 0
    Self = 1
    PartyMember = 2
    Friendly = 3
    Hostile = 4


class IsIsNot(IntEnum):
    Is_ = 0
    IsNot = 1


class ComparisonOperator(IntEnum):
    Equals = 0
    Less = 1
    Greater = 2
    LessOrEqual = 3
    GreaterOrEqual = 4
    NotEquals = 5


class HasSkillRequirement(IntEnum):
    OnBar = 0
    OffCooldown = 1
    ReadyToUse = 2


class AnyNoYes(IntEnum):
    Any = 0
    No = 1
    Yes = 2


class Class(IntEnum):
    Any = 0
    Warrior = 1
    Ranger = 2
    Monk = 3
    Necro = 4
    Mesmer = 5
    Elementalist = 6
    Assassin = 7
    Ritualist = 8
    Paragon = 9
    Dervish = 10


class Status(IntEnum):
    Enchanted = 0
    WeaponSpelled = 1
    Alive = 2
    Bleeding = 3
    Crippled = 4
    DeepWounded = 5
    Poisoned = 6
    Hexed = 7
    Idle = 8
    KnockedDown = 9
    Moving = 10
    Attacking = 11
    Casting = 12


class WeaponType(IntEnum):
    Any = 0
    None_ = 1
    Bow = 2
    Axe = 3
    Hammer = 4
    Daggers = 5
    Scythe = 6
    Spear = 7
    Sword = 8
    Wand = 9
    Staff = 10


class SkillType(IntEnum):
    Any = 0
    Spell = 1
    Signet = 2
    Well = 3
    Skill_ = 4
    Ward = 5
    Glyph = 6
    Attack = 7
    Preparation = 8
    Trap = 9
    Ritual = 10
    WeaponSpell = 11
    Chant = 12
    Hex = 13
    Enchantment = 14


class TrueFalse(IntEnum):
    True_ = 0
    False_ = 1


class GoToTargetFinishCondition(IntEnum):
    None_ = 0
    StoppedMovingNextToTarget = 1
    DialogOpen = 2


class MoveToBehaviour(IntEnum):
    SendOnce = 0
    RepeatIfIdle = 1
    ImmediateFinish = 2


class ReferenceFrame(IntEnum):
    Player = 0
    Camera = 1


class Bag(IntEnum):
    Backpack = 0
    BeltPouch = 1
    Bag1 = 2
    Bag2 = 3
    EquipmentPack = 4


class EquippedItemSlot(IntEnum):
    Mainhand = 0
    Offhand = 1
    Chest = 2
    Legs = 3
    Head = 4
    Feet = 5
    Hands = 6


class DoorStatus(IntEnum):
    Open = 0
    Closed = 1


class Area(IntEnum):
    Urgoz = 0
    Deep = 1
    Doa = 2


class DoaZone(IntEnum):
    Foundry = 0x273F
    Veil = 0x2740
    Gloom = 0x2741
    City = 0x2742


class MovementDirection(IntEnum):
    Forwards = 0
    Left = 1
    Right = 2
    Backwards = 3


class IdRestriction(IntEnum):
    Any = 0
    SpecificId = 1


class QuestStatus(IntEnum):
    NotStarted = 0
    Running = 1
    Completed = 2
    Failed = 3


class ObjectiveType(IntEnum):
    Quest = 0
    Mission = 1


class PlayerConnectednessRequirement(IntEnum):
    All = 0
    Individual = 1


class InstanceType(IntEnum):
    Explorable = 0
    Mission = 1


class CharacteristicType(IntEnum):
    Position = 0
    PositionPolygon = 1
    DistanceToPlayer = 2
    DistanceToTarget = 3
    Class_ = 4
    Name = 5
    HP = 6
    Speed = 7
    HPRegen = 8
    WeaponType_ = 9
    Model = 10
    Allegiance = 11
    Status_ = 12
    Skill = 13
    Bond = 14
    AngleToPlayerForward = 15
    AngleToCameraForward = 16
    DistanceToModelId = 17
    IsStoredTarget = 18
    Not = 19
    And = 20
    Or = 21


# === Script-level types ===


@dataclass
class Hotkey:
    key_data: int = 0
    modifier: int = 0


@dataclass
class TriggerData:
    hotkey: Hotkey = field(default_factory=Hotkey)
    message: str = ""
    skill_id: int = 0
    hsr: int = 0  # AnyNoYes
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
    trigger: int = 0  # Trigger enum
    trigger_data: TriggerData = field(default_factory=TriggerData)
    enabled: bool = True
    toggle_hotkey: Hotkey = field(default_factory=Hotkey)
    options: ScriptOptions = field(default_factory=ScriptOptions)
    conditions: list[Condition] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)


# === Characteristic types ===


class Characteristic:
    pass


@dataclass
class AllegianceCharacteristic(Characteristic):
    agent_type: int = 0  # AgentType
    comparison: int = 0  # IsIsNot


@dataclass
class StatusCharacteristic(Characteristic):
    status: int = 0  # Status
    comparison: int = 0  # IsIsNot
    skill_type: int = 0  # SkillType


@dataclass
class DistanceToPlayerCharacteristic(Characteristic):
    value: float = 166.0
    comparison: int = 3  # ComparisonOperator.LessOrEqual


@dataclass
class DistanceToTargetCharacteristic(Characteristic):
    value: float = 166.0
    comparison: int = 3  # ComparisonOperator.LessOrEqual


@dataclass
class DistanceToModelIdCharacteristic(Characteristic):
    value: float = 166.0
    comparison: int = 3  # ComparisonOperator.LessOrEqual
    model_id: int = 0


@dataclass
class PositionCharacteristic(Characteristic):
    x: float = 0.0
    y: float = 0.0
    accuracy: float = 166.0
    comparison: int = 3  # ComparisonOperator.LessOrEqual


@dataclass
class PositionPolygonCharacteristic(Characteristic):
    positions: list[tuple[float, float]] = field(default_factory=list)
    comparison: int = 0  # IsIsNot


@dataclass
class HPCharacteristic(Characteristic):
    hp: float = 50.0
    comparison: int = 3  # ComparisonOperator.LessOrEqual


@dataclass
class HPRegenCharacteristic(Characteristic):
    regen: int = 0
    comparison: int = 2  # ComparisonOperator.Greater


@dataclass
class SpeedCharacteristic(Characteristic):
    speed: float = 0.0
    comparison: int = 4  # ComparisonOperator.GreaterOrEqual


@dataclass
class ClassCharacteristic(Characteristic):
    primary: int = 0  # Class
    secondary: int = 0  # Class
    comparison: int = 0  # IsIsNot


@dataclass
class NameCharacteristic(Characteristic):
    name: str = ""
    comparison: int = 0  # IsIsNot


@dataclass
class ModelCharacteristic(Characteristic):
    model_id: int = 0
    comparison: int = 0  # IsIsNot


@dataclass
class WeaponTypeCharacteristic(Characteristic):
    weapon_type: int = 0  # WeaponType
    comparison: int = 0  # IsIsNot


@dataclass
class SkillCharacteristic(Characteristic):
    skill_id: int = 0
    comparison: int = 0  # IsIsNot


@dataclass
class BondCharacteristic(Characteristic):
    bond: int = 0
    comparison: int = 0  # IsIsNot


@dataclass
class AngleToPlayerForwardCharacteristic(Characteristic):
    angle: float = 180.0
    comparison: int = 3  # ComparisonOperator.LessOrEqual


@dataclass
class AngleToCameraForwardCharacteristic(Characteristic):
    angle: float = 180.0
    comparison: int = 3  # ComparisonOperator.LessOrEqual


@dataclass
class IsStoredTargetCharacteristic(Characteristic):
    slot: int = 0
    comparison: int = 0  # IsIsNot
    id_restriction: int = 0  # IdRestriction


@dataclass
class NegationCharacteristic(Characteristic):
    characteristic: Characteristic = field(default_factory=lambda: TrueCharacteristic())


@dataclass
class ConjunctionCharacteristic(Characteristic):
    characteristics: list[Characteristic] = field(default_factory=list)


@dataclass
class DisjunctionCharacteristic(Characteristic):
    characteristics: list[Characteristic] = field(default_factory=list)


@dataclass
class TrueCharacteristic(Characteristic):
    pass


Characteristic = Union[
    AllegianceCharacteristic,
    StatusCharacteristic,
    DistanceToPlayerCharacteristic,
    DistanceToTargetCharacteristic,
    DistanceToModelIdCharacteristic,
    PositionCharacteristic,
    PositionPolygonCharacteristic,
    HPCharacteristic,
    HPRegenCharacteristic,
    SpeedCharacteristic,
    ClassCharacteristic,
    NameCharacteristic,
    ModelCharacteristic,
    WeaponTypeCharacteristic,
    SkillCharacteristic,
    BondCharacteristic,
    AngleToPlayerForwardCharacteristic,
    AngleToCameraForwardCharacteristic,
    IsStoredTargetCharacteristic,
    NegationCharacteristic,
    ConjunctionCharacteristic,
    DisjunctionCharacteristic,
    TrueCharacteristic,
]


# === Condition types ===


class Condition:
    pass


@dataclass
class NegatedCondition(Condition):
    cond: Condition = field(default_factory=lambda: TrueCondition())


@dataclass
class ConjunctionCondition(Condition):
    conditions: list[Condition] = field(default_factory=list)


@dataclass
class DisjunctionCondition(Condition):
    conditions: list[Condition] = field(default_factory=list)


@dataclass
class IsInMapCondition(Condition):
    map_id: int = 0


@dataclass
class Deprecated_QuestObjectiveHasStateCondition(Condition):
    id: int = 0
    status: int = 0  # QuestStatus


@dataclass
class PartyPlayerCountCondition(Condition):
    count: int = 1
    comparison: int = 0  # ComparisonOperator


@dataclass
class PartyMemberStatusCondition(Condition):
    name: str = ""
    alive: int = 1  # AnyNoYes


@dataclass
class HasPartyWindowAllyOfNameCondition(Condition):
    name: str = ""


@dataclass
class InstanceProgressCondition(Condition):
    required_progress: float = 50.0
    comparison: int = 4  # ComparisonOperator.GreaterOrEqual


@dataclass
class InstanceTimeCondition(Condition):
    time_seconds: int = 0
    comparison: int = 4  # ComparisonOperator.GreaterOrEqual


@dataclass
class OnlyTriggerOnceCondition(Condition):
    pass


@dataclass
class CanPopAgentCondition(Condition):
    pass


@dataclass
class PlayerHasBuffCondition(Condition):
    skill_id: int = 0
    has_min_duration: bool = False
    min_duration: int = 0
    has_max_duration: bool = False
    max_duration: int = 0


@dataclass
class PlayerHasSkillCondition(Condition):
    skill_id: int = 0
    requirement: int = 2  # HasSkillRequirement.ReadyToUse


@dataclass
class PlayerHasSkillBySlotCondition(Condition):
    slot: int = 1
    requirement: int = 2  # HasSkillRequirement.ReadyToUse


@dataclass
class HeroHasSkillCondition(Condition):
    hero_id: int = 0  # HeroID
    skill_id: int = 0
    requirement: int = 2  # HasSkillRequirement.ReadyToUse


@dataclass
class PlayerHasEnergyCondition(Condition):
    energy: int = 0
    comparison: int = 4  # ComparisonOperator.GreaterOrEqual


@dataclass
class PlayerHasEnergyRegenCondition(Condition):
    regeneration: int = 4
    comparison: int = 0  # ComparisonOperator.Equals


@dataclass
class PlayerHasItemEquippedCondition(Condition):
    model_id: int = 0


@dataclass
class ItemInInventoryCondition(Condition):
    model_id: int = 0


@dataclass
class RemainingCooldownCondition(Condition):
    skill_id: int = 0
    has_min: bool = False
    min_cooldown: int = 0
    has_max: bool = False
    max_cooldown: int = 1000


@dataclass
class InstanceTypeCondition(Condition):
    instance_type: int = 0  # InstanceType


@dataclass
class PartyHasLoadedInCondition(Condition):
    requirement: int = 0  # PlayerConnectednessRequirement
    slot: int = 1


@dataclass
class FoeCountCondition(Condition):
    count: int = 0
    comparison: int = 3  # ComparisonOperator.LessOrEqual


@dataclass
class PlayerMoraleCondition(Condition):
    morale: int = 0
    comparison: int = 4  # ComparisonOperator.GreaterOrEqual


@dataclass
class FalseCondition(Condition):
    pass


@dataclass
class TrueCondition(Condition):
    pass


@dataclass
class UntilCondition(Condition):
    cond: Condition = field(default_factory=lambda: TrueCondition())


@dataclass
class OnceCondition(Condition):
    cond: Condition = field(default_factory=lambda: TrueCondition())


@dataclass
class AfterCondition(Condition):
    cond: Condition = field(default_factory=lambda: TrueCondition())


@dataclass
class ToggleCondition(Condition):
    default_state: int = 1  # TrueFalse.False_
    toggle_on_cond: Condition = field(default_factory=lambda: TrueCondition())
    toggle_off_cond: Condition = field(default_factory=lambda: TrueCondition())


@dataclass
class ThrottleCondition(Condition):
    delay_ms: int = 100


@dataclass
class PlayerHasCharacteristicsCondition(Condition):
    characteristic: Characteristic = field(default_factory=lambda: TrueCharacteristic())


@dataclass
class TargetHasCharacteristicsCondition(Condition):
    characteristic: Characteristic = field(default_factory=lambda: TrueCharacteristic())


@dataclass
class AgentWithCharacteristicsCountCondition(Condition):
    characteristics: list[Characteristic] = field(default_factory=list)
    count: int = 1
    comparison: int = 4  # ComparisonOperator.GreaterOrEqual


@dataclass
class ScriptVariableValueCondition(Condition):
    name: str = ""
    value: int = 0
    comparison: int = 0  # ComparisonOperator.Equals


@dataclass
class ScriptVariableIsSetCondition(Condition):
    name: str = ""
    comparison: int = 0  # IsIsNot


@dataclass
class DoorStatusCondition(Condition):
    door_id: int = 0
    status: int = 0  # DoorStatus
    area: int = 2  # Area.Doa


@dataclass
class QuestHasStateCondition(Condition):
    name: str = ""
    status: int = 0  # QuestStatus


@dataclass
class ObjectiveHasStateCondition(Condition):
    quest_name: str = ""
    objective_name: str = ""
    status: int = 0  # QuestStatus
    objective_type: int = 1  # ObjectiveType.Mission


@dataclass
class HeroHasEnergyCondition(Condition):
    hero_id: int = 0
    energy: int = 0
    comparison: int = 4  # ComparisonOperator.GreaterOrEqual


@dataclass
class HeroHasBuffCondition(Condition):
    hero_id: int = 0
    skill_id: int = 0


@dataclass
class HasTerrainClearanceCondition(Condition):
    degree: float = 0.0
    distance: float = 0.0


@dataclass
class PlayerIsDrunkCondition(Condition):
    min_level: int = 1
    has_min_level: bool = False


@dataclass
class ItemInInventoryListCondition(Condition):
    ids: list[int] = field(default_factory=list)


@dataclass
class PlayerAdrenalineCondition(Condition):
    skill_id: int = 0
    adrenaline: int = 0
    comparison: int = 4  # ComparisonOperator.GreaterOrEqual


@dataclass
class KeyIsPressedCondition(Condition):
    hotkey: Hotkey = field(default_factory=Hotkey)
    description: str = ""
    block_key: bool = False


@dataclass
class HasCalledTargetCondition(Condition):
    pass


@dataclass
class IsInCombatCondition(Condition):
    range: float = 1012.0
    comparison: int = 1  # ComparisonOperator.Less


def IsInCombat(range: float = 1012.0) -> IsInCombatCondition:
    """Higher-level condition: true when at least one hostile agent is within range (default 1012 gwinches)."""
    return IsInCombatCondition(range=range)


Condition = Union[
    NegatedCondition,
    ConjunctionCondition,
    DisjunctionCondition,
    IsInMapCondition,
    Deprecated_QuestObjectiveHasStateCondition,
    PartyPlayerCountCondition,
    PartyMemberStatusCondition,
    HasPartyWindowAllyOfNameCondition,
    InstanceProgressCondition,
    InstanceTimeCondition,
    OnlyTriggerOnceCondition,
    CanPopAgentCondition,
    PlayerHasBuffCondition,
    PlayerHasSkillCondition,
    PlayerHasSkillBySlotCondition,
    HeroHasSkillCondition,
    PlayerHasEnergyCondition,
    PlayerHasEnergyRegenCondition,
    PlayerHasItemEquippedCondition,
    ItemInInventoryCondition,
    RemainingCooldownCondition,
    InstanceTypeCondition,
    PartyHasLoadedInCondition,
    FoeCountCondition,
    PlayerMoraleCondition,
    FalseCondition,
    TrueCondition,
    UntilCondition,
    OnceCondition,
    AfterCondition,
    ToggleCondition,
    ThrottleCondition,
    PlayerHasCharacteristicsCondition,
    TargetHasCharacteristicsCondition,
    AgentWithCharacteristicsCountCondition,
    ScriptVariableValueCondition,
    ScriptVariableIsSetCondition,
    DoorStatusCondition,
    QuestHasStateCondition,
    ObjectiveHasStateCondition,
    HeroHasEnergyCondition,
    HeroHasBuffCondition,
    HasTerrainClearanceCondition,
    PlayerIsDrunkCondition,
    ItemInInventoryListCondition,
    PlayerAdrenalineCondition,
    KeyIsPressedCondition,
    HasCalledTargetCondition,
    IsInCombatCondition,
]


# === Action types ===


class Action:
    pass


@dataclass
class MoveToAction(Action):
    pos_x: float = 0.0
    pos_y: float = 0.0
    accuracy: float = 0.0
    move_behaviour: int = 1  # MoveToBehaviour.RepeatIfIdle


@dataclass
class MoveToTargetPositionAction(Action):
    target_distance: float = 0.0
    accuracy: float = 0.0
    move_behaviour: int = 1  # MoveToBehaviour.RepeatIfIdle


@dataclass
class MoveInchwiseAction(Action):
    forward: float = 1.0
    right: float = 0.0
    reference_frame: int = 1  # ReferenceFrame.Camera


@dataclass
class KeyboardMoveAction(Action):
    target_x: float = 0.0
    target_y: float = 0.0
    movement_direction: int = 2  # MovementDirection.Right


@dataclass
class GoToTargetAction(Action):
    finish_condition: int = 2  # GoToTargetFinishCondition.DialogOpen


@dataclass
class CastAction(Action):
    skill_id: int = 0


@dataclass
class CastBySlotAction(Action):
    slot: int = 1


@dataclass
class DropBuffAction(Action):
    skill_id: int = 0


@dataclass
class UseHeroSkillAction(Action):
    hero_id: int = 0
    skill_id: int = 0


@dataclass
class LoadSkillbarAction(Action):
    hero_id: int = 0
    build: str = ""


@dataclass
class CancelAction(Action):
    pass


@dataclass
class ChangeTargetAction(Action):
    sorting: int = 0  # Sorting
    prefer_non_hexed: bool = False
    require_same_model_id: bool = False
    rotate_through: bool = False
    characteristics: list[Characteristic] = field(default_factory=list)


@dataclass
class ClearTargetAction(Action):
    pass


@dataclass
class StoreTargetAction(Action):
    id: int = 0


@dataclass
class RestoreTargetAction(Action):
    id: int = 0


@dataclass
class UseItemAction(Action):
    id: int = 0


@dataclass
class UseItemListAction(Action):
    ids: list[int] = field(default_factory=list)


@dataclass
class EquipItemAction(Action):
    id: int = 0
    modstruct: int = 0
    has_modstruct: bool = False


@dataclass
class EquipItemBySlotAction(Action):
    bag: int = 4  # Bag.EquipmentPack
    slot: int = 1


@dataclass
class UnequipItemAction(Action):
    slot: int = 0  # EquippedItemSlot.Mainhand


@dataclass
class MoveItemToSlotAction(Action):
    id: int = 0
    modstruct: int = 0
    has_modstruct: bool = False
    bag_id: int = 0  # Bag.Backpack
    slot: int = 0


@dataclass
class DestroyItemAction(Action):
    id: int = 0


@dataclass
class DropItemAction(Action):
    id: int = 0


@dataclass
class ChangeWeaponSetAction(Action):
    id: int = 1


@dataclass
class SendDialogAction(Action):
    id: int = 0


@dataclass
class SendChatAction(Action):
    channel: int = 0  # Channel
    message: str = ""


@dataclass
class PingHardModeAction(Action):
    pass


@dataclass
class PingTargetAction(Action):
    only_once: bool = True


@dataclass
class AutoAttackTargetAction(Action):
    pass


@dataclass
class WaitAction(Action):
    ms: int = 1000


@dataclass
class WaitUntilAction(Action):
    condition: Condition = field(default_factory=lambda: TrueCondition())


@dataclass
class ConditionedAction(Action):
    condition: Condition = field(default_factory=lambda: TrueCondition())
    actions_if: list[Action] = field(default_factory=list)
    actions_else: list[Action] = field(default_factory=list)
    actions_else_if: list[tuple[Condition, list[Action]]] = field(default_factory=list)


@dataclass
class RandomAction(Action):
    actions: list[Action] = field(default_factory=list)


@dataclass
class StopScriptAction(Action):
    pass


@dataclass
class EnterCriticalSectionAction(Action):
    pass


@dataclass
class LeaveCriticalSectionAction(Action):
    pass


@dataclass
class SetVariableAction(Action):
    name: str = ""
    value: int = 0
    preserve: bool = False


@dataclass
class IncrementVariableAction(Action):
    name: str = ""


@dataclass
class DecrementVariableAction(Action):
    name: str = ""


@dataclass
class AbandonQuestAction(Action):
    name: str = ""


@dataclass
class RepopMinipetAction(Action):
    item_model_id: int = 36651
    agent_model_id: int = 350


@dataclass
class LogOutAction(Action):
    pass


@dataclass
class GWKeyAction(Action):
    action: int = 0  # GW::UI::ControlAction


@dataclass
class FlagHeroAction(Action):
    hero: int = 0
    degree: float = 0.0
    distance: float = 0.0


@dataclass
class AddHeroAction(Action):
    hero_id: int = 0


@dataclass
class KickHeroAction(Action):
    hero_id: int = 0


Action = Union[
    MoveToAction,
    MoveToTargetPositionAction,
    MoveInchwiseAction,
    KeyboardMoveAction,
    GoToTargetAction,
    CastAction,
    CastBySlotAction,
    DropBuffAction,
    UseHeroSkillAction,
    LoadSkillbarAction,
    CancelAction,
    ChangeTargetAction,
    ClearTargetAction,
    StoreTargetAction,
    RestoreTargetAction,
    UseItemAction,
    UseItemListAction,
    EquipItemAction,
    EquipItemBySlotAction,
    UnequipItemAction,
    MoveItemToSlotAction,
    DestroyItemAction,
    DropItemAction,
    ChangeWeaponSetAction,
    SendDialogAction,
    SendChatAction,
    PingHardModeAction,
    PingTargetAction,
    AutoAttackTargetAction,
    WaitAction,
    WaitUntilAction,
    ConditionedAction,
    RandomAction,
    StopScriptAction,
    EnterCriticalSectionAction,
    LeaveCriticalSectionAction,
    SetVariableAction,
    IncrementVariableAction,
    DecrementVariableAction,
    AbandonQuestAction,
    RepopMinipetAction,
    LogOutAction,
    GWKeyAction,
    FlagHeroAction,
    AddHeroAction,
    KickHeroAction,
]


# === Binary Serializer ===
# Matches the C++ plugin's output byte-for-byte.
# Design: caller writes separators, nodes write only their data.


class OutputStream:
    def __init__(self):
        self.parts: list[str] = []

    def write(self, val):
        """Write a value followed by a space. Matches C++ operator<<."""
        if isinstance(val, bool):
            val = 1 if val else 0
        self.parts.append(str(val) + " ")
        return self

    def write_string_with_spaces(self, s):
        """Write a string followed by '<'. Matches C++ writeStringWithSpaces."""
        self.parts.append(s + " < ")
        return self

    def write_separator(self, lvl=1):
        """Write a raw separator byte. No space after."""
        tokens = {1: 0x7F, 2: 0x04, 3: 0x05, 4: 0x06}
        self.parts.append(chr(tokens[lvl]))
        return self

    def __str__(self):
        return "".join(self.parts)


def _missing_token(stream):
    """Write the '/' missing content token."""
    stream.write('/')


# === Characteristic serialization ===


def _serialize_characteristic(stream, char):
    if char is None:
        _missing_token(stream)
        return
    if isinstance(char, AllegianceCharacteristic):
        _serialize_allegiance(stream, char)
    elif isinstance(char, StatusCharacteristic):
        _serialize_status(stream, char)
    elif isinstance(char, DistanceToPlayerCharacteristic):
        _serialize_distance_to_player(stream, char)
    elif isinstance(char, DistanceToTargetCharacteristic):
        _serialize_distance_to_target(stream, char)
    elif isinstance(char, DistanceToModelIdCharacteristic):
        _serialize_distance_to_model_id(stream, char)
    elif isinstance(char, PositionCharacteristic):
        _serialize_position(stream, char)
    elif isinstance(char, PositionPolygonCharacteristic):
        _serialize_position_polygon(stream, char)
    elif isinstance(char, HPCharacteristic):
        _serialize_hp(stream, char)
    elif isinstance(char, HPRegenCharacteristic):
        _serialize_hp_regen(stream, char)
    elif isinstance(char, SpeedCharacteristic):
        _serialize_speed(stream, char)
    elif isinstance(char, ClassCharacteristic):
        _serialize_class(stream, char)
    elif isinstance(char, NameCharacteristic):
        _serialize_name(stream, char)
    elif isinstance(char, ModelCharacteristic):
        _serialize_model(stream, char)
    elif isinstance(char, WeaponTypeCharacteristic):
        _serialize_weapon_type(stream, char)
    elif isinstance(char, SkillCharacteristic):
        _serialize_skill(stream, char)
    elif isinstance(char, BondCharacteristic):
        _serialize_bond(stream, char)
    elif isinstance(char, AngleToPlayerForwardCharacteristic):
        _serialize_angle_to_player_forward(stream, char)
    elif isinstance(char, AngleToCameraForwardCharacteristic):
        _serialize_angle_to_camera_forward(stream, char)
    elif isinstance(char, IsStoredTargetCharacteristic):
        _serialize_is_stored_target(stream, char)
    elif isinstance(char, NegationCharacteristic):
        _serialize_negation_char(stream, char)
    elif isinstance(char, ConjunctionCharacteristic):
        _serialize_conjunction_char(stream, char)
    elif isinstance(char, DisjunctionCharacteristic):
        _serialize_disjunction_char(stream, char)
    elif isinstance(char, TrueCharacteristic):
        _serialize_true_char(stream, char)


def _serialize_allegiance(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.Allegiance)
    stream.write(char.agent_type)
    stream.write(char.comparison)


def _serialize_status(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.Status_)
    stream.write(char.status)
    stream.write(char.comparison)
    stream.write(char.skill_type)


def _serialize_distance_to_player(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.DistanceToPlayer)
    stream.write(char.value)
    stream.write(char.comparison)


def _serialize_distance_to_target(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.DistanceToTarget)
    stream.write(char.value)
    stream.write(char.comparison)


def _serialize_distance_to_model_id(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.DistanceToModelId)
    stream.write(char.model_id)
    stream.write(char.value)
    stream.write(char.comparison)


def _serialize_position(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.Position)
    stream.write(char.x)
    stream.write(char.y)
    stream.write(char.accuracy)
    stream.write(char.comparison)


def _serialize_position_polygon(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.PositionPolygon)
    stream.write(len(char.positions))
    for x, y in char.positions:
        stream.write(x)
        stream.write(y)
    stream.write(char.comparison)


def _serialize_hp(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.HP)
    stream.write(char.hp)
    stream.write(char.comparison)


def _serialize_hp_regen(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.HPRegen)
    stream.write(char.regen)
    stream.write(char.comparison)


def _serialize_speed(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.Speed)
    stream.write(char.speed)
    stream.write(char.comparison)


def _serialize_class(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.Class_)
    stream.write(char.primary)
    stream.write(char.secondary)
    stream.write(char.comparison)


def _serialize_name(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.Name)
    stream.write_string_with_spaces(char.name)
    stream.write(char.comparison)


def _serialize_model(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.Model)
    stream.write(char.model_id)
    stream.write(char.comparison)


def _serialize_weapon_type(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.WeaponType_)
    stream.write(char.weapon_type)
    stream.write(char.comparison)


def _serialize_skill(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.Skill)
    stream.write(char.skill_id)
    stream.write(char.comparison)


def _serialize_bond(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.Bond)
    stream.write(char.bond)
    stream.write(char.comparison)


def _serialize_angle_to_player_forward(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.AngleToPlayerForward)
    stream.write(char.angle)
    stream.write(char.comparison)


def _serialize_angle_to_camera_forward(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.AngleToCameraForward)
    stream.write(char.angle)
    stream.write(char.comparison)


def _serialize_is_stored_target(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.IsStoredTarget)
    stream.write(char.comparison)
    stream.write(char.id_restriction)
    stream.write(char.slot)


def _serialize_negation_char(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.Not)
    _serialize_characteristic(stream, char.characteristic)
    stream.write_separator(3)


def _serialize_conjunction_char(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.And)
    for c in char.characteristics:
        _serialize_characteristic(stream, c)
        stream.write_separator(3)


def _serialize_disjunction_char(stream, char):
    stream.write('X')
    stream.write(CharacteristicType.Or)
    for c in char.characteristics:
        _serialize_characteristic(stream, c)
        stream.write_separator(3)


def _serialize_true_char(stream, char):
    # TrueCharacteristic has no type-specific data.
    # Its type marker is written by the caller as part of the condition.
    pass


# === Condition serialization ===


def _serialize_condition(stream, cond):
    if cond is None:
        _missing_token(stream)
        return
    if isinstance(cond, NegatedCondition):
        _serialize_negated_condition(stream, cond)
    elif isinstance(cond, ConjunctionCondition):
        _serialize_conjunction_condition(stream, cond)
    elif isinstance(cond, DisjunctionCondition):
        _serialize_disjunction_condition(stream, cond)
    elif isinstance(cond, IsInMapCondition):
        _serialize_is_in_map_condition(stream, cond)
    elif isinstance(cond, Deprecated_QuestObjectiveHasStateCondition):
        _serialize_deprecated_quest_objective(stream, cond)
    elif isinstance(cond, PartyPlayerCountCondition):
        _serialize_party_player_count_condition(stream, cond)
    elif isinstance(cond, PartyMemberStatusCondition):
        _serialize_party_member_status_condition(stream, cond)
    elif isinstance(cond, HasPartyWindowAllyOfNameCondition):
        _serialize_has_party_window_ally_of_name_condition(stream, cond)
    elif isinstance(cond, InstanceProgressCondition):
        _serialize_instance_progress_condition(stream, cond)
    elif isinstance(cond, InstanceTimeCondition):
        _serialize_instance_time_condition(stream, cond)
    elif isinstance(cond, OnlyTriggerOnceCondition):
        _serialize_only_trigger_once_condition(stream, cond)
    elif isinstance(cond, CanPopAgentCondition):
        _serialize_can_pop_agent_condition(stream, cond)
    elif isinstance(cond, PlayerHasBuffCondition):
        _serialize_player_has_buff_condition(stream, cond)
    elif isinstance(cond, PlayerHasSkillCondition):
        _serialize_player_has_skill_condition(stream, cond)
    elif isinstance(cond, PlayerHasSkillBySlotCondition):
        _serialize_player_has_skill_by_slot_condition(stream, cond)
    elif isinstance(cond, HeroHasSkillCondition):
        _serialize_hero_has_skill_condition(stream, cond)
    elif isinstance(cond, PlayerHasEnergyCondition):
        _serialize_player_has_energy_condition(stream, cond)
    elif isinstance(cond, PlayerHasEnergyRegenCondition):
        _serialize_player_has_energy_regen_condition(stream, cond)
    elif isinstance(cond, PlayerHasItemEquippedCondition):
        _serialize_player_has_item_equipped_condition(stream, cond)
    elif isinstance(cond, ItemInInventoryCondition):
        _serialize_item_in_inventory_condition(stream, cond)
    elif isinstance(cond, RemainingCooldownCondition):
        _serialize_remaining_cooldown_condition(stream, cond)
    elif isinstance(cond, InstanceTypeCondition):
        _serialize_instance_type_condition(stream, cond)
    elif isinstance(cond, PartyHasLoadedInCondition):
        _serialize_party_has_loaded_in_condition(stream, cond)
    elif isinstance(cond, FoeCountCondition):
        _serialize_foe_count_condition(stream, cond)
    elif isinstance(cond, PlayerMoraleCondition):
        _serialize_player_morale_condition(stream, cond)
    elif isinstance(cond, FalseCondition):
        _serialize_false_condition(stream, cond)
    elif isinstance(cond, TrueCondition):
        _serialize_true_condition(stream, cond)
    elif isinstance(cond, UntilCondition):
        _serialize_until_condition(stream, cond)
    elif isinstance(cond, OnceCondition):
        _serialize_once_condition(stream, cond)
    elif isinstance(cond, AfterCondition):
        _serialize_after_condition(stream, cond)
    elif isinstance(cond, ToggleCondition):
        _serialize_toggle_condition(stream, cond)
    elif isinstance(cond, ThrottleCondition):
        _serialize_throttle_condition(stream, cond)
    elif isinstance(cond, PlayerHasCharacteristicsCondition):
        _serialize_player_has_characteristics_condition(stream, cond)
    elif isinstance(cond, TargetHasCharacteristicsCondition):
        _serialize_target_has_characteristics_condition(stream, cond)
    elif isinstance(cond, AgentWithCharacteristicsCountCondition):
        _serialize_agent_with_characteristics_count_condition(stream, cond)
    elif isinstance(cond, ScriptVariableValueCondition):
        _serialize_script_variable_value_condition(stream, cond)
    elif isinstance(cond, ScriptVariableIsSetCondition):
        _serialize_script_variable_is_set_condition(stream, cond)
    elif isinstance(cond, DoorStatusCondition):
        _serialize_door_status_condition(stream, cond)
    elif isinstance(cond, QuestHasStateCondition):
        _serialize_quest_has_state_condition(stream, cond)
    elif isinstance(cond, ObjectiveHasStateCondition):
        _serialize_objective_has_state_condition(stream, cond)
    elif isinstance(cond, HeroHasEnergyCondition):
        _serialize_hero_has_energy_condition(stream, cond)
    elif isinstance(cond, HeroHasBuffCondition):
        _serialize_hero_has_buff_condition(stream, cond)
    elif isinstance(cond, HasTerrainClearanceCondition):
        _serialize_has_terrain_clearance_condition(stream, cond)
    elif isinstance(cond, PlayerIsDrunkCondition):
        _serialize_player_is_drunk_condition(stream, cond)
    elif isinstance(cond, ItemInInventoryListCondition):
        _serialize_item_in_inventory_list_condition(stream, cond)
    elif isinstance(cond, PlayerAdrenalineCondition):
        _serialize_player_adrenaline_condition(stream, cond)
    elif isinstance(cond, KeyIsPressedCondition):
        _serialize_key_is_pressed_condition(stream, cond)
    elif isinstance(cond, HasCalledTargetCondition):
        _serialize_has_called_target_condition(stream, cond)
    elif isinstance(cond, IsInCombatCondition):
        _serialize_is_in_combat_condition(stream, cond)


def _serialize_negated_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.Not)
    _serialize_condition(stream, cond.cond)


def _serialize_conjunction_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.And)
    stream.write(len(cond.conditions))
    for c in cond.conditions:
        _serialize_condition(stream, c)
        stream.write_separator(2)


def _serialize_disjunction_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.Or)
    stream.write(len(cond.conditions))
    for c in cond.conditions:
        _serialize_condition(stream, c)
        stream.write_separator(2)


def _serialize_is_in_map_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.IsInMap)
    stream.write(cond.map_id)


def _serialize_deprecated_quest_objective(stream, cond):
    stream.write('C')
    stream.write(ConditionType.Deprecated_QuestObjectiveHasState)
    stream.write(cond.id)
    stream.write(cond.status)


def _serialize_party_player_count_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.PartyPlayerCount)
    stream.write(cond.count)
    stream.write(cond.comparison)


def _serialize_party_member_status_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.PartyMemberStatus)
    stream.write(cond.alive)
    stream.write_string_with_spaces(cond.name)


def _serialize_has_party_window_ally_of_name_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.HasPartyWindowAllyOfName)
    stream.write_string_with_spaces(cond.name)


def _serialize_instance_progress_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.InstanceProgress)
    stream.write(cond.required_progress)
    stream.write(cond.comparison)


def _serialize_instance_time_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.InstanceTime)
    stream.write(cond.time_seconds)
    stream.write(cond.comparison)


def _serialize_only_trigger_once_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.OnlyTriggerOncePerInstance)


def _serialize_can_pop_agent_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.CanPopAgent)


def _serialize_player_has_buff_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.PlayerHasBuff)
    stream.write(cond.skill_id)
    stream.write(cond.min_duration)
    stream.write(cond.max_duration)
    stream.write(cond.has_min_duration)
    stream.write(cond.has_max_duration)


def _serialize_player_has_skill_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.PlayerHasSkill)
    stream.write(cond.skill_id)
    stream.write(cond.requirement)


def _serialize_player_has_skill_by_slot_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.PlayerHasSkillBySlot)
    stream.write(cond.slot)
    stream.write(cond.requirement)


def _serialize_hero_has_skill_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.HeroHasSkill)
    stream.write(cond.hero_id)
    stream.write(cond.skill_id)
    stream.write(cond.requirement)


def _serialize_player_has_energy_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.PlayerHasEnergy)
    stream.write(cond.energy)
    stream.write(cond.comparison)


def _serialize_player_has_energy_regen_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.PlayerHasEnergyRegen)
    stream.write(cond.regeneration)
    stream.write(cond.comparison)


def _serialize_player_has_item_equipped_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.PlayerHasItemEquipped)
    stream.write(cond.model_id)


def _serialize_item_in_inventory_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.ItemInInventory)
    stream.write(cond.model_id)


def _serialize_remaining_cooldown_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.RemainingCooldown)
    stream.write(cond.skill_id)
    stream.write(cond.has_min)
    stream.write(cond.has_max)
    stream.write(cond.min_cooldown)
    stream.write(cond.max_cooldown)


def _serialize_instance_type_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.InstanceType)
    stream.write(cond.instance_type)


def _serialize_party_has_loaded_in_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.PartyHasLoadedIn)
    stream.write(cond.requirement)
    stream.write(cond.slot)


def _serialize_foe_count_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.FoeCount)
    stream.write(cond.count)
    stream.write(cond.comparison)


def _serialize_player_morale_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.PlayerMorale)
    stream.write(cond.morale)
    stream.write(cond.comparison)


def _serialize_false_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.False_)


def _serialize_true_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.True_)


def _serialize_until_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.Until)
    _serialize_condition(stream, cond.cond)


def _serialize_once_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.Once)
    _serialize_condition(stream, cond.cond)


def _serialize_after_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.After)
    _serialize_condition(stream, cond.cond)


def _serialize_toggle_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.Toggle)
    stream.write(cond.default_state)
    if cond.toggle_on_cond:
        _serialize_condition(stream, cond.toggle_on_cond)
        stream.write_separator(2)
    else:
        _missing_token(stream)
    if cond.toggle_off_cond:
        _serialize_condition(stream, cond.toggle_off_cond)
        stream.write_separator(2)
    else:
        _missing_token(stream)


def _serialize_throttle_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.Throttle)
    stream.write(cond.delay_ms)


def _serialize_player_has_characteristics_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.PlayerHasCharacteristics)
    _serialize_characteristic(stream, cond.characteristic)
    stream.write_separator(3)


def _serialize_target_has_characteristics_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.TargetHasCharacteristics)
    _serialize_characteristic(stream, cond.characteristic)
    stream.write_separator(3)


def _serialize_agent_with_characteristics_count_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.AgentWithCharacteristicsCount)
    stream.write(cond.comparison)
    stream.write(cond.count)
    for c in cond.characteristics:
        _serialize_characteristic(stream, c)
        stream.write_separator(3)


def _serialize_script_variable_value_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.ScriptVariableValue)
    stream.write_string_with_spaces(cond.name)
    stream.write(cond.value)
    stream.write(cond.comparison)


def _serialize_script_variable_is_set_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.ScriptVariableIsSet)
    stream.write_string_with_spaces(cond.name)
    stream.write(cond.comparison)


def _serialize_door_status_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.DoorStatus)
    stream.write(cond.door_id)
    stream.write(cond.status)
    stream.write(cond.area)


def _serialize_quest_has_state_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.QuestHasState)
    stream.write_string_with_spaces(cond.name)
    stream.write(cond.status)


def _serialize_objective_has_state_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.ObjectiveHasState)
    stream.write_string_with_spaces(cond.quest_name)
    stream.write_string_with_spaces(cond.objective_name)
    stream.write(cond.status)
    stream.write(cond.objective_type)


def _serialize_hero_has_energy_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.HeroHasEnergy)
    stream.write(cond.hero_id)
    stream.write(cond.energy)
    stream.write(cond.comparison)


def _serialize_hero_has_buff_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.HeroHasBuff)
    stream.write(cond.hero_id)
    stream.write(cond.skill_id)


def _serialize_has_terrain_clearance_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.HasTerrainClearance)
    stream.write(cond.degree)
    stream.write(cond.distance)


def _serialize_player_is_drunk_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.PlayerIsDrunk)
    stream.write(cond.min_level)
    stream.write(cond.has_min_level)


def _serialize_item_in_inventory_list_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.ItemInInventoryList)
    stream.write(len(cond.ids))
    for item_id in cond.ids:
        stream.write(item_id)


def _serialize_player_adrenaline_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.PlayerAdrenaline)
    stream.write(cond.skill_id)
    stream.write(cond.adrenaline)
    stream.write(cond.comparison)


def _serialize_key_is_pressed_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.KeyIsPressed)
    stream.write(cond.hotkey.key_data)
    stream.write(cond.hotkey.modifier)
    stream.write(cond.block_key)


def _serialize_has_called_target_condition(stream, cond):
    stream.write('C')
    stream.write(ConditionType.HasCalledTarget)


def _serialize_is_in_combat_condition(stream, cond):
    _serialize_agent_with_characteristics_count_condition(stream, AgentWithCharacteristicsCountCondition(
        characteristics=[
            AllegianceCharacteristic(agent_type=AgentType.Hostile, comparison=IsIsNot.Is_),
            DistanceToPlayerCharacteristic(value=cond.range, comparison=cond.comparison),
        ],
        count=1,
        comparison=ComparisonOperator.GreaterOrEqual,
    ))


# === Action serialization ===


def _serialize_action(stream, action):
    if action is None:
        _missing_token(stream)
        return
    if isinstance(action, MoveToAction):
        _serialize_move_to_action(stream, action)
    elif isinstance(action, MoveToTargetPositionAction):
        _serialize_move_to_target_position_action(stream, action)
    elif isinstance(action, MoveInchwiseAction):
        _serialize_move_inchwise_action(stream, action)
    elif isinstance(action, KeyboardMoveAction):
        _serialize_keyboard_move_action(stream, action)
    elif isinstance(action, GoToTargetAction):
        _serialize_go_to_target_action(stream, action)
    elif isinstance(action, CastAction):
        _serialize_cast_action(stream, action)
    elif isinstance(action, CastBySlotAction):
        _serialize_cast_by_slot_action(stream, action)
    elif isinstance(action, DropBuffAction):
        _serialize_drop_buff_action(stream, action)
    elif isinstance(action, UseHeroSkillAction):
        _serialize_use_hero_skill_action(stream, action)
    elif isinstance(action, LoadSkillbarAction):
        _serialize_load_skillbar_action(stream, action)
    elif isinstance(action, CancelAction):
        _serialize_cancel_action(stream, action)
    elif isinstance(action, ChangeTargetAction):
        _serialize_change_target_action(stream, action)
    elif isinstance(action, ClearTargetAction):
        _serialize_clear_target_action(stream, action)
    elif isinstance(action, StoreTargetAction):
        _serialize_store_target_action(stream, action)
    elif isinstance(action, RestoreTargetAction):
        _serialize_restore_target_action(stream, action)
    elif isinstance(action, UseItemAction):
        _serialize_use_item_action(stream, action)
    elif isinstance(action, UseItemListAction):
        _serialize_use_item_list_action(stream, action)
    elif isinstance(action, EquipItemAction):
        _serialize_equip_item_action(stream, action)
    elif isinstance(action, EquipItemBySlotAction):
        _serialize_equip_item_by_slot_action(stream, action)
    elif isinstance(action, UnequipItemAction):
        _serialize_unequip_item_action(stream, action)
    elif isinstance(action, MoveItemToSlotAction):
        _serialize_move_item_to_slot_action(stream, action)
    elif isinstance(action, DestroyItemAction):
        _serialize_destroy_item_action(stream, action)
    elif isinstance(action, DropItemAction):
        _serialize_drop_item_action(stream, action)
    elif isinstance(action, ChangeWeaponSetAction):
        _serialize_change_weapon_set_action(stream, action)
    elif isinstance(action, SendDialogAction):
        _serialize_send_dialog_action(stream, action)
    elif isinstance(action, SendChatAction):
        _serialize_send_chat_action(stream, action)
    elif isinstance(action, PingHardModeAction):
        _serialize_ping_hard_mode_action(stream, action)
    elif isinstance(action, PingTargetAction):
        _serialize_ping_target_action(stream, action)
    elif isinstance(action, AutoAttackTargetAction):
        _serialize_auto_attack_target_action(stream, action)
    elif isinstance(action, WaitAction):
        _serialize_wait_action(stream, action)
    elif isinstance(action, WaitUntilAction):
        _serialize_wait_until_action(stream, action)
    elif isinstance(action, ConditionedAction):
        _serialize_conditioned_action(stream, action)
    elif isinstance(action, RandomAction):
        _serialize_random_action(stream, action)
    elif isinstance(action, StopScriptAction):
        _serialize_stop_script_action(stream, action)
    elif isinstance(action, EnterCriticalSectionAction):
        _serialize_enter_critical_section_action(stream, action)
    elif isinstance(action, LeaveCriticalSectionAction):
        _serialize_leave_critical_section_action(stream, action)
    elif isinstance(action, SetVariableAction):
        _serialize_set_variable_action(stream, action)
    elif isinstance(action, IncrementVariableAction):
        _serialize_increment_variable_action(stream, action)
    elif isinstance(action, DecrementVariableAction):
        _serialize_decrement_variable_action(stream, action)
    elif isinstance(action, AbandonQuestAction):
        _serialize_abandon_quest_action(stream, action)
    elif isinstance(action, RepopMinipetAction):
        _serialize_repop_minipet_action(stream, action)
    elif isinstance(action, LogOutAction):
        _serialize_log_out_action(stream, action)
    elif isinstance(action, GWKeyAction):
        _serialize_gw_key_action(stream, action)
    elif isinstance(action, FlagHeroAction):
        _serialize_flag_hero_action(stream, action)
    elif isinstance(action, AddHeroAction):
        _serialize_add_hero_action(stream, action)
    elif isinstance(action, KickHeroAction):
        _serialize_kick_hero_action(stream, action)


def _serialize_move_to_action(stream, action):
    stream.write('A')
    stream.write(ActionType.MoveTo)
    stream.write(action.pos_x)
    stream.write(action.pos_y)
    stream.write(action.accuracy)
    stream.write(action.move_behaviour)


def _serialize_move_to_target_position_action(stream, action):
    stream.write('A')
    stream.write(ActionType.MoveToTargetPosition)
    stream.write(action.target_distance)
    stream.write(action.move_behaviour)
    stream.write(action.accuracy)


def _serialize_move_inchwise_action(stream, action):
    stream.write('A')
    stream.write(ActionType.MoveInchwise)
    stream.write(action.forward)
    stream.write(action.right)
    stream.write(action.reference_frame)


def _serialize_keyboard_move_action(stream, action):
    stream.write('A')
    stream.write(ActionType.KeyboardMove)
    stream.write(action.target_x)
    stream.write(action.target_y)
    stream.write(action.movement_direction)


def _serialize_go_to_target_action(stream, action):
    stream.write('A')
    stream.write(ActionType.GoToTarget)
    stream.write(action.finish_condition)


def _serialize_cast_action(stream, action):
    stream.write('A')
    stream.write(ActionType.Cast)
    stream.write(action.skill_id)


def _serialize_cast_by_slot_action(stream, action):
    stream.write('A')
    stream.write(ActionType.CastBySlot)
    stream.write(action.slot)


def _serialize_drop_buff_action(stream, action):
    stream.write('A')
    stream.write(ActionType.DropBuff)
    stream.write(action.skill_id)


def _serialize_use_hero_skill_action(stream, action):
    stream.write('A')
    stream.write(ActionType.UseHeroSkill)
    stream.write(action.hero_id)
    stream.write(action.skill_id)


def _serialize_load_skillbar_action(stream, action):
    stream.write('A')
    stream.write(ActionType.LoadSkillbar)
    stream.write(action.hero_id)
    stream.write(action.build)


def _serialize_cancel_action(stream, action):
    stream.write('A')
    stream.write(ActionType.Cancel)


def _serialize_change_target_action(stream, action):
    stream.write('A')
    stream.write(ActionType.ChangeTarget)
    stream.write(action.sorting)
    stream.write(action.prefer_non_hexed)
    stream.write(action.require_same_model_id)
    stream.write(action.rotate_through)
    for c in action.characteristics:
        _serialize_characteristic(stream, c)
        stream.write_separator(3)


def _serialize_clear_target_action(stream, action):
    stream.write('A')
    stream.write(ActionType.ClearTarget)


def _serialize_store_target_action(stream, action):
    stream.write('A')
    stream.write(ActionType.StoreTarget)
    stream.write(action.id)


def _serialize_restore_target_action(stream, action):
    stream.write('A')
    stream.write(ActionType.RestoreTarget)
    stream.write(action.id)


def _serialize_use_item_action(stream, action):
    stream.write('A')
    stream.write(ActionType.UseItem)
    stream.write(action.id)


def _serialize_use_item_list_action(stream, action):
    stream.write('A')
    stream.write(ActionType.UseItemList)
    stream.write(len(action.ids))
    for item_id in action.ids:
        stream.write(item_id)


def _serialize_equip_item_action(stream, action):
    stream.write('A')
    stream.write(ActionType.EquipItem)
    stream.write(action.id)
    stream.write(action.modstruct)
    stream.write(action.has_modstruct)


def _serialize_equip_item_by_slot_action(stream, action):
    stream.write('A')
    stream.write(ActionType.EquipItemBySlot)
    stream.write(action.bag)
    stream.write(action.slot)


def _serialize_unequip_item_action(stream, action):
    stream.write('A')
    stream.write(ActionType.UnequipItem)
    stream.write(action.slot)


def _serialize_move_item_to_slot_action(stream, action):
    stream.write('A')
    stream.write(ActionType.MoveItemToSlot)
    stream.write(action.id)
    stream.write(action.modstruct)
    stream.write(action.has_modstruct)
    stream.write(action.bag_id)
    stream.write(action.slot)


def _serialize_destroy_item_action(stream, action):
    stream.write('A')
    stream.write(ActionType.DestroyItem)
    stream.write(action.id)


def _serialize_drop_item_action(stream, action):
    stream.write('A')
    stream.write(ActionType.DropItem)
    stream.write(action.id)


def _serialize_change_weapon_set_action(stream, action):
    stream.write('A')
    stream.write(ActionType.ChangeWeaponSet)
    stream.write(action.id)


def _serialize_send_dialog_action(stream, action):
    stream.write('A')
    stream.write(ActionType.SendDialog)
    stream.write(action.id)


def _serialize_send_chat_action(stream, action):
    stream.write('A')
    stream.write(ActionType.SendChat)
    stream.write(action.channel)
    stream.write_string_with_spaces(action.message)


def _serialize_ping_hard_mode_action(stream, action):
    stream.write('A')
    stream.write(ActionType.PingHardMode)


def _serialize_ping_target_action(stream, action):
    stream.write('A')
    stream.write(ActionType.PingTarget)
    stream.write(action.only_once)


def _serialize_auto_attack_target_action(stream, action):
    stream.write('A')
    stream.write(ActionType.AutoAttackTarget)


def _serialize_wait_action(stream, action):
    stream.write('A')
    stream.write(ActionType.Wait)
    stream.write(action.ms)


def _serialize_wait_until_action(stream, action):
    stream.write('A')
    stream.write(ActionType.WaitUntil)
    _serialize_condition(stream, action.condition)


def _serialize_conditioned_action(stream, action):
    stream.write('A')
    stream.write(ActionType.Conditioned)

    # Condition + level-2 separator
    _serialize_condition(stream, action.condition)
    stream.write_separator(2)

    # Then actions
    stream.write(len(action.actions_if))
    for a in action.actions_if:
        _serialize_action(stream, a)
        stream.write_separator(2)

    # Else actions
    stream.write(len(action.actions_else))
    for a in action.actions_else:
        _serialize_action(stream, a)
        stream.write_separator(2)

    # Else-if branches
    stream.write(len(action.actions_else_if))
    for ei_cond, ei_actions in action.actions_else_if:
        _serialize_condition(stream, ei_cond)
        stream.write_separator(2)
        stream.write(len(ei_actions))
        for a in ei_actions:
            _serialize_action(stream, a)
            stream.write_separator(2)


def _serialize_random_action(stream, action):
    stream.write('A')
    stream.write(ActionType.Random)
    stream.write(len(action.actions))
    for a in action.actions:
        _serialize_action(stream, a)
        stream.write_separator(2)


def _serialize_stop_script_action(stream, action):
    stream.write('A')
    stream.write(ActionType.StopScript)


def _serialize_enter_critical_section_action(stream, action):
    stream.write('A')
    stream.write(ActionType.EnterCriticalSection)


def _serialize_leave_critical_section_action(stream, action):
    stream.write('A')
    stream.write(ActionType.LeaveCriticalSection)


def _serialize_set_variable_action(stream, action):
    stream.write('A')
    stream.write(ActionType.SetVariable)
    stream.write_string_with_spaces(action.name)
    stream.write(action.value)
    stream.write(action.preserve)


def _serialize_increment_variable_action(stream, action):
    stream.write('A')
    stream.write(ActionType.IncrementVariable)
    stream.write_string_with_spaces(action.name)


def _serialize_decrement_variable_action(stream, action):
    stream.write('A')
    stream.write(ActionType.DecrementVariable)
    stream.write_string_with_spaces(action.name)


def _serialize_abandon_quest_action(stream, action):
    stream.write('A')
    stream.write(ActionType.AbandonQuest)
    stream.write_string_with_spaces(action.name)


def _serialize_repop_minipet_action(stream, action):
    stream.write('A')
    stream.write(ActionType.RepopMinipet)
    stream.write(action.item_model_id)
    stream.write(action.agent_model_id)


def _serialize_log_out_action(stream, action):
    stream.write('A')
    stream.write(ActionType.LogOut)


def _serialize_gw_key_action(stream, action):
    stream.write('A')
    stream.write(ActionType.GWKey)
    stream.write(action.action)


def _serialize_flag_hero_action(stream, action):
    stream.write('A')
    stream.write(ActionType.FlagHero)
    stream.write(action.degree)
    stream.write(action.distance)
    stream.write(action.hero)


def _serialize_add_hero_action(stream, action):
    stream.write('A')
    stream.write(ActionType.AddHero)
    stream.write(action.hero_id)


def _serialize_kick_hero_action(stream, action):
    stream.write('A')
    stream.write(ActionType.KickHero)
    stream.write(action.hero_id)


# === Trigger data serialization ===


def _serialize_trigger_data(stream, script):
    """Serialize trigger-specific data based on trigger type."""
    trigger = script.trigger
    td = script.trigger_data

    if trigger == Trigger.Hotkey:
        stream.write(td.hotkey.key_data)
        stream.write(td.hotkey.modifier)
    elif trigger == Trigger.ChatMessage:
        stream.write_string_with_spaces(td.message)
    elif trigger in (Trigger.BeginCooldown, Trigger.SkillCastInterrupt):
        stream.write(td.skill_id)
    elif trigger == Trigger.BeginSkillCast:
        stream.write(td.skill_id)
        stream.write(td.hsr)
    elif trigger == Trigger.DoaZoneComplete:
        stream.write(td.doa_zone)
    elif trigger == Trigger.DisplayDialog:
        stream.write_string_with_spaces(td.message)


# === Top-level script serialization ===


def serialize_script(script: Script) -> str:
    """Serialize a Script AST to the raw binary string (before Huffman encoding)."""
    stream = OutputStream()

    stream.write('S')
    stream.write_string_with_spaces(script.name)
    stream.write(script.trigger)
    stream.write(script.enabled)

    _serialize_trigger_data(stream, script)

    stream.write(script.toggle_hotkey.key_data)
    stream.write(script.toggle_hotkey.modifier)
    stream.write(script.options.show_message_when_triggered)
    stream.write(script.options.show_message_when_toggled)
    stream.write(script.options.globally_exclusive)
    stream.write(script.options.can_launch_in_parallel)

    stream.write_separator(1)

    for cond in script.conditions:
        _serialize_condition(stream, cond)
        stream.write_separator(1)

    for act in script.actions:
        _serialize_action(stream, act)
        stream.write_separator(1)

    return str(stream)
