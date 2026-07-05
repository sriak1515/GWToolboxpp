#!/usr/bin/env python3
"""Generate SST clipboard-importable script strings from .sst files.

Usage:
    python3 sst_script_gen.py dark-aura-maintainer.sst          # Copy to clipboard
    python3 sst_script_gen.py dark-aura-maintainer.sst --dry-run # Print only
"""
import sys
import re

# === Enum values (must match SST source) ===

class Trigger:
    None_ = 0; InstanceLoad = 1; HardModePing = 2; Hotkey = 3
    ChatMessage = 4; BeginSkillCast = 5; BeginCooldown = 6
    SkillCastInterrupt = 7; DisplayDialog = 8; DungeonReward = 9
    DoaZoneComplete = 10

class ConditionType:
    Not = 0; Or = 1; And = 2; IsInMap = 3
    Deprecated_QuestObjectiveHasState = 4; PartyPlayerCount = 5
    PartyMemberStatus = 6; HasPartyWindowAllyOfName = 7
    InstanceProgress = 8; InstanceTime = 9
    OnlyTriggerOncePerInstance = 10; CanPopAgent = 11
    PlayerHasBuff = 13; PlayerHasSkill = 14
    PlayerHasEnergy = 17; PlayerHasItemEquipped = 19
    KeyIsPressed = 20; PartyHasLoadedIn = 28
    ItemInInventory = 29; InstanceType = 33
    RemainingCooldown = 34; FoeCount = 35
    PlayerMorale = 36; False_ = 37; True_ = 38
    Until = 39; Once = 40; Toggle = 41; After = 42
    Throttle = 44; PlayerHasCharacteristics = 46
    TargetHasCharacteristics = 47
    AgentWithCharacteristicsCount = 48
    ScriptVariableValue = 49; PlayerHasSkillBySlot = 50
    ScriptVariableIsSet = 51; DoorStatus = 52
    PlayerHasEnergyRegen = 53; QuestHasState = 54
    ObjectiveHasState = 55; HeroHasSkill = 56
    HasTerrainClearance = 57; HeroHasEnergy = 58
    HeroHasBuff = 59; PlayerIsDead = 60
    PlayerIsDrunk = 61; ItemInInventoryList = 62

class ActionType:
    MoveTo = 0; Cast = 2; CastBySlot = 3; DropBuff = 4
    ChangeTarget = 5; UseItem = 6; EquipItem = 7
    RepopMinipet = 8; PingHardMode = 9; PingTarget = 10
    AutoAttackTarget = 11; SendDialog = 12; GoToTarget = 13
    Wait = 14; SendChat = 15; Cancel = 16; Conditioned = 17
    ChangeWeaponSet = 18; StoreTarget = 19; RestoreTarget = 20
    StopScript = 21; LogOut = 22; UseHeroSkill = 23
    UnequipItem = 24; ClearTarget = 25; WaitUntil = 26
    MoveToTargetPosition = 27; MoveInchwise = 28; GWKey = 29
    EquipItemBySlot = 30; EnterCriticalSection = 31
    LeaveCriticalSection = 32; SetVariable = 33
    AbandonQuest = 34; IncrementVariable = 35
    DecrementVariable = 36; MoveItemToSlot = 37
    KeyboardMove = 39; Random = 40; AddHero = 41
    KickHero = 42; LoadSkillbar = 43; DestroyItem = 44
    DropItem = 45; FlagHero = 46; UseItemList = 47

class Sorting:
    AgentId = 0; ClosestToPlayer = 1; FurthestFromPlayer = 2
    ClosestToTarget = 3; FurthestFromTarget = 4
    LowestHp = 5; HighestHp = 6; ModelID = 7

class Channel:
    All = 0; Guild = 1; Team = 2; Trade = 3
    Alliance = 4; Whisper = 5; Emote = 6; Log = 7

class AgentType:
    Any = 0; Self = 1; PartyMember = 2; Friendly = 3; Hostile = 4

class IsIsNot:
    Is_ = 0; IsNot = 1

class ComparisonOperator:
    Equals = 0; Less = 1; Greater = 2
    LessOrEqual = 3; GreaterOrEqual = 4; NotEquals = 5

