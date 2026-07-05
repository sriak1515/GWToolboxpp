# Task 4: Text Parser

**Depends on:** Task 1 (AST)  
**Output:** tokenizer + recursive descent parser in `sst_gen.py`

## What to build

Parse `.sst` text files into ASTs. No regex for structure — use a proper tokenizer and recursive descent parser. Regex only for simple token patterns like `>=`.

## .sst Format

See `plans/sst-script-gen-rewrite.md` for the full format spec.

Key rules:
- `//` starts a line comment
- Indentation is 4 spaces, significant for `then:`, `if`/`elif`/`else` blocks
- `when:` block body is indented (conditions, one per line)
- `then:` block body is indented (actions, one per line)
- `if`/`elif`/`else` blocks use indentation for nesting
- Parentheses delimit function calls and argument lists
- Commas separate arguments
- Colons separate keys from values in kwargs

## Tokenizer

Yield tokens of type: `IDENT`, `NUMBER`, `STRING`, `KEYWORD`, `OP`, `LPAREN`, `RPAREN`, `COLON`, `COMMA`, `DOT`, `NEWLINE`, `INDENT`, `DEDENT`, `EOF`.

Keywords (reserved): `script`, `trigger`, `when`, `then`, `if`, `elif`, `else`, `not`, `And`, `Or`, `true`, `false`

Ignore: spaces within a line (not at start), blank lines, comment lines.

Indent tracking:
- Track current indent level (number of leading spaces / 4)
- At start of each non-blank line, compute indent
- If indent increased: emit `INDENT`
- If indent decreased: emit `DEDENT` (one per level dropped)
- Track a stack of indent levels

## Grammar

```
script         := "script" STRING ":" INDENT header when_block then_block DEDENT
header         := (trigger_line | option_line)*
trigger_line   := "trigger" ":" IDENT
option_line    := IDENT ":" ("true" | "false")
when_block     := "when" ":" INDENT condition_line+ DEDENT
then_block     := "then" ":" INDENT action_line+ DEDENT

condition_line := condition_expr
condition_expr := "not" condition_expr
               | "Or" "(" condition_list ")"
               | "And" "(" condition_list ")"
               | IDENT "(" kwargs? ")"
               | IDENT COMPAR_OP NUMBER

action_line    := if_block | simple_action
if_block       := "if" condition_expr ":" INDENT action_line+ DEDENT
                  ("elif" condition_expr ":" INDENT action_line+ DEDENT)*
                  ("else" ":" INDENT action_line+ DEDENT)?
simple_action  := IDENT "(" kwargs? ")"
               | IDENT    # no-arg actions: EnterCriticalSection, LeaveCriticalSection, etc.

condition_list := condition_expr ("," condition_expr)*
kwargs         := kwarg ("," kwarg)*
kwarg          := IDENT ":" value
value          := IDENT | NUMBER | STRING | bool
```

## Parser structure

```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token: ...
    def advance(self) -> Token: ...
    def expect(self, type) -> Token: ...
    def match(self, type) -> Token | None: ...

    def parse_script(self) -> Script: ...
    def parse_header(self, script) -> None: ...
    def parse_when_block(self) -> list[Condition]: ...
    def parse_then_block(self) -> list[Action]: ...

    def parse_condition(self) -> Condition: ...
    def parse_condition_primary(self) -> Condition: ...

    def parse_action(self) -> Action: ...
    def parse_if_block(self) -> ConditionedAction: ...
    def parse_simple_action(self) -> Action: ...

    def parse_kwargs(self) -> dict: ...
    def parse_condition_list(self) -> list[Condition]: ...
```

## Condition parsing

`parse_condition` handles:
1. `not X` -> `NegatedCondition(parse_condition())`
2. `Or(X, Y, ...)` -> `DisjunctionCondition([parse_condition() for ...])`
3. `And(X, Y, ...)` -> `ConjunctionCondition([parse_condition() for ...])` — accepted but equivalent to listing them separately in `when`
4. `Type(args)` -> look up condition type, build with kwargs
5. `Type >= N` -> comparison condition

