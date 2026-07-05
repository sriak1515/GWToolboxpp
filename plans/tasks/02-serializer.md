# Task 3: Binary Serializer

**Depends on:** Task 1 (AST)  
**Output:** serializer functions + `OutputStream` class in `sst_gen.py`

## What to build

Walk an AST and produce the raw binary string (before Huffman encoding). Must match the C++ plugin's output byte-for-byte.

## Design Principle

**The caller writes separators, not the node.** In C++, `serialize(Script)` calls:
```cpp
for (const auto& condition : script.conditions) {
    condition->serialize(stream);
    stream.writeSeparator();
}
```

The Python serializer must do the same. Each node's `serialize(stream)` writes only its data. The calling code writes the separator after.

## OutputStream

```python
class OutputStream:
    def __init__(self):
        self.parts = []

    def write(self, val):
        """Write a value followed by a space. Matches C++ operator<<."""
        if isinstance(val, bool):
            val = 1 if val else 0
        self.parts.append(str(val) + " ")
        return self

    def write_string_with_spaces(self, s):
        """Write a string followed by '<'. Matches C++ writeStringWithSpaces.
        
        CRITICAL: C++ does  stream << word << "<"  
        Which with operator<< produces:  word < 
        (space after word from first <<, then '<', then space from second <<)
        """
        self.parts.append(s + " < ")
        return self

    def write_separator(self, lvl=1):
        """Write a raw separator byte. No space after."""
        tokens = {1: 0x7F, 2: 0x04, 3: 0x05, 4: 0x06}
        self.parts.append(chr(tokens[lvl]))
        return self

    def __str__(self):
        return "".join(self.parts)
```

## Top-level serialize

From `SpeedrunScriptingTools.cpp:158-214`:

```python
def serialize_script(script: Script) -> str:
    stream = OutputStream()
    stream.write('S')
    stream.write_string_with_spaces(script.name)
    stream.write(script.trigger)
    stream.write(script.enabled)
    # trigger-specific data (varies by trigger type)
    serialize_trigger_data(stream, script)
    stream.write(script.toggle_hotkey.key_data)
    stream.write(script.toggle_hotkey.modifier)
    stream.write(script.options.show_message_when_triggered)
    stream.write(script.options.show_message_when_toggled)
    stream.write(script.options.globally_exclusive)
    stream.write(script.options.can_launch_in_parallel)
    stream.write_separator(1)
    for cond in script.conditions:
        cond.serialize(stream)
        stream.write_separator(1)
    for act in script.actions:
        act.serialize(stream)
        stream.write_separator(1)
    return str(stream)
```

## Trigger data serialization

From `SpeedrunScriptingTools.cpp:166-194`. Varies by trigger type:

| Trigger | Data written |
|---------|-------------|
| None, InstanceLoad, HardModePing, DungeonReward | (nothing) |
| Hotkey | keyData, modifier |
| ChatMessage | message (writeStringWithSpaces) |
| BeginCooldown, SkillCastInterrupt | skillId |
| BeginSkillCast | skillId, hsr |
| DoaZoneComplete | doaZone |
| DisplayDialog | message (writeStringWithSpaces) |

## Condition serialize

Each condition type writes: `C <type_id>` (from base) + type-specific data.

**Do NOT write a trailing separator.** The caller does that.

Reference for each condition: `plugins/Scripting/ConditionImpls.cpp`. Key examples:

- `TrueCondition`: just `C 38` (no additional data)
- `FoeCountCondition`: `C 35 <count> <comparison>`
- `NegatedCondition`: `C 0 <inner_condition>` (inner condition serializes itself)
- `ConjunctionCondition`: `C 2 <count> <sub_conditions...>`
- `PlayerHasBuffCondition`: `C 13 <skill_id> <min_dur> <has_min> <max_dur> <has_max>`
- `PlayerHasCharacteristicsCondition`: `C 46 <characteristic>` + `writeSeparator(3)`
- `ThrottleCondition`: `C 44 <delay_ms>`

## Action serialize

Each action type writes: `A <type_id>` (from base) + type-specific data.

**Do NOT write a trailing separator.** The caller does that.

Reference: `plugins/Scripting/ActionImpls.cpp`. Key examples:

- `WaitAction`: `A 14 <ms>`
- `CastAction`: `A 2 <skill_id>`
- `EnterCriticalSection`: `A 31` (no additional data)
- `ChangeTargetAction`: `A 5 <sorting> <preferNonHexed> <requireSameModelId> <rotateThrough> <characteristics...>` (each characteristic followed by `writeSeparator(3)`)
- `SendChatAction`: `A 15 <channel> <message>< >`
- `ConditionedAction`: see below

## ConditionedAction serialize

From `ActionImpls.cpp:1270-1305`. This is the most complex action:

```python
def serialize_conditioned(stream, action):
    stream.write('A')
    stream.write(17)  # ActionType.Conditioned
    # Condition + level-2 separator
    if action.condition:
        action.condition.serialize(stream)
    else:
        stream.write('/')  # missingContentToken
    stream.write_separator(2)
    # Then actions
    stream.write(len(action.actions_if))
    for a in action.actions_if:
        if a:
            a.serialize(stream)
        else:
            stream.write('/')
        stream.write_separator(2)
    # Else actions
    stream.write(len(action.actions_else))
    for a in action.actions_else:
        if a:
            a.serialize(stream)
        else:
            stream.write('/')
        stream.write_separator(2)
    # Else-if branches
    stream.write(len(action.actions_else_if))
    for ei_cond, ei_actions in action.actions_else_if:
        if ei_cond:
            ei_cond.serialize(stream)
        else:
            stream.write('/')
        stream.write_separator(2)
        stream.write(len(ei_actions))
        for a in ei_actions:
            if a:
                a.serialize(stream)
            else:
                stream.write('/')
            stream.write_separator(2)
```

## Characteristic serialize

Each characteristic writes: `X <type_id>` (from base) + type-specific data + `writeSeparator(3)`.

Reference: `plugins/Scripting/CharacteristicImpls.cpp`. Example:

```python
def serialize_allegiance(stream, char):
    stream.write('X')
    stream.write(11)  # CharacteristicType::Allegiance
    stream.write(char.agent_type)
    stream.write(char.comparison)
    stream.write_separator(3)
```

## Missing content token

C++ uses `"/"` as a placeholder for null/empty child nodes. From `SerializationIncrement.cpp:9`:
```cpp
const std::string missingContentToken = "/";
```

Write `"/"` followed by a space (via `stream.write("/")`) when a child is null.

## Verification

Build ASTs by hand for the simplest scripts and compare serialized output:
1. `soh-maintainer.sst` — simple conditions + simple actions
2. `dark-aura-maintainer.sst` — `not` condition, `HeroHasSkill`, `ChangeTarget` with `Allegiance` characteristic
3. `drunken-master-maintainer.sst` — nested `ConditionedAction`
4. `dervish-attack-optimizer.sst` — uses `PlayerAdrenaline`, `RemainingCooldown`, `PlayerHasEnergy` conditions