class HasSkillRequirement:
    OnBar = 0; OffCooldown = 1; ReadyToUse = 2

class SkillID:
    Skills = {
        "No_Skill": 0, "Dark_Aura": 116,
        "Strength_of_Honor": 243,
        "Union": 745, "Shelter": 816,
        "Armor_of_Unfeeling": 1050, "Soul_Twisting": 1058,
        "Displacement": 1067,
        "Summon_Spirits_luxon": 1838, "Summon_Spirits_kurzick": 1887,
        "Drunken_Master": 2001, "Masochism": 2139,
        "Soul_Taker": 3423,
    }

class HeroID:
    Heroes = { "NoHero": 0, "Norgu": 1, "Goren": 2, "Tahlkora": 3,
               "MasterOfWhispers": 4, "AcolyteJin": 5, "Koss": 6,
               "Dunkoro": 7, "AcolyteSousuke": 8, "Melonni": 9,
               "ZhedShadowhoof": 10, "GeneralMorgahn": 11,
               "MargridTheSly": 12, "Zenmai": 13, "Olias": 14,
               "Razah": 15, "MOX": 16, "KeiranThackeray": 17,
               "Jora": 18, "PyreFierceshot": 19, "Anton": 20,
               "Livia": 21, "Hayda": 22, "Kahmu": 23, "Gwen": 24,
               "Xandra": 25, "Vekk": 26, "Ogden": 27 }

class TriggerID:
    Triggers = { "None": 0, "InstanceLoad": 1, "HardModePing": 2,
                 "Hotkey": 3, "ChatMessage": 4 }

# === Serializer ===

class OutputStream:
    def __init__(self):
        self.parts = []

    def write(self, val):
        if isinstance(val, bool):
            val = 1 if val else 0
        self.parts.append(str(val) + " ")
        return self

    def write_string_with_spaces(self, s):
        self.parts.append(s + "< ")
        return self

    def write_separator(self, lvl=1):
        tokens = {1: 0x7F, 2: 0x04, 3: 0x05, 4: 0x06}
        self.parts.append(chr(tokens.get(lvl, 0x7F)))
        return self

    def __str__(self):
        return "".join(self.parts)


# === Huffman encoder (must match SST's io.cpp) ===

def frequent_char_value(c):
    if 'a' <= c <= 'z':
        return ord(c) - ord('a')
    if 'D' <= c <= 'Z':
        return ord(c) - ord('D') + 26
    table = {
        'B': 26+23, '!': 26+24, '"': 26+25, '_': 26+26,
        '#': 26+27, '+': 26+28, '-': 26+29, '=': 26+30,
        '*': 26+31, "'": 26+32, '&': 26+33, '/': 26+34,
        '\x7f': 26+35, '<': 26+36, '>': 26+37,
    }
    return table.get(c, 0xFF)


def huffman_encode(s):
    result = []

    def append(bits):
        result.extend(bits)

    for c in s:
        if c == ' ':
            append([0, 0])
        elif c == '0':
            append([0, 1, 0, 0])
        elif c == '1':
            append([0, 1, 0, 1])
        elif c in '23456789':
            n = int(c) - 2
            bits = [0, 1, 1]
            bits.append((n >> 2) & 1)
            bits.append((n >> 1) & 1)
            bits.append(n & 1)
            append(bits)
        elif c == 'A':
            append([1, 0, 0, 0])
        elif c == 'C':
            append([1, 0, 0, 1])
        elif c == '.':
            append([1, 0, 1, 0])
        else:
            fv = frequent_char_value(c)
            if fv < 64:
                append([1, 1])
                for shift in range(5, -1, -1):
                    append([(fv >> shift) & 1])
            else:
                append([1, 0, 1, 1])
                raw = ord(c)
                for shift in range(7, -1, -1):
                    append([(raw >> shift) & 1])

    while len(result) % 12 != 0:
        result.append(0)

    return result


def bits_to_readable(bits):
    chars = []
    for i in range(0, len(bits), 6):
        val = 0
        for j in range(6):
            if bits[i + j]:
                val |= (1 << (5 - j))
        if val < 26:
            chars.append(chr(ord('a') + val))
        elif val < 52:
            chars.append(chr(ord('A') + val - 26))
        elif val < 62:
            chars.append(chr(ord('0') + val - 52))
        elif val == 62:
            chars.append('_')
        else:
            chars.append('#')
    return ''.join(chars)