## Action parsing

`parse_action` handles:
1. `if cond: ... elif cond: ... else: ...` -> `ConditionedAction` via `parse_if_block`
2. `Type(args)` -> look up action type, build with kwargs
3. `Type` (no parens) -> no-arg action

### `parse_if_block`

This is the most complex parser function:

```python
def parse_if_block(self):
    self.expect('if')
    cond = self.parse_condition()
    self.expect(':')
    self.expect('INDENT')
    then_actions = []
    while not self.match('DEDENT'):
        then_actions.append(self.parse_action())
    
    else_ifs = []
    while self.match('elif'):
        ei_cond = self.parse_condition()
        self.expect(':')
        self.expect('INDENT')
        ei_actions = []
        while not self.match('DEDENT'):
            ei_actions.append(self.parse_action())
        else_ifs.append((ei_cond, ei_actions))
    
    else_actions = []
    if self.match('else'):
        self.expect(':')
        self.expect('INDENT')
        while not self.match('DEDENT'):
            else_actions.append(self.parse_action())
    
    return ConditionedAction(cond, then_actions, else_actions, else_ifs)
```

## Known condition type dispatch

Map condition names to `ConditionType` values and constructor kwargs:

```python
CONDITION_MAP = {
    "True_": (38, lambda kw: TrueCondition()),
    "False_": (37, lambda kw: FalseCondition()),
    "FoeCount": (35, lambda kw: FoeCountCondition(kw['count'], kw['comp'])),
    "PlayerHasBuff": (13, lambda kw: PlayerHasBuffCondition(...)),
    "PlayerHasSkill": (14, lambda kw: PlayerHasSkillCondition(...)),
    "HeroHasSkill": (56, lambda kw: HeroHasSkillCondition(...)),
    "Throttle": (44, lambda kw: ThrottleCondition(kw['ms'])),
    "PlayerIsDrunk": (61, lambda kw: PlayerIsDrunkCondition(...)),
    "ItemInInventoryList": (62, lambda kw: ItemInInventoryListCondition(kw['ids'])),
    "HasTerrainClearance": (57, lambda kw: HasTerrainClearanceCondition(...)),
    "ScriptVariableIsSet": (51, lambda kw: ScriptVariableIsSetCondition(...)),
    "PlayerHasCharacteristics": (46, lambda kw: PlayerHasCharacteristicsCondition(...)),
    "TargetHasCharacteristics": (47, lambda kw: TargetHasCharacteristicsCondition(...)),
    "AgentWithCharacteristicsCount": (48, lambda kw: AgentWithCharacteristicsCountCondition(...)),
    # ... etc for all conditions
}
```

## Known action type dispatch

```python
ACTION_MAP = {
    "Wait": (14, lambda kw: WaitAction(kw['ms'])),
    "Cast": (2, lambda kw: CastAction(kw['id'])),
    "EnterCriticalSection": (31, lambda kw: EnterCriticalSectionAction()),
    "LeaveCriticalSection": (32, lambda kw: LeaveCriticalSectionAction()),
    "ChangeTarget": (5, lambda kw: ChangeTargetAction(...)),
    "UseHeroSkill": (23, lambda kw: UseHeroSkillAction(...)),
    "SendChat": (15, lambda kw: SendChatAction(...)),
    "SetVariable": (33, lambda kw: SetVariableAction(...)),
    "FlagHero": (46, lambda kw: FlagHeroAction(...)),
    # ... etc
}
```

## Verification

Parse each of the 7 existing `.sst` files and dump the AST. Verify:
- Correct number of conditions and actions
- Nested `ConditionedAction` in `drunken-master-maintainer.sst` is properly tree-shaped
- `Or(...)` in `soul-taker-self-buff-maintainer.sst` parses correctly
- All kwargs are captured
