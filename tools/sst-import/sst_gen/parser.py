"""Tokenizer and recursive-descent parser for .sst text files.

Parses .sst files into ASTs.  Uses a proper tokenizer (no regex for structure)
and a recursive-descent parser.  Regex is only used for simple token patterns.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterator

from .ast import (
    Action,
    ActionType,
    AfterCondition,
    Condition,
    ConditionType,
    ConditionedAction,
    ConjunctionCondition,
    DisjunctionCondition,
    FalseCondition,
    FoeCountCondition,
    HasCalledTargetCondition,
    HeroHasBuffCondition,
    HeroHasEnergyCondition,
    HeroHasSkillCondition,
    HasTerrainClearanceCondition,
    IsInCombatCondition,
    ItemInInventoryListCondition,
    NegatedCondition,
    OnlyTriggerOnceCondition,
    PlayerAdrenalineCondition,
    PlayerHasBuffCondition,
    PlayerHasCharacteristicsCondition,
    PlayerHasEnergyCondition,
    PlayerHasSkillCondition,
    PlayerIsDrunkCondition,
    RemainingCooldownCondition,
    Script,
    ScriptOptions,
    ThrottleCondition,
    TrueCondition,
    TriggerData,
    Hotkey,
    AllegianceCharacteristic,
    StatusCharacteristic,
    DistanceToPlayerCharacteristic,
    DistanceToTargetCharacteristic,
    DistanceToModelIdCharacteristic,
    PositionCharacteristic,
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
    TrueCharacteristic,
    Characteristic,
)


# === Token types ===


class TT(Enum):
    IDENT = auto()
    NUMBER = auto()
    STRING = auto()
    KEYWORD = auto()
    OP = auto()       # comparison ops: >=, <=, ==, !=, >, <
    LPAREN = auto()   # ( or {
    RPAREN = auto()   # ) or }
    COLON = auto()
    COMMA = auto()
    LBRACKET = auto() # [
    RBRACKET = auto() # ]
    NEWLINE = auto()
    MISC = auto()     # catch-all for chars in values: / ! etc.
    EOF = auto()


KEYWORDS = frozenset({
    "script", "trigger", "when", "then",
    "if", "elif", "else",
    "not", "And", "Or",
    "true", "false",
})

COMPARISON_OP_RE = re.compile(r"^(>=|<=|==|!=|>|<)")


@dataclass
class Token:
    type: TT
    value: str
    line: int
    col: int


# === Comment stripping ===

def _strip_comments(source: str) -> str:
    """Remove // line comments, preserving line structure."""
    result = []
    for line in source.split("\n"):
        in_string = False
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == '"':
                in_string = not in_string
            elif not in_string and ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
                line = line[:i]
                break
            i += 1
        result.append(line.rstrip())
    return "\n".join(result)


# === Tokenizer ===


def tokenize(source: str) -> list[Token]:
    """Tokenize .sst source text into a flat list of tokens.

    Strips comments first. Block structure is determined by {}/() delimiters.
    Characters that appear inside kwarg values (e.g. /, !) are tokenized as MISC.
    """
    source = _strip_comments(source)
    tokens: list[Token] = []
    line_num = 1
    pos = 0
    length = len(source)

    while pos < length:
        ch = source[pos]

        # --- Newline ---
        if ch == "\n":
            tokens.append(Token(TT.NEWLINE, "\\n", line_num, 1))
            pos += 1
            line_num += 1
            continue

        # --- Whitespace: skip ---
        if ch in (" ", "\t", "\r"):
            pos += 1
            continue

        col = pos + 1  # 1-indexed

        # --- String literal ---
        if ch == '"':
            pos += 1
            start = pos
            while pos < length and source[pos] != '"':
                if source[pos] == "\n":
                    raise SyntaxError(f"Line {line_num}: unterminated string")
                pos += 1
            if pos >= length:
                raise SyntaxError(f"Line {line_num}: unterminated string")
            tokens.append(Token(TT.STRING, source[start:pos], line_num, col))
            pos += 1
            continue

        # --- Parentheses and braces ---
        if ch in ("(", "{"):
            tokens.append(Token(TT.LPAREN, ch, line_num, col))
            pos += 1
            continue
        if ch in (")", "}"):
            tokens.append(Token(TT.RPAREN, ch, line_num, col))
            pos += 1
            continue

        # --- Brackets ---
        if ch == "[":
            tokens.append(Token(TT.LBRACKET, "[", line_num, col))
            pos += 1
            continue
        if ch == "]":
            tokens.append(Token(TT.RBRACKET, "]", line_num, col))
            pos += 1
            continue

        # --- Colon ---
        if ch == ":":
            tokens.append(Token(TT.COLON, ":", line_num, col))
            pos += 1
            continue

        # --- Comma ---
        if ch == ",":
            tokens.append(Token(TT.COMMA, ",", line_num, col))
            pos += 1
            continue

        # --- Comparison operators (must check before single < >) ---
        m = COMPARISON_OP_RE.match(source[pos:])
        if m:
            tokens.append(Token(TT.OP, m.group(1), line_num, col))
            pos += len(m.group(1))
            continue

        # --- Number (integer or float) ---
        if ch.isdigit() or (ch == "." and pos + 1 < length and source[pos + 1].isdigit()):
            start = pos
            if ch == ".":
                pos += 1
            while pos < length and source[pos].isdigit():
                pos += 1
            if pos < length and source[pos] == "." and pos + 1 < length and source[pos + 1].isdigit():
                pos += 1
                while pos < length and source[pos].isdigit():
                    pos += 1
            # Consume optional unit suffix (e.g. "ms")
            while pos < length and source[pos].isalpha():
                pos += 1
            tokens.append(Token(TT.NUMBER, source[start:pos], line_num, col))
            continue

        # --- Identifier or keyword ---
        if ch.isalpha() or ch == "_":
            start = pos
            while pos < length and (source[pos].isalnum() or source[pos] == "_"):
                pos += 1
            word = source[start:pos]
            if word in KEYWORDS:
                tokens.append(Token(TT.KEYWORD, word, line_num, col))
            else:
                tokens.append(Token(TT.IDENT, word, line_num, col))
            continue

        # --- Catch-all for characters that can appear in kwarg values ---
        # / ! @ # $ % ^ & * ~ ` etc.
        tokens.append(Token(TT.MISC, ch, line_num, col))
        pos += 1
        continue

    tokens.append(Token(TT.EOF, "", line_num, 1))
    return tokens


