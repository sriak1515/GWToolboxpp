# Task 6: Tests

**Depends on:** Task 5 (CLI)  
**Output:** `tests/test_sst_gen.py`

## What to build

A test suite that verifies each layer independently and the full pipeline end-to-end.

## Test structure

```python
# tests/test_sst_gen.py
import pytest
import sys
sys.path.insert(0, "tools/sst-import")
from sst_gen import (
    # Huffman
    encode_string, decode_string, huffman_encode, frequent_char_value,
    # AST
    Script, Condition, Action, ...,
    # Serializer
    OutputStream, serialize_script,
    # Parser
    parse,
)
```

## Test categories

### 1. Huffman round-trip (5 tests)

```python
def test_huffman_roundtrip_simple():
    """Encode then decode a plain string."""
    s = "Hello World 123"
    assert decode_string(encode_string(s)) == s

def test_huffman_roundtrip_separators():
    """Encode then decode a string with separator bytes."""
    s = "S Test  0 1 \x7f C 38 \x7f A 14 1000 \x7f"
    assert decode_string(encode_string(s)) == s

def test_huffman_roundtrip_empty():
    assert decode_string(encode_string("")) == ""

def test_huffman_roundtrip_all_special_chars():
    """Test characters that have special Huffman encodings."""
    s = "A C . 0 1 2 3 4 5 6 7 8 9"
    assert decode_string(encode_string(s)) == s

def test_huffman_frequent_char_value():
    """Verify frequent_char_value matches C++ frequentCharValue."""
    assert frequent_char_value('a') == 0
    assert frequent_char_value('z') == 25
    assert frequent_char_value('D') == 26
    assert frequent_char_value('Z') == 48
    assert frequent_char_value('B') == 49
    assert frequent_char_value('<') == 62
    assert frequent_char_value('>') == 63
```

### 2. OutputStream tests (3 tests)

```python
def test_output_stream_write():
    s = OutputStream()
    s.write('S')
    s.write(42)
    s.write(True)
    assert str(s) == "S 42 1 "

def test_output_stream_write_string_with_spaces():
    s = OutputStream()
    s.write_string_with_spaces("Hello")
    # Must produce "Hello < " (space before <, matching C++)
    assert str(s) == "Hello < "

def test_output_stream_separator():
    s = OutputStream()
    s.write_separator(1)
    s.write_separator(2)
    s.write_separator(3)
    s.write_separator(4)
    result = str(s)
    assert result == "\x7f\x04\x05\x06"
```

### 3. Serializer unit tests (4 tests)

Build ASTs by hand, serialize, compare against known byte strings.

```python
def test_serialize_true_condition():
    """True_ condition should produce 'C 38 '."""
    from sst_gen.ast import TrueCondition
    s = OutputStream()
    TrueCondition().serialize(s)
    assert str(s) == "C 38 "

def test_serialize_wait_action():
    """Wait(1000ms) should produce 'A 14 1000 '."""
    from sst_gen.ast import WaitAction
    s = OutputStream()
    WaitAction(ms=1000).serialize(s)
    assert str(s) == "A 14 1000 "

def test_serialize_simple_script():
    """Minimal script: True_ condition + Wait(1000ms) action."""
    from sst_gen.ast import Script, TrueCondition, WaitAction
    script = Script(
        name="Test",
        trigger=0,
        conditions=[TrueCondition()],
        actions=[WaitAction(ms=1000)],
    )
    raw = serialize_script(script)
    # Verify it starts with "S Test < 0 1 ..." and contains expected tokens
    assert raw.startswith("S Test < ")
    assert "C 38 " in raw
    assert "A 14 1000 " in raw

def test_serialize_conditioned_action():
    """Conditioned with then/else should use level-2 separators."""
    from sst_gen.ast import (
        Script, TrueCondition, FoeCountCondition, WaitAction,
        ConditionedAction, ComparisonOperator,
    )
    cond = FoeCountCondition(count=1, comparison=ComparisonOperator.GreaterOrEqual)
    then = [WaitAction(ms=1000)]
    else_ = [WaitAction(ms=2000)]
    action = ConditionedAction(cond=cond, actions_if=then, actions_else=else_, actions_else_if=[])
    script = Script(
        name="CondTest",
        trigger=0,
        conditions=[TrueCondition()],
        actions=[action],
    )
    raw = serialize_script(script)
    # Level-2 separator must appear inside the Conditioned block
    assert "\x04" in raw
    # Level-1 separator must separate top-level actions
    assert "\x7f" in raw
```