def encode_string(s):
    bits = huffman_encode(s)
    return bits_to_readable(bits)


# === .sst parser ===

CURRENT_VERSION = 11

COMPARISON_OPS = {
    ">=": ComparisonOperator.GreaterOrEqual,
    "<=": ComparisonOperator.LessOrEqual,
    "==": ComparisonOperator.Equals,
    "!=": ComparisonOperator.NotEquals,
    ">": ComparisonOperator.Greater,
    "<": ComparisonOperator.Less,
}

def strip_comments(lines):
    result = []
    for line in lines:
        idx = line.find("//")
        if idx >= 0:
            line = line[:idx]
        result.append(line.rstrip())
    return result


def strip_braces(text):
    """Remove outer { } from a block."""
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        text = text[1:-1]
    return text.strip()


def split_top_level(text, sep=","):
    """Split by sep, respecting nested parens."""
    parts = []
    depth = 0
    current = []
    for c in text:
        if c == '(':
            depth += 1
            current.append(c)
        elif c == ')':
            depth -= 1
            current.append(c)
        elif c == sep and depth == 0:
            parts.append(''.join(current).strip())
            current = []
        else:
            current.append(c)
    parts.append(''.join(current).strip())
    return [p for p in parts if p]


def parse_kwargs(text):
    """Parse 'key: val, key: val' into dict."""
    result = {}
    for part in split_top_level(text):
        if ':' in part:
            k, v = part.split(':', 1)
            result[k.strip()] = v.strip()
    return result