# === Helpers ===

COMPARISON_OPS = {
    ">=": 4,  # ComparisonOperator.GreaterOrEqual
    "<=": 3,  # ComparisonOperator.LessOrEqual
    "==": 0,  # ComparisonOperator.Equals
    "!=": 5,  # ComparisonOperator.NotEquals
    ">":  2,  # ComparisonOperator.Greater
    "<":  1,  # ComparisonOperator.Less
}


def _resolve_skill(name: str) -> int:
    """Resolve a skill name to its numeric ID.

    Falls back to interpreting ``name`` as a plain integer so that scripts
    can use ``Cast(id: 2218)`` directly when a name isn't in the mapping.
    """
    from .constants_generated import SKILL_IDS

    val = SKILL_IDS.get(name)
    if val is not None:
        return val
    try:
        return int(name)
    except ValueError:
        return 0


def _resolve_hero(name: str) -> int:
    """Resolve a hero name to its numeric ID."""
    from .constants_generated import HERO_IDS

    val = HERO_IDS.get(name)
    if val is not None:
        return val
    try:
        return int(name)
    except ValueError:
        return 0


def _resolve_trigger(name: str) -> int:
    TRIGGERS = {
        "None": 0, "InstanceLoad": 1, "HardModePing": 2,
        "Hotkey": 3, "ChatMessage": 4, "BeginSkillCast": 5,
        "BeginCooldown": 6, "SkillCastInterrupt": 7,
        "DisplayDialog": 8, "DungeonReward": 9, "DoaZoneComplete": 10,
    }
    return TRIGGERS.get(name, 0)


def _parse_number_value(raw: str) -> int | float:
    """Parse a number token, stripping optional unit suffix like 'ms'."""
    s = re.sub(r"[a-zA-Z]+$", "", raw)
    if not s:
        return 0
    if "." in s:
        return float(s)
    return int(s)


def _resolve_comparison(raw: str) -> int:
    """Resolve a comparison name (e.g. 'GreaterOrEqual') or op (e.g. '>=') to enum int."""
    NAME_MAP = {
        "Equals": 0, "Less": 1, "Greater": 2,
        "LessOrEqual": 3, "GreaterOrEqual": 4, "NotEquals": 5,
    }
    if raw in NAME_MAP:
        return NAME_MAP[raw]
    return COMPARISON_OPS.get(raw, 4)


# === Condition dispatch ===