### 4. Parser tests (4 tests)

```python
def test_parse_minimal_script():
    text = '''
script "Test":
    trigger: None
    when:
        True_
    then:
        Wait(ms: 1000)
'''
    ast = parse(text)
    assert ast.name == "Test"
    assert len(ast.conditions) == 1
    assert len(ast.actions) == 1

def test_parse_if_else():
    text = '''
script "IfTest":
    trigger: None
    when:
        True_
    then:
        if FoeCount >= 1:
            Wait(ms: 1000)
        else:
            Wait(ms: 2000)
'''
    ast = parse(text)
    assert len(ast.actions) == 1
    action = ast.actions[0]
    assert isinstance(action, ConditionedAction)
    assert len(action.actions_if) == 1
    assert len(action.actions_else) == 1

def test_parse_nested_if():
    text = '''
script "Nested":
    trigger: None
    when:
        True_
    then:
        if FoeCount >= 1:
            if PlayerIsDrunk:
                Wait(ms: 1000)
            else:
                Wait(ms: 2000)
        else:
            Wait(ms: 3000)
'''
    ast = parse(text)
    outer = ast.actions[0]
    assert isinstance(outer, ConditionedAction)
    inner = outer.actions_if[0]
    assert isinstance(inner, ConditionedAction)
    assert len(inner.actions_if) == 1  # Wait(1000)
    assert len(inner.actions_else) == 1  # Wait(2000)

def test_parse_or_condition():
    text = '''
script "OrTest":
    trigger: None
    when:
        Or(not PlayerHasBuff(Soul_Taker), PlayerHasBuff(id: Soul_Taker, hasMax: true, maxDuration: 5))
    then:
        Wait(ms: 1000)
'''
    ast = parse(text)
    assert len(ast.conditions) == 1
    assert isinstance(ast.conditions[0], DisjunctionCondition)
```

### 5. Full pipeline tests (7 tests, one per .sst file)

For each existing `.sst` file, generate the import string and verify it round-trips correctly.

```python
SST_FILES = [
    "scripts/sst/dark-aura-maintainer.sst",
    "scripts/sst/drunken-master-maintainer.sst",
    "scripts/sst/flag-formation-auto.sst",
    "scripts/sst/flag-narrow-formation.sst",
    "scripts/sst/flag-wide-formation.sst",
    "scripts/sst/soh-maintainer.sst",
    "scripts/sst/soul-taker-self-buff-maintainer.sst",
]

@pytest.mark.parametrize("filepath", SST_FILES)
def test_pipeline_roundtrip(filepath):
    """Generate import string, decode it, re-encode it, verify identity."""
    import os
    if not os.path.exists(filepath):
        pytest.skip("file not found")
    result = generate_import(filepath)
    encoded_part = result.split(" ", 1)[1]
    decoded = decode_string(encoded_part)
    re_encoded = encode_string(decoded)
    assert re_encoded == encoded_part
```

### 6. Regression: nested Conditioned (1 test)

Specific test for `drunken-master-maintainer.sst`:

```python
def test_drunken_master_nested_conditioned():
    """The drunken master script has 3 levels of nesting.
    This was completely broken in the old parser."""
    filepath = "scripts/sst/drunken-master-maintainer.sst"
    if not os.path.exists(filepath):
        pytest.skip("file not found")
    ast = parse(read_file(filepath))
    # Outer conditioned in then block
    outer = ast.actions[0]
    assert isinstance(outer, ConditionedAction)
    # Inner conditioned in then branch
    inner = outer.actions_if[1]  # EnterCriticalSection is [0], inner Conditioned is [1]
    assert isinstance(inner, ConditionedAction)
    # Inner has then and else
    assert len(inner.actions_if) == 2  # UseItemList + Wait
    assert len(inner.actions_else) == 1  # SendChat
```