def parse_condition(line, sep_level=1):
    """Parse a condition line and return a serializer function."""
    line = line.strip()

    # True_ (always true)
    if line == "True_":
        return lambda s: (
            s.write('C').write(ConditionType.True_),
            s.write_separator(sep_level)
        )

    # not Condition(...)
    m = re.match(r'^not\s+(.+)$', line)
    if m:
        inner = parse_condition(m.group(1), sep_level=3)
        return lambda s: (
            s.write('C').write(ConditionType.Not),
            inner(s),
            s.write_separator()
        )

    # And(Cond1, Cond2, ...)
    m = re.match(r'^And\((.+)\)$', line, re.DOTALL)
    if m:
        inner_text = m.group(1).strip()
        inner_conds = [c.strip() for c in split_top_level(inner_text)]
        inner_fns = [parse_condition(c, sep_level=3) for c in inner_conds]
        def serialize_and(s):
            s.write('C').write(ConditionType.And)
            s.write(len(inner_fns))
            for fn in inner_fns:
                fn(s)
                s.write_separator(2)
            s.write_separator(sep_level)
        return serialize_and

    # Or(Cond1, Cond2, ...)
    m = re.match(r'^Or\((.+)\)$', line, re.DOTALL)
    if m:
        inner_text = m.group(1).strip()
        inner_conds = [c.strip() for c in split_top_level(inner_text)]
        inner_fns = [parse_condition(c, sep_level=3) for c in inner_conds]
        def serialize_or(s):
            s.write('C').write(ConditionType.Or)
            s.write(len(inner_fns))
            for fn in inner_fns:
                fn(s)
                s.write_separator(2)
            s.write_separator(sep_level)
        return serialize_or

    # FoeCount >= N
    m = re.match(r'^FoeCount\s*([><=!]+)\s*(\d+)$', line)
    if m:
        op = COMPARISON_OPS[m.group(1)]
        count = int(m.group(2))
        return lambda s: (
            s.write('C').write(ConditionType.FoeCount),
            s.write(count).write(op),
            s.write_separator(sep_level)
        )

    # PlayerHasBuff(SkillName) - simple form
    m = re.match(r'^PlayerHasBuff\((\w+)\)$', line)
    if m:
        skill_id = SkillID.Skills.get(m.group(1), 0)
        return lambda s: (
            s.write('C').write(ConditionType.PlayerHasBuff),
            s.write(skill_id),
            s.write(0).write(0).write(0).write(0),  # dur params
            s.write_separator(sep_level)
        )

    # PlayerHasBuff(id: SkillName, hasMax: true, maxDuration: N) - full form
    m = re.match(r'^PlayerHasBuff\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        skill_id = SkillID.Skills.get(kwargs.get("id", "No_Skill"), 0)
        min_dur = int(kwargs.get("minDuration", "0"))
        has_min = 1 if kwargs.get("hasMin", "false").lower() == "true" else 0
        max_dur = int(kwargs.get("maxDuration", "0"))
        has_max = 1 if kwargs.get("hasMax", "false").lower() == "true" else 0
        return lambda s: (
            s.write('C').write(ConditionType.PlayerHasBuff),
            s.write(skill_id),
            s.write(min_dur).write(has_min).write(max_dur).write(has_max),
            s.write_separator(sep_level)
        )

    # PlayerHasSkill(skill: X, requirement: Y)
    m = re.match(r'^PlayerHasSkill\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        skill_id = SkillID.Skills.get(kwargs.get("skill", "No_Skill"), 0)
        req_map = {"OnBar": 0, "OffCooldown": 1, "ReadyToUse": 2}
        req = req_map.get(kwargs.get("requirement", "ReadyToUse"), 2)
        return lambda s: (
            s.write('C').write(ConditionType.PlayerHasSkill),
            s.write(skill_id).write(req),
            s.write_separator(sep_level)
        )

    # HeroHasSkill(hero: X, skill: Y, requirement: Z)
    m = re.match(r'^HeroHasSkill\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        hero_id = HeroID.Heroes.get(kwargs.get("hero", "NoHero"), 0)
        skill_id = SkillID.Skills.get(kwargs.get("skill", "No_Skill"), 0)
        req_map = {"OnBar": 0, "OffCooldown": 1, "ReadyToUse": 2}
        req = req_map.get(kwargs.get("requirement", "ReadyToUse"), 2)
        return lambda s: (
            s.write('C').write(ConditionType.HeroHasSkill),
            s.write(hero_id).write(skill_id).write(req),
            s.write_separator(sep_level)
        )

    # PlayerHasEnergy(energy: X, comp: Y)
    m = re.match(r'^PlayerHasEnergy\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        energy = int(kwargs.get("energy", "0"))
        comp = COMPARISON_OPS.get(kwargs.get("comp", ">="), ComparisonOperator.GreaterOrEqual)
        return lambda s: (
            s.write('C').write(ConditionType.PlayerHasEnergy),
            s.write(energy).write(comp),
            s.write_separator(sep_level)
        )

    # HeroHasEnergy(hero: X, energy: Y, comp: Z)
    m = re.match(r'^HeroHasEnergy\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        hero_id = HeroID.Heroes.get(kwargs.get("hero", "NoHero"), 0)
        energy = int(kwargs.get("energy", "0"))
        comp = COMPARISON_OPS.get(kwargs.get("comp", ">="), ComparisonOperator.GreaterOrEqual)
        return lambda s: (
            s.write('C').write(ConditionType.HeroHasEnergy),
            s.write(hero_id).write(energy).write(comp),
            s.write_separator(sep_level)
        )

    # HeroHasBuff(hero: X, skill: Y)
    m = re.match(r'^HeroHasBuff\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        hero_id = HeroID.Heroes.get(kwargs.get("hero", "NoHero"), 0)
        skill_id = SkillID.Skills.get(kwargs.get("skill", "No_Skill"), 0)
        return lambda s: (
            s.write('C').write(ConditionType.HeroHasBuff),
            s.write(hero_id).write(skill_id),
            s.write(0).write(0).write(0).write(0),  # dur params
            s.write_separator(sep_level)
        )

    # Throttle(Nms)
    m = re.match(r'^Throttle\((\d+)ms\)$', line)
    if m:
        delay = int(m.group(1))
        return lambda s: (
            s.write('C').write(ConditionType.Throttle),
            s.write(delay),
            s.write_separator(sep_level)
        )

    # ScriptVariableIsSet(name: X, comp: Is|IsNot)
    m = re.match(r'^ScriptVariableIsSet\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        name = kwargs.get("name", "")
        is_is_not = 0 if kwargs.get("comp", "Is") == "Is" else 1
        return lambda s: (
            s.write('C').write(ConditionType.ScriptVariableIsSet),
            s.write_string_with_spaces(name),
            s.write(is_is_not),
            s.write_separator(sep_level)
        )

    # not ScriptVariableIsSet(name: X, comp: Is|IsNot)
    m = re.match(r'^not\s+ScriptVariableIsSet\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        name = kwargs.get("name", "")
        is_is_not = 0 if kwargs.get("comp", "Is") == "Is" else 1
        inner = lambda s: (
            s.write('C').write(ConditionType.ScriptVariableIsSet),
            s.write_string_with_spaces(name),
            s.write(is_is_not),
            s.write_separator(3)
        )
        def serialize_not_var(s):
            s.write('C').write(ConditionType.Not)
            inner(s)
            s.write_separator(sep_level)
        return serialize_not_var

    # PlayerIsDead
    if line == "PlayerIsDead":
        return lambda s: (
            s.write('C').write(ConditionType.PlayerIsDead),
            s.write_separator(sep_level)
        )

    # PlayerIsDrunk
    if line == "PlayerIsDrunk":
        return lambda s: (
            s.write('C').write(ConditionType.PlayerIsDrunk),
            s.write(0).write(0),  # minLevel=0, hasMinLevel=false
            s.write_separator(sep_level)
        )

    # PlayerIsDrunk(minLevel: N)
    m = re.match(r'^PlayerIsDrunk\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        min_level = int(kwargs.get("minLevel", "1"))
        return lambda s: (
            s.write('C').write(ConditionType.PlayerIsDrunk),
            s.write(min_level).write(1),  # hasMinLevel=true
            s.write_separator(sep_level)
        )

    # ItemInInventoryList(ids: N, M, ...)
    m = re.match(r'^ItemInInventoryList\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        ids_str = kwargs.get("ids", "")
        ids = [int(x.strip()) for x in ids_str.split(',') if x.strip()]
        def serialize_item_list(s):
            s.write('C').write(ConditionType.ItemInInventoryList)
            s.write(len(ids))
            for item_id in ids:
                s.write(item_id)
            s.write_separator(sep_level)
        return serialize_item_list

    # HasTerrainClearance(degree: X, distance: Y)
    m = re.match(r'^HasTerrainClearance\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        degree = float(kwargs.get("degree", "0"))
        distance = float(kwargs.get("distance", "166"))
        return lambda s: (
            s.write('C').write(ConditionType.HasTerrainClearance),
            s.write(degree).write(distance),
            s.write_separator(sep_level)
        )

    # RemainingCooldown(id: X, hasMin: Y, minCooldown: Z, hasMax: W, maxCooldown: V)
    m = re.match(r'^RemainingCooldown\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        skill_id = SkillID.Skills.get(kwargs.get("id", "No_Skill"), 0)
        has_min = 1 if kwargs.get("hasMin", "false").lower() == "true" else 0
        min_cooldown = int(kwargs.get("minCooldown", "0"))
        has_max = 1 if kwargs.get("hasMax", "false").lower() == "true" else 0
        max_cooldown = int(kwargs.get("maxCooldown", "0"))
        return lambda s: (
            s.write('C').write(ConditionType.RemainingCooldown),
            s.write(skill_id),
            s.write(has_min).write(has_max),
            s.write(min_cooldown).write(max_cooldown),
            s.write_separator(sep_level)
        )

    raise ValueError(f"Unknown condition: {line}")


def parse_filter(text):
    """Parse filter: Allegiance(Self) into serializer."""
    text = text.strip()
    m = re.match(r'^Allegiance\((\w+)\)$', text)
    if m:
        agent_type = getattr(AgentType, m.group(1))
        return lambda s: (
            s.write('X').write(11),  # CharacteristicType::Allegiance
            s.write(agent_type).write(IsIsNot.Is_),
            s.write_separator(3)
        )
    raise ValueError(f"Unknown filter: {text}")


def parse_action(line):
    """Parse an action line and return a serializer function."""
    line = line.strip()

    # EnterCriticalSection / LeaveCriticalSection / ClearTarget / Cancel / StopScript / etc.
    simple_actions = {
        "EnterCriticalSection": ActionType.EnterCriticalSection,
        "LeaveCriticalSection": ActionType.LeaveCriticalSection,
        "ClearTarget": ActionType.ClearTarget,
        "Cancel": ActionType.Cancel,
        "StopScript": ActionType.StopScript,
        "PingHardMode": ActionType.PingHardMode,
    }
    if line in simple_actions:
        act = simple_actions[line]
        return lambda s: (s.write('A').write(act), s.write_separator())

    # ChangeTarget(sorting: X, filter: Y)
    m = re.match(r'^ChangeTarget\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        sort_name = kwargs.get("sorting", "AgentId")
        sorting = getattr(Sorting, sort_name)
        filter_fn = parse_filter(kwargs.get("filter", "Any"))
        return lambda s: (
            s.write('A').write(ActionType.ChangeTarget),
            s.write(sorting),
            s.write(0).write(0).write(0),  # booleans
            filter_fn(s),
            s.write_separator()
        )

    # UseHeroSkill(hero: X, skill: Y)
    m = re.match(r'^UseHeroSkill\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        hero_id = HeroID.Heroes.get(kwargs.get("hero", "NoHero"), 0)
        skill_id = SkillID.Skills.get(kwargs.get("skill", "No_Skill"), 0)
        return lambda s: (
            s.write('A').write(ActionType.UseHeroSkill),
            s.write(hero_id).write(skill_id),
            s.write_separator()
        )

    # SendChat(channel: X, message: Y)
    m = re.match(r'^SendChat\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        channel_name = kwargs.get("channel", "All")
        channel = getattr(Channel, channel_name)
        message = kwargs.get("message", "")
        return lambda s: (
            s.write('A').write(ActionType.SendChat),
            s.write(channel),
            s.write_string_with_spaces(message),
            s.write_separator()
        )

    # Cast(skill: X) or Cast(id: X)
    m = re.match(r'^Cast\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        if "skill" in kwargs:
            skill_id = SkillID.Skills.get(kwargs.get("skill", "No_Skill"), 0)
        else:
            skill_id = SkillID.Skills.get(kwargs.get("id", "No_Skill"), 0)
        return lambda s: (
            s.write('A').write(ActionType.Cast),
            s.write(skill_id),
            s.write_separator()
        )

    # Wait(Nms)
    m = re.match(r'^Wait\((\d+)ms\)$', line)
    if m:
        delay = int(m.group(1))
        return lambda s: (
            s.write('A').write(ActionType.Wait),
            s.write(delay),
            s.write_separator()
        )

    # FlagHero(degree: X, distance: Y, hero: Z)
    m = re.match(r'^FlagHero\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        degree = float(kwargs.get("degree", "0"))
        distance = float(kwargs.get("distance", "0"))
        hero = int(kwargs.get("hero", "0"))
        return lambda s: (
            s.write('A').write(ActionType.FlagHero),
            s.write(degree).write(distance).write(hero),
            s.write_separator()
        )

    # SetVariable(name: X, value: Y, preserve: Z)
    m = re.match(r'^SetVariable\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        name = kwargs.get("name", "")
        value = int(kwargs.get("value", "0"))
        preserve = 1 if kwargs.get("preserve", "false").lower() == "true" else 0
        return lambda s: (
            s.write('A').write(ActionType.SetVariable),
            s.write_string_with_spaces(name),
            s.write(value).write(preserve),
            s.write_separator()
        )

    # UseItem(id: X)
    m = re.match(r'^UseItem\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        item_id = int(kwargs.get("id", "0"))
        return lambda s: (
            s.write('A').write(ActionType.UseItem),
            s.write(item_id),
            s.write_separator()
        )

    # UseItemList(ids: N, M, ...)
    m = re.match(r'^UseItemList\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        ids_str = kwargs.get("ids", "")
        ids = [int(x.strip()) for x in ids_str.split(',') if x.strip()]
        def serialize_use_item_list(s):
            s.write('A').write(ActionType.UseItemList)
            s.write(len(ids))
            for item_id in ids:
                s.write(item_id)
            s.write_separator()
        return serialize_use_item_list

    # ChangeWeaponSet(id: N)
    m = re.match(r'^ChangeWeaponSet\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        set_id = int(kwargs.get("id", "1"))
        return lambda s: (
            s.write('A').write(ActionType.ChangeWeaponSet),
            s.write(set_id),
            s.write_separator()
        )

    # StoreTarget(id: N)
    m = re.match(r'^StoreTarget\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        slot_id = int(kwargs.get("id", "1"))
        return lambda s: (
            s.write('A').write(ActionType.StoreTarget),
            s.write(slot_id),
            s.write_separator()
        )

    # RestoreTarget(id: N)
    m = re.match(r'^RestoreTarget\((.+)\)$', line)
    if m:
        kwargs = parse_kwargs(m.group(1))
        slot_id = int(kwargs.get("id", "1"))
        return lambda s: (
            s.write('A').write(ActionType.RestoreTarget),
            s.write(slot_id),
            s.write_separator()
        )

    # Conditioned(cond: ..., then: {...}, else: {...})
    if line.startswith('Conditioned('):
        # Find the matching closing paren
        depth = 1
        pos = len('Conditioned(')
        while pos < len(line) and depth > 0:
            if line[pos] == '(':
                depth += 1
            elif line[pos] == ')':
                depth -= 1
            pos += 1
        inner = line[len('Conditioned('):pos-1]
        return parse_conditioned_block(inner)

    raise ValueError(f"Unknown action: {line}")


def parse_action_sequence(lines):
    """Parse a list of action lines and return a serializer function."""
    # Join multi-line actions first (e.g., nested Conditioned blocks)
    joined_lines = []
    i = 0
    while i < len(lines):
        if lines[i].startswith('Conditioned('):
            # Join until matching closing paren
            joined = lines[i]
            depth = joined.count('(') - joined.count(')')
            i += 1
            while i < len(lines) and depth > 0:
                joined += ' ' + lines[i]
                depth += lines[i].count('(') - lines[i].count(')')
                i += 1
            joined_lines.append(joined)
        else:
            joined_lines.append(lines[i])
            i += 1

    actions = [parse_action(l) for l in joined_lines]
    return lambda s: (
        s.write(len(actions)),
        *[a(s) for a in actions]
    )


def extract_brace_content(text, start_pos):
    """Extract content between matching braces starting at start_pos (after opening brace)."""
    depth = 1
    pos = start_pos
    while pos < len(text) and depth > 0:
        if text[pos] == '{':
            depth += 1
        elif text[pos] == '}':
            depth -= 1
        pos += 1
    if depth != 0:
        return None, pos
    return text[start_pos:pos-1], pos


def parse_conditioned_block(text):
    """Parse the body of a Conditioned(...) block and return a serializer function."""
    cond_fn = None
    then_fn = None
    else_fn = None

    # Extract cond (everything before the first then:)
    m = re.search(r'cond:\s*(.+?)(?:,\s*then:)', text, re.DOTALL)
    if m:
        cond_text = m.group(1).strip()
        cond_fn = parse_condition(cond_text, sep_level=2)
        search_start = m.end()
    else:
        search_start = 0

    # Extract then block (handles nested braces) - search after cond
    m = re.search(r'then:\s*\{', text[search_start:])
    if m:
        then_content, _ = extract_brace_content(text[search_start:], m.end())
        if then_content:
            then_lines = [l.strip() for l in then_content.strip().split('\n') if l.strip()]
            then_fn = parse_action_sequence(then_lines)

    # Extract else block (handles nested braces) - search after then block
    else_search_start = search_start + m.end() + (len(then_content) if m and then_content else 0) if m else search_start
    m = re.search(r'else:\s*\{', text[else_search_start:])
    if m:
        else_content, _ = extract_brace_content(text[else_search_start:], m.end())
        if else_content:
            else_lines = [l.strip() for l in else_content.strip().split('\n') if l.strip()]
            else_fn = parse_action_sequence(else_lines)

    def serialize_conditioned(s):
        s.write('A').write(ActionType.Conditioned)
        if cond_fn:
            cond_fn(s)
        else:
            s.write('C').write(ConditionType.True_)
            s.write_separator(2)
        if then_fn:
            then_fn(s)
        else:
            s.write(0)  # empty action sequence
        if else_fn:
            else_fn(s)
        else:
            s.write(0)  # empty action sequence
        s.write(0)  # no else-if branches
        s.write_separator()

    return serialize_conditioned


def parse_sst_file(filepath):
    """Parse a .sst file and return (name, trigger, options, conditions, actions)."""
    with open(filepath) as f:
        lines = f.readlines()

    lines = strip_comments(lines)
    text = '\n'.join(lines)

    # Extract script name
    m = re.search(r'script\s+"([^"]+)"', text)
    if not m:
        raise ValueError("No script name found")
    name = m.group(1)

    # Extract trigger
    m = re.search(r'trigger:\s*(\w+)', text)
    trigger = TriggerID.Triggers.get(m.group(1) if m else "None", 0)

    # Extract options
    options = {}
    for key in ["canLaunchInParallel", "globallyExclusive", "showMessageWhenTriggered", "showMessageWhenToggled"]:
        m = re.search(rf'{key}:\s*(true|false)', text)
        if m:
            options[key] = m.group(1) == "true"

    # Extract when block
    m = re.search(r'when\s*\{([^}]+)\}', text)
    if not m:
        raise ValueError("No 'when' block found")
    cond_lines = [l.strip() for l in m.group(1).strip().split('\n') if l.strip()]

    # Extract then block - handle nested braces for Conditioned actions
    # Find the then keyword and match braces manually
    then_match = re.search(r'then\s*\{', text)
    if not then_match:
        raise ValueError("No 'then' block found")
    start = then_match.end()
    # Count braces to find matching close
    depth = 1
    pos = start
    while pos < len(text) and depth > 0:
        if text[pos] == '{':
            depth += 1
        elif text[pos] == '}':
            depth -= 1
        pos += 1
    then_body = text[start:pos-1].strip()

    # Parse then block as list of actions
    raw_lines = [l.strip() for l in then_body.split('\n') if l.strip()]
    act_lines = []
    i = 0
    while i < len(raw_lines):
        if raw_lines[i].startswith('Conditioned('):
            joined = raw_lines[i]
            depth = joined.count('(') - joined.count(')')
            i += 1
            while i < len(raw_lines) and depth > 0:
                joined += ' ' + raw_lines[i]
                depth += raw_lines[i].count('(') - raw_lines[i].count(')')
                i += 1
            act_lines.append(joined)
        else:
            act_lines.append(raw_lines[i])
            i += 1
    actions = [parse_action(l) for l in act_lines]

    conditions = [parse_condition(l) for l in cond_lines]

    return name, trigger, options, conditions, actions


def serialize_script(name, trigger, options, conditions, actions):
    """Serialize a parsed script to the SST binary format."""
    stream = OutputStream()

    # Header
    stream.write('S')
    stream.write_string_with_spaces(name)
    stream.write(trigger)
    stream.write(1)  # enabled
    stream.write(0)  # toggleHotkey.keyData
    stream.write(0)  # toggleHotkey.modifier
    stream.write(options.get("showMessageWhenTriggered", False))
    stream.write(options.get("showMessageWhenToggled", False))
    stream.write(options.get("globallyExclusive", False))
    stream.write(options.get("canLaunchInParallel", True))
    stream.write_separator()

    # Conditions
    for cond in conditions:
        cond(stream)

    # Actions
    for act in actions:
        act(stream)

    return str(stream)


def generate_clipboard_import(filepath):
    """Parse .sst file and return clipboard import string."""
    name, trigger, options, conditions, actions = parse_sst_file(filepath)
    raw = serialize_script(name, trigger, options, conditions, actions)
    encoded = encode_string(raw)
    return f"{CURRENT_VERSION} {encoded}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file.sst> [--dry-run]")
        sys.exit(1)

    filepath = sys.argv[1]
    result = generate_clipboard_import(filepath)

    if "--dry-run" in sys.argv:
        print(result)
    else:
        try:
            import subprocess
            subprocess.run(["termux-clipboard-set", result], check=True)
            print("Copied to clipboard! Paste into SST's Import field.")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(result)
            print("\n(termux-clipboard-set not available; copy the string above)")