CONDITION_MAP: dict[str, tuple[int, callable]] = {
    "True_": (38, lambda kw: TrueCondition()),
    "False_": (37, lambda kw: FalseCondition()),
    "FoeCount": (35, lambda kw: FoeCountCondition(
        count=kw.get("count", kw.get("0", 0)),
        comparison=_resolve_comparison(kw.get("comp", ">=")),
    )),
    "PlayerHasBuff": (13, lambda kw: PlayerHasBuffCondition(
        skill_id=_resolve_skill(kw.get("skill", kw.get("id", kw.get("0", "No_Skill")))),
        has_min_duration=kw.get("hasMin", "false").lower() == "true",
        min_duration=_parse_number_value(kw.get("minDuration", "0")),
        has_max_duration=kw.get("hasMax", "false").lower() == "true",
        max_duration=_parse_number_value(kw.get("maxDuration", "0")),
    )),
    "PlayerHasSkill": (14, lambda kw: PlayerHasSkillCondition(
        skill_id=_resolve_skill(kw.get("skill", kw.get("0", "No_Skill"))),
        requirement={"OnBar": 0, "OffCooldown": 1, "ReadyToUse": 2}.get(
            kw.get("requirement", "ReadyToUse"), 2
        ),
    )),
    "HeroHasSkill": (56, lambda kw: HeroHasSkillCondition(
        hero_id=_resolve_hero(kw.get("hero", "NoHero")),
        skill_id=_resolve_skill(kw.get("skill", kw.get("0", "No_Skill"))),
        requirement={"OnBar": 0, "OffCooldown": 1, "ReadyToUse": 2}.get(
            kw.get("requirement", "ReadyToUse"), 2
        ),
    )),
    "Throttle": (44, lambda kw: ThrottleCondition(
        delay_ms=_parse_number_value(kw.get("ms", kw.get("0", "100"))),
    )),
    "PlayerIsDrunk": (61, lambda kw: PlayerIsDrunkCondition(
        min_level=_parse_number_value(kw.get("minLevel", "1")),
        has_min_level=kw.get("hasMinLevel", "false").lower() == "true",
    )),
    "ItemInInventoryList": (62, lambda kw: ItemInInventoryListCondition(
        ids=[int(x.strip()) for x in kw.get("ids", kw.get("0", "")).split(",") if x.strip()],
    )),
    "HasTerrainClearance": (57, lambda kw: HasTerrainClearanceCondition(
        degree=_parse_number_value(kw.get("degree", "0")),
        distance=_parse_number_value(kw.get("distance", "166")),
    )),
    "ScriptVariableIsSet": (51, lambda kw: None),
    "PlayerHasEnergy": (17, lambda kw: PlayerHasEnergyCondition(
        energy=_parse_number_value(kw.get("energy", "0")),
        comparison=_resolve_comparison(kw.get("comp", ">=")),
    )),
    "RemainingCooldown": (34, lambda kw: RemainingCooldownCondition(
        skill_id=_resolve_skill(kw.get("id", kw.get("0", "No_Skill"))),
        has_min=kw.get("hasMin", "false").lower() == "true",
        min_cooldown=_parse_number_value(kw.get("minCooldown", "0")),
        has_max=kw.get("hasMax", "false").lower() == "true",
        max_cooldown=_parse_number_value(kw.get("maxCooldown", "1000")),
    )),
    "PlayerAdrenaline": (63, lambda kw: PlayerAdrenalineCondition(
        skill_id=_resolve_skill(kw.get("skill", kw.get("0", "No_Skill"))),
        adrenaline=_parse_number_value(kw.get("adrenaline", "0")),
        comparison=_resolve_comparison(kw.get("comp", ">=")),
    )),
    "OnlyTriggerOncePerInstance": (10, lambda kw: OnlyTriggerOnceCondition()),
    "HasCalledTarget": (64, lambda kw: HasCalledTargetCondition()),
    "IsInCombat": (48, lambda kw: IsInCombatCondition(
        range=_parse_number_value(kw.get("range", "1012")),
    )),
}


# === Action dispatch ===

ACTION_MAP: dict[str, int] = {
    "Wait": 14,
    "Cast": 2,
    "EnterCriticalSection": 31,
    "LeaveCriticalSection": 32,
    "ClearTarget": 25,
    "Cancel": 16,
    "StopScript": 21,
    "PingHardMode": 9,
    "ChangeTarget": 5,
    "UseHeroSkill": 23,
    "SendChat": 15,
    "FlagHero": 46,
    "SetVariable": 33,
    "StoreTarget": 19,
    "RestoreTarget": 20,
    "ChangeWeaponSet": 18,
    "UseItem": 6,
    "UseItemList": 47,
}


# === Parser ===


class Parser:
    """Recursive-descent parser for .sst tokens."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, tt: TT, value: str | None = None) -> Token:
        tok = self.peek()
        if tok.type != tt:
            raise SyntaxError(
                f"Line {tok.line}: expected {tt.name}, got {tok.type.name} ({tok.value!r})"
            )
        if value is not None and tok.value != value:
            raise SyntaxError(
                f"Line {tok.line}: expected {value!r}, got {tok.value!r}"
            )
        return self.advance()

    def match(self, tt: TT, value: str | None = None) -> Token | None:
        tok = self.peek()
        if tok.type != tt:
            return None
        if value is not None and tok.value != value:
            return None
        return self.advance()

    def skip_newlines(self) -> None:
        while self.peek().type == TT.NEWLINE:
            self.advance()

    # --- Top-level ---

    def parse_script(self) -> Script:
        """Parse: script "Name" { header when { ... } then { ... } }"""
        self.skip_newlines()
        self.expect(TT.KEYWORD, "script")
        name_tok = self.expect(TT.STRING)
        self.expect(TT.LPAREN)  # '{'

        script = Script(name=name_tok.value)

        # Parse header (trigger, options)
        self._parse_header(script)

        # Parse when block: "when" "{"
        self.expect(TT.KEYWORD, "when")
        self.expect(TT.LPAREN)  # '{'
        script.conditions = self._parse_when_body()
        self.expect(TT.RPAREN)  # '}'

        # Skip newlines between when and then
        self.skip_newlines()

        # Parse then block: "then" "{"
        self.expect(TT.KEYWORD, "then")
        self.expect(TT.LPAREN)  # '{'
        script.actions = self._parse_then_body()
        self.expect(TT.RPAREN)  # '}'

        return script

    def _parse_header(self, script: Script) -> None:
        """Parse optional trigger and option lines before when/then."""
        while True:
            self.skip_newlines()
            tok = self.peek()
            if tok.type != TT.IDENT and tok.type != TT.KEYWORD:
                break
            # trigger: Value
            if tok.value == "trigger":
                self.advance()
                self.expect(TT.COLON)
                val = self.advance()
                if val.type in (TT.IDENT, TT.KEYWORD):
                    script.trigger = _resolve_trigger(val.value)
            # option: true/false
            elif tok.type == TT.IDENT:
                key = self.advance().value
                self.expect(TT.COLON)
                val = self.advance()
                if val.type == TT.KEYWORD and val.value in ("true", "false"):
                    bval = val.value == "true"
                elif val.type == TT.IDENT and val.value in ("true", "false"):
                    bval = val.value == "true"
                else:
                    raise SyntaxError(
                        f"Line {val.line}: expected true/false, got {val.value!r}"
                    )
                if key == "canLaunchInParallel":
                    script.options.can_launch_in_parallel = bval
                elif key == "globallyExclusive":
                    script.options.globally_exclusive = bval
                elif key == "showMessageWhenTriggered":
                    script.options.show_message_when_triggered = bval
                elif key == "showMessageWhenToggled":
                    script.options.show_message_when_toggled = bval
            else:
                break

    def _parse_when_body(self) -> list[Condition]:
        """Parse condition lines inside a when { ... } block."""
        conditions: list[Condition] = []
        while True:
            self.skip_newlines()
            if self.peek().type == TT.RPAREN:
                break
            conditions.append(self.parse_condition())
        return conditions

    def _parse_then_body(self) -> list[Action]:
        """Parse action lines inside a then { ... } block."""
        actions: list[Action] = []
        while True:
            self.skip_newlines()
            if self.peek().type == TT.RPAREN:
                break
            actions.append(self.parse_action())
        return actions

    # --- Condition parsing ---

    def parse_condition(self) -> Condition:
        """Parse a single condition expression."""
        # not Condition
        if self.peek().type == TT.KEYWORD and self.peek().value == "not":
            self.advance()
            inner = self.parse_condition()
            return NegatedCondition(cond=inner)

        # Or(Cond, Cond, ...)
        if self.peek().type == TT.KEYWORD and self.peek().value == "Or":
            self.advance()
            self.expect(TT.LPAREN)
            conds = self._parse_condition_list()
            self.skip_newlines()
            self.expect(TT.RPAREN)
            return DisjunctionCondition(conditions=conds)

        # And(Cond, Cond, ...)
        if self.peek().type == TT.KEYWORD and self.peek().value == "And":
            self.advance()
            self.expect(TT.LPAREN)
            conds = self._parse_condition_list()
            self.skip_newlines()
            self.expect(TT.RPAREN)
            return ConjunctionCondition(conditions=conds)

        # True_ / False_
        if self.peek().type == TT.KEYWORD and self.peek().value == "True_":
            self.advance()
            return TrueCondition()
        if self.peek().type == TT.KEYWORD and self.peek().value == "False_":
            self.advance()
            return FalseCondition()

        # Type(args) or Type >= N
        if self.peek().type == TT.IDENT:
            name = self.advance().value

            # Check for comparison: Name >= Number
            if self.peek().type == TT.OP:
                op_tok = self.advance()
                num_tok = self.expect(TT.NUMBER)
                return self._make_comparison_condition(name, op_tok.value, num_tok.value)

            # Check for parentheses: Name(...)
            if self.peek().type == TT.LPAREN:
                self.advance()
                # Special handling for conditions that take a characteristic argument
                if name == "PlayerHasCharacteristics":
                    char = self.parse_characteristic()
                    self.expect(TT.RPAREN)
                    return PlayerHasCharacteristicsCondition(characteristic=char)
                kw = self._parse_kwargs()
                self.expect(TT.RPAREN)
                return self._make_condition(name, kw)

            # Bare keyword like Throttle or PlayerIsDrunk (no parens)
            if name == "PlayerIsDrunk":
                return PlayerIsDrunkCondition()
            if name == "IsInCombat":
                return IsInCombatCondition()
            if name == "HasCalledTarget":
                return HasCalledTargetCondition()
            if name == "OnlyTriggerOncePerInstance":
                return OnlyTriggerOnceCondition()
            if name == "True_":
                return TrueCondition()
            if name == "False_":
                return FalseCondition()

            raise SyntaxError(
                f"Line {self.peek().line}: unexpected identifier {name!r} in condition"
            )

        tok = self.peek()
        raise SyntaxError(
            f"Line {tok.line}: expected condition, got {tok.type.name} ({tok.value!r})"
        )

    def _make_comparison_condition(
        self, name: str, op: str, num_raw: str
    ) -> Condition:
        """Build a condition from Name op Number (e.g. FoeCount >= 1)."""
        num = _parse_number_value(num_raw)
        comp = _resolve_comparison(op)

        if name == "FoeCount":
            return FoeCountCondition(count=int(num), comparison=comp)

        if name == "PlayerHasEnergy":
            return PlayerHasEnergyCondition(energy=int(num), comparison=comp)

        from .ast import (
            PlayerMoraleCondition,
            InstanceTimeCondition,
            InstanceProgressCondition,
            PartyPlayerCountCondition,
        )

        if name == "PlayerMorale":
            return PlayerMoraleCondition(morale=int(num), comparison=comp)
        if name == "InstanceTime":
            return InstanceTimeCondition(time_seconds=int(num), comparison=comp)
        if name == "InstanceProgress":
            return InstanceProgressCondition(required_progress=float(num), comparison=comp)
        if name == "PartyPlayerCount":
            return PartyPlayerCountCondition(count=int(num), comparison=comp)

        raise SyntaxError(f"Unknown condition with comparison: {name} {op} {num}")

    def _make_condition(self, name: str, kw: dict[str, str]) -> Condition:
        """Build a condition from Name(kwargs)."""
        if name in CONDITION_MAP:
            _, ctor = CONDITION_MAP[name]
            return ctor(kw)

        if name == "PlayerIsDrunk":
            return PlayerIsDrunkCondition()

        raise SyntaxError(f"Unknown condition type: {name}")

    def _parse_condition_list(self) -> list[Condition]:
        """Parse comma-separated condition expressions."""
        conds: list[Condition] = []
        self.skip_newlines()
        conds.append(self.parse_condition())
        while self.match(TT.COMMA):
            self.skip_newlines()
            conds.append(self.parse_condition())
        return conds

    # --- Characteristic parsing ---

    def parse_characteristic(self) -> Characteristic:
        """Parse a single characteristic expression."""
        from .ast import (
            NegationCharacteristic,
            ConjunctionCharacteristic,
            DisjunctionCharacteristic,
        )

        # not Characteristic
        if self.peek().type == TT.KEYWORD and self.peek().value == "not":
            self.advance()
            inner = self.parse_characteristic()
            return NegationCharacteristic(characteristic=inner)

        # Or(Characteristic, Characteristic, ...)
        if self.peek().type == TT.KEYWORD and self.peek().value == "Or":
            self.advance()
            self.expect(TT.LPAREN)
            chars = self._parse_characteristic_list()
            self.skip_newlines()
            self.expect(TT.RPAREN)
            return DisjunctionCharacteristic(characteristics=chars)

        # And(Characteristic, Characteristic, ...)
        if self.peek().type == TT.KEYWORD and self.peek().value == "And":
            self.advance()
            self.expect(TT.LPAREN)
            chars = self._parse_characteristic_list()
            self.skip_newlines()
            self.expect(TT.RPAREN)
            return ConjunctionCharacteristic(characteristics=chars)

        # Type(args)
        if self.peek().type == TT.IDENT:
            name = self.advance().value
            if self.peek().type == TT.LPAREN:
                self.advance()
                kw = self._parse_kwargs()
                self.expect(TT.RPAREN)
                return self._make_characteristic(name, kw)

            raise SyntaxError(
                f"Line {self.peek().line}: expected characteristic with args, got {self.peek().type.name} ({self.peek().value!r})"
            )

        tok = self.peek()
        raise SyntaxError(
            f"Line {tok.line}: expected characteristic, got {tok.type.name} ({tok.value!r})"
        )

    def _parse_characteristic_list(self) -> list[Characteristic]:
        """Parse comma-separated characteristic expressions."""
        chars: list[Characteristic] = []
        self.skip_newlines()
        chars.append(self.parse_characteristic())
        while self.match(TT.COMMA):
            self.skip_newlines()
            chars.append(self.parse_characteristic())
        return chars

    def _make_characteristic(self, name: str, kw: dict[str, str]) -> Characteristic:
        """Build a characteristic from Name(kwargs)."""
        from .ast import AgentType, IsIsNot, Status, SkillType, Class, WeaponType, IdRestriction

        if name == "Allegiance":
            return AllegianceCharacteristic(
                agent_type=getattr(AgentType, kw.get("agentType", kw.get("0", "Any")), 0),
                comparison=getattr(IsIsNot, kw.get("comp", "Is_"), 0),
            )
        if name == "Status":
            return StatusCharacteristic(
                status=getattr(Status, kw.get("status", kw.get("0", "Alive")), 2),
                comparison=getattr(IsIsNot, kw.get("comp", "Is_"), 0),
                skill_type=getattr(SkillType, kw.get("skillType", "Any"), 0),
            )
        if name == "DistanceToPlayer":
            return DistanceToPlayerCharacteristic(
                value=_parse_number_value(kw.get("distance", kw.get("0", "166"))),
                comparison=_resolve_comparison(kw.get("comp", "<=")),
            )
        if name == "DistanceToTarget":
            return DistanceToTargetCharacteristic(
                value=_parse_number_value(kw.get("distance", kw.get("0", "166"))),
                comparison=_resolve_comparison(kw.get("comp", "<=")),
            )
        if name == "DistanceToModelId":
            return DistanceToModelIdCharacteristic(
                model_id=int(kw.get("modelId", kw.get("0", "0"))),
                value=_parse_number_value(kw.get("distance", kw.get("1", "166"))),
                comparison=_resolve_comparison(kw.get("comp", "<=")),
            )
        if name == "Position":
            return PositionCharacteristic(
                x=_parse_number_value(kw.get("x", kw.get("0", "0"))),
                y=_parse_number_value(kw.get("y", kw.get("1", "0"))),
                accuracy=_parse_number_value(kw.get("distance", kw.get("2", "166"))),
                comparison=_resolve_comparison(kw.get("comp", "<=")),
            )
        if name == "HP":
            return HPCharacteristic(
                hp=_parse_number_value(kw.get("hp", kw.get("0", "50"))),
                comparison=_resolve_comparison(kw.get("comp", "<=")),
            )
        if name == "HPRegen":
            return HPRegenCharacteristic(
                regen=int(_parse_number_value(kw.get("hpRegen", kw.get("0", "0")))),
                comparison=_resolve_comparison(kw.get("comp", ">")),
            )
        if name == "Speed":
            return SpeedCharacteristic(
                speed=_parse_number_value(kw.get("speed", kw.get("0", "0"))),
                comparison=_resolve_comparison(kw.get("comp", ">=")),
            )
        if name == "Class":
            return ClassCharacteristic(
                primary=getattr(Class, kw.get("primary", kw.get("0", "Any")), 0),
                secondary=getattr(Class, kw.get("secondary", kw.get("1", "Any")), 0),
                comparison=getattr(IsIsNot, kw.get("comp", "Is_"), 0),
            )
        if name == "Name":
            return NameCharacteristic(
                name=kw.get("name", kw.get("0", "")),
                comparison=getattr(IsIsNot, kw.get("comp", "Is_"), 0),
            )
        if name == "Model":
            return ModelCharacteristic(
                model_id=int(kw.get("modelId", kw.get("0", "0"))),
                comparison=getattr(IsIsNot, kw.get("comp", "Is_"), 0),
            )
        if name == "WeaponType":
            return WeaponTypeCharacteristic(
                weapon_type=getattr(WeaponType, kw.get("weapon", kw.get("0", "Any")), 0),
                comparison=getattr(IsIsNot, kw.get("comp", "Is_"), 0),
            )
        if name == "Skill":
            return SkillCharacteristic(
                skill_id=_resolve_skill(kw.get("skill", kw.get("0", "No_Skill"))),
                comparison=getattr(IsIsNot, kw.get("comp", "Is_"), 0),
            )
        if name == "Bond":
            return BondCharacteristic(
                bond=_resolve_skill(kw.get("skill", kw.get("0", "No_Skill"))),
                comparison=getattr(IsIsNot, kw.get("comp", "Is_"), 0),
            )
        if name == "AngleToPlayerForward":
            return AngleToPlayerForwardCharacteristic(
                angle=_parse_number_value(kw.get("angle", kw.get("0", "180"))),
                comparison=_resolve_comparison(kw.get("comp", "<=")),
            )
        if name == "AngleToCameraForward":
            return AngleToCameraForwardCharacteristic(
                angle=_parse_number_value(kw.get("angle", kw.get("0", "180"))),
                comparison=_resolve_comparison(kw.get("comp", "<=")),
            )
        if name == "IsStoredTarget":
            return IsStoredTargetCharacteristic(
                slot=int(_parse_number_value(kw.get("slot", kw.get("0", "0")))),
                comparison=getattr(IsIsNot, kw.get("comp", "Is_"), 0),
                id_restriction=getattr(IdRestriction, kw.get("idRestriction", "Any"), 0),
            )
        raise SyntaxError(f"Unknown characteristic type: {name}")

    # --- Action parsing ---

    def parse_action(self) -> Action:
        """Parse a single action line."""
        # if block
        if self.peek().type == TT.KEYWORD and self.peek().value == "if":
            return self._parse_if_block()

        # Conditioned(cond: ..., then: {...}, else: {...})
        if self.peek().type == TT.IDENT and self.peek().value == "Conditioned":
            return self._parse_conditioned_action()

        # Simple action: Name or Name(args)
        return self._parse_simple_action()

    def _parse_if_block(self) -> ConditionedAction:
        """Parse if/elif/else block into a ConditionedAction."""
        self.expect(TT.KEYWORD, "if")
        cond = self.parse_condition()
        self.expect(TT.COLON)
        self.skip_newlines()
        self.expect(TT.LPAREN)  # '{'
        then_actions = self._parse_action_list()
        self.expect(TT.RPAREN)  # '}'

        else_ifs: list[tuple[Condition, list[Action]]] = []
        while self.peek().type == TT.KEYWORD and self.peek().value == "elif":
            self.advance()
            ei_cond = self.parse_condition()
            self.expect(TT.COLON)
            self.skip_newlines()
            self.expect(TT.LPAREN)
            ei_actions = self._parse_action_list()
            self.expect(TT.RPAREN)
            else_ifs.append((ei_cond, ei_actions))

        else_actions: list[Action] = []
        if self.peek().type == TT.KEYWORD and self.peek().value == "else":
            self.advance()
            self.expect(TT.COLON)
            self.skip_newlines()
            self.expect(TT.LPAREN)
            else_actions = self._parse_action_list()
            self.expect(TT.RPAREN)

        return ConditionedAction(
            condition=cond,
            actions_if=then_actions,
            actions_else=else_actions,
            actions_else_if=else_ifs,
        )

    def _parse_conditioned_action(self) -> ConditionedAction:
        """Parse Conditioned(cond: ..., then: {...}, else: {...})"""
        self.expect(TT.IDENT, "Conditioned")
        self.expect(TT.LPAREN)

        cond: Condition = TrueCondition()
        then_actions: list[Action] = []
        else_actions: list[Action] = []

        while True:
            self.skip_newlines()
            if self.peek().type == TT.RPAREN:
                break

            # Accept both IDENT and KEYWORD for keys (then/else are keywords)
            tok = self.peek()
            if tok.type == TT.IDENT:
                key = self.advance().value
            elif tok.type == TT.KEYWORD and tok.value in ("then", "else", "cond"):
                key = self.advance().value
            else:
                raise SyntaxError(
                    f"Line {tok.line}: expected key (cond/then/else), got {tok.type.name} ({tok.value!r})"
                )

            self.expect(TT.COLON)

            if key == "cond":
                cond = self.parse_condition()
            elif key == "then":
                self.expect(TT.LPAREN)  # '{'
                then_actions = self._parse_action_list()
                self.expect(TT.RPAREN)  # '}'
            elif key == "else":
                self.expect(TT.LPAREN)  # '{'
                else_actions = self._parse_action_list()
                self.expect(TT.RPAREN)  # '}'
            else:
                raise SyntaxError(
                    f"Line {self.peek().line}: unexpected key {key!r} in Conditioned"
                )

            # Skip comma separator if present
            self.match(TT.COMMA)

        self.expect(TT.RPAREN)

        return ConditionedAction(
            condition=cond,
            actions_if=then_actions,
            actions_else=else_actions,
        )

    def _parse_action_list(self) -> list[Action]:
        """Parse action lines inside a { ... } block."""
        actions: list[Action] = []
        while True:
            self.skip_newlines()
            if self.peek().type == TT.RPAREN:
                break
            actions.append(self.parse_action())
        return actions

    def _parse_simple_action(self) -> Action:
        """Parse Name or Name(args)."""
        name = self.expect(TT.IDENT).value

        # No-arg actions
        if self.peek().type != TT.LPAREN:
            return self._make_action(name, {})

        self.advance()  # '('
        kw = self._parse_kwargs()
        self.expect(TT.RPAREN)
        return self._make_action(name, kw)

    def _make_action(self, name: str, kw: dict[str, str]) -> Action:
        """Build an action AST node from name and kwargs."""
        if name == "EnterCriticalSection":
            from .ast import EnterCriticalSectionAction
            return EnterCriticalSectionAction()
        if name == "LeaveCriticalSection":
            from .ast import LeaveCriticalSectionAction
            return LeaveCriticalSectionAction()
        if name == "ClearTarget":
            from .ast import ClearTargetAction
            return ClearTargetAction()
        if name == "Cancel":
            from .ast import CancelAction
            return CancelAction()
        if name == "StopScript":
            from .ast import StopScriptAction
            return StopScriptAction()
        if name == "PingHardMode":
            from .ast import PingHardModeAction
            return PingHardModeAction()
        if name == "Wait":
            from .ast import WaitAction
            ms_val = list(kw.values())[0] if kw else "1000"
            return WaitAction(ms=_parse_number_value(ms_val))
        if name == "Cast":
            from .ast import CastAction
            skill_id = _resolve_skill(kw.get("skill", kw.get("id", "No_Skill")))
            return CastAction(skill_id=skill_id)
        if name == "ChangeTarget":
            from .ast import ChangeTargetAction, Sorting, AgentType, IsIsNot
            sorting_name = kw.get("sorting", "AgentId")
            sorting_val = getattr(Sorting, sorting_name, 0)
            filter_str = kw.get("filter", "Any")
            m = re.match(r"Allegiance\((\w+)\)", filter_str)
            if m:
                agent_type = getattr(AgentType, m.group(1), 0)
                char = AllegianceCharacteristic(
                    agent_type=agent_type, comparison=IsIsNot.Is_
                )
            else:
                char = TrueCharacteristic()
            return ChangeTargetAction(
                sorting=sorting_val,
                characteristics=[char],
            )
        if name == "UseHeroSkill":
            from .ast import UseHeroSkillAction
            return UseHeroSkillAction(
                hero_id=_resolve_hero(kw.get("hero", "NoHero")),
                skill_id=_resolve_skill(kw.get("skill", "No_Skill")),
            )
        if name == "SendChat":
            from .ast import SendChatAction, Channel
            channel_name = kw.get("channel", "All")
            channel_val = getattr(Channel, channel_name, 0)
            return SendChatAction(
                channel=channel_val,
                message=kw.get("message", ""),
            )
        if name == "FlagHero":
            from .ast import FlagHeroAction
            return FlagHeroAction(
                hero=_parse_number_value(kw.get("hero", "0")),
                degree=_parse_number_value(kw.get("degree", "0")),
                distance=_parse_number_value(kw.get("distance", "0")),
            )
        if name == "StoreTarget":
            from .ast import StoreTargetAction
            return StoreTargetAction(id=_parse_number_value(kw.get("id", "0")))
        if name == "RestoreTarget":
            from .ast import RestoreTargetAction
            return RestoreTargetAction(id=_parse_number_value(kw.get("id", "0")))
        if name == "ChangeWeaponSet":
            from .ast import ChangeWeaponSetAction
            return ChangeWeaponSetAction(id=_parse_number_value(kw.get("id", "1")))
        if name == "UseItem":
            from .ast import UseItemAction
            return UseItemAction(id=_parse_number_value(kw.get("id", "0")))
        if name == "UseItemList":
            from .ast import UseItemListAction
            ids = [int(x.strip()) for x in kw.get("ids", "").split(",") if x.strip()]
            return UseItemListAction(ids=ids)
        if name == "SetVariable":
            from .ast import SetVariableAction
            return SetVariableAction(
                name=kw.get("name", ""),
                value=_parse_number_value(kw.get("value", "0")),
                preserve=kw.get("preserve", "false").lower() == "true",
            )

        raise SyntaxError(f"Unknown action: {name}")

    # --- Kwargs ---

    def _parse_kwargs(self) -> dict[str, str]:
        """Parse 'key: val, key: val' or positional args like '100ms' into a dict.

        Positional args are stored with numeric string keys ('0', '1', ...).
        Values can contain arbitrary tokens (MISC, brackets, etc.)
        and extend until the next comma or closing paren.
        """
        kw: dict[str, str] = {}
        pos_idx = 0
        self.skip_newlines()
        while self.peek().type != TT.RPAREN:
            if self.peek().type == TT.COMMA:
                self.advance()
                self.skip_newlines()
                continue
            # Check if this is a keyword: value pair or a positional arg
            if self.peek().type == TT.IDENT:
                # Peek ahead to see if IDENT is followed by COLON
                saved = self.pos
                self.advance()  # consume IDENT
                if self.peek().type == TT.COLON:
                    # keyword: value pair
                    key = self.tokens[saved].value
                    self.advance()  # skip colon
                    val = self._parse_raw_value()
                    kw[key] = val
                else:
                    # Not a kwarg — this is a positional IDENT arg
                    # (e.g. PlayerHasBuff(Strength_of_Honor))
                    self.pos = saved
                    val = self._parse_raw_value()
                    kw[str(pos_idx)] = val
                    pos_idx += 1
            elif self.peek().type in (TT.NUMBER, TT.KEYWORD, TT.OP):
                # Positional arg (e.g. Wait(100ms), DistanceToPlayer(500, <))
                val = self._parse_raw_value()
                kw[str(pos_idx)] = val
                pos_idx += 1
            else:
                break
            self.skip_newlines()
        return kw

    def _parse_raw_value(self) -> str:
        """Parse a value: collect all tokens until comma or RPAREN at depth 0.

        Handles NUMBER, IDENT, KEYWORD, STRING, MISC, LBRACKET/RBRACKET pairs,
        and nested LPAREN/RPAREN.
        """
        parts: list[str] = []
        depth = 0  # paren depth
        bracket_depth = 0

        while True:
            tok = self.peek()
            if tok.type == TT.RPAREN and depth == 0 and bracket_depth == 0:
                break
            if tok.type == TT.COMMA and depth == 0 and bracket_depth == 0:
                break

            if tok.type == TT.LPAREN:
                depth += 1
                parts.append(tok.value)
                self.advance()
            elif tok.type == TT.RPAREN:
                depth -= 1
                parts.append(tok.value)
                self.advance()
            elif tok.type == TT.LBRACKET:
                bracket_depth += 1
                parts.append(tok.value)
                self.advance()
            elif tok.type == TT.RBRACKET:
                bracket_depth -= 1
                parts.append(tok.value)
                self.advance()
            elif tok.type in (TT.IDENT, TT.KEYWORD, TT.NUMBER, TT.STRING, TT.MISC, TT.OP):
                parts.append(tok.value)
                self.advance()
            elif tok.type == TT.COLON:
                parts.append(tok.value)
                self.advance()
            else:
                break

        return "".join(parts).strip()


# === Public API ===


def parse_sst(source: str) -> Script:
    """Parse .sst source text into a Script AST node."""
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse_script()


def parse_sst_file(path: str) -> Script:
    """Parse a .sst file into a Script AST node."""
    with open(path) as f:
        source = f.read()
    return parse_sst(source)
