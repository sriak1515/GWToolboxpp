"""Tests for the SST script generator rewrite.

Covers Huffman encoding, OutputStream, serializer, parser,
full pipeline round-trips, and new condition types.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "sst-import"))

import pytest
from sst_gen.huffman import encode_string, decode_string, frequent_char_value
from sst_gen.ast import (
    OutputStream,
    Script,
    TrueCondition,
    FoeCountCondition,
    WaitAction,
    ConditionedAction,
    ComparisonOperator,
    PlayerAdrenalineCondition,
    PlayerHasEnergyCondition,
    RemainingCooldownCondition,
    DisjunctionCondition,
    NegatedCondition,
    serialize_script,
    _serialize_condition,
    _serialize_action,
    IsInCombatCondition,
    IsInCombat,
    AgentWithCharacteristicsCountCondition,
    AllegianceCharacteristic,
    DistanceToPlayerCharacteristic,
    AgentType,
    IsIsNot,
)
from sst_gen.parser import parse_sst, parse_sst_file
from sst_gen.__main__ import generate_import


# ── 1. Huffman round-trip (5 tests) ─────────────────────────────────────────


def test_huffman_roundtrip_simple():
    s = "Hello World 123"
    enc = encode_string(s)
    dec = decode_string(enc)
    assert dec.startswith(s)
    assert encode_string(dec) == enc


def test_huffman_roundtrip_separators():
    s = "S Test  0 1 \x7f C 38 \x7f A 14 1000 \x7f"
    enc = encode_string(s)
    dec = decode_string(enc)
    assert dec.startswith(s)
    assert encode_string(dec) == enc


def test_huffman_roundtrip_empty():
    assert decode_string(encode_string("")) == ""


def test_huffman_roundtrip_all_special_chars():
    s = "A C . 0 1 2 3 4 5 6 7 8 9"
    enc = encode_string(s)
    dec = decode_string(enc)
    assert dec.startswith(s)
    assert encode_string(dec) == enc


def test_huffman_frequent_char_value():
    assert frequent_char_value('a') == 0
    assert frequent_char_value('z') == 25
    assert frequent_char_value('D') == 26
    assert frequent_char_value('Z') == 48
    assert frequent_char_value('B') == 49
    assert frequent_char_value('<') == 62
    assert frequent_char_value('>') == 63


# ── 2. OutputStream tests (3 tests) ─────────────────────────────────────────


def test_output_stream_write():
    s = OutputStream()
    s.write('S')
    s.write(42)
    s.write(True)
    assert str(s) == "S 42 1 "


def test_output_stream_write_string_with_spaces():
    s = OutputStream()
    s.write_string_with_spaces("Hello")
    assert str(s) == "Hello < "


def test_output_stream_separator():
    s = OutputStream()
    s.write_separator(1)
    s.write_separator(2)
    s.write_separator(3)
    s.write_separator(4)
    result = str(s)
    assert result == "\x7f\x04\x05\x06"


# ── 3. Serializer unit tests (4 tests) ──────────────────────────────────────


def test_serialize_true_condition():
    s = OutputStream()
    _serialize_condition(s, TrueCondition())
    assert str(s) == "C 38 "


def test_serialize_wait_action():
    s = OutputStream()
    _serialize_action(s, WaitAction(ms=1000))
    assert str(s) == "A 14 1000 "


def test_serialize_simple_script():
    script = Script(
        name="Test",
        trigger=0,
        conditions=[TrueCondition()],
        actions=[WaitAction(ms=1000)],
    )
    raw = serialize_script(script)
    assert raw.startswith("S Test < ")
    assert "C 38 " in raw
    assert "A 14 1000 " in raw


def test_serialize_conditioned_action():
    cond = FoeCountCondition(count=1, comparison=ComparisonOperator.GreaterOrEqual)
    then = [WaitAction(ms=1000)]
    else_ = [WaitAction(ms=2000)]
    action = ConditionedAction(condition=cond, actions_if=then, actions_else=else_, actions_else_if=[])
    script = Script(
        name="CondTest",
        trigger=0,
        conditions=[TrueCondition()],
        actions=[action],
    )
    raw = serialize_script(script)
    assert "\x04" in raw
    assert "\x7f" in raw


# ── 4. Parser tests (4 tests) ───────────────────────────────────────────────


def test_parse_minimal_script():
    text = '''
script "Test" {
    trigger: None
    when {
        True_
    }
    then {
        Wait(1000ms)
    }
}
'''
    ast = parse_sst(text)
    assert ast.name == "Test"
    assert len(ast.conditions) == 1
    assert len(ast.actions) == 1


def test_parse_if_else():
    text = '''
script "IfTest" {
    trigger: None
    when {
        True_
    }
    then {
        if FoeCount >= 1: {
            Wait(1000ms)
        } else: {
            Wait(2000ms)
        }
    }
}
'''
    ast = parse_sst(text)
    assert len(ast.actions) == 1
    action = ast.actions[0]
    assert isinstance(action, ConditionedAction)
    assert len(action.actions_if) == 1
    assert len(action.actions_else) == 1


def test_parse_nested_if():
    text = '''
script "Nested" {
    trigger: None
    when {
        True_
    }
    then {
        if FoeCount >= 1: {
            if PlayerIsDrunk: {
                Wait(1000ms)
            } else: {
                Wait(2000ms)
            }
        } else: {
            Wait(3000ms)
        }
    }
}
'''
    ast = parse_sst(text)
    outer = ast.actions[0]
    assert isinstance(outer, ConditionedAction)
    inner = outer.actions_if[0]
    assert isinstance(inner, ConditionedAction)
    assert len(inner.actions_if) == 1
    assert len(inner.actions_else) == 1


def test_parse_or_condition():
    text = '''
script "OrTest" {
    trigger: None
    when {
        Or(not PlayerHasBuff(Dark_Aura), PlayerHasBuff(skill: Dark_Aura, hasMax: true, maxDuration: 5))
    }
    then {
        Wait(1000ms)
    }
}
'''
    ast = parse_sst(text)
    assert len(ast.conditions) == 1
    assert isinstance(ast.conditions[0], DisjunctionCondition)


# ── 5. Full pipeline tests (9 tests, one per .sst file) ─────────────────────

SST_FILES = [
    "scripts/sst/dark-aura-maintainer.sst",
    "scripts/sst/dervish-attack-optimizer.sst",
    "scripts/sst/drunken-master-maintainer.sst",
    "scripts/sst/flag-formation-auto.sst",
    "scripts/sst/flag-narrow-formation.sst",
    "scripts/sst/flag-wide-formation.sst",
    "scripts/sst/soh-maintainer.sst",
    "scripts/sst/soul-taker-self-buff-maintainer.sst",
    "scripts/sst/st-combat-prep.sst",
]


@pytest.mark.parametrize("filepath", SST_FILES)
def test_pipeline_roundtrip(filepath):
    full_path = os.path.join(os.path.dirname(__file__), "..", filepath)
    if not os.path.exists(full_path):
        pytest.skip("file not found")
    result = generate_import(full_path)
    encoded_part = result.split(" ", 1)[1]
    decoded = decode_string(encoded_part)
    re_encoded = encode_string(decoded)
    assert re_encoded == encoded_part


# ── 6. Regression: nested Conditioned (1 test) ─────────────────────────────


def test_drunken_master_nested_conditioned():
    filepath = os.path.join(
        os.path.dirname(__file__), "..", "scripts/sst/drunken-master-maintainer.sst"
    )
    if not os.path.exists(filepath):
        pytest.skip("file not found")
    ast = parse_sst_file(filepath)
    outer = ast.actions[0]
    assert isinstance(outer, ConditionedAction)
    inner = outer.actions_if[1]
    assert isinstance(inner, ConditionedAction)
    assert len(inner.actions_if) == 2
    assert len(inner.actions_else) == 1


# ── 7. New condition types (3 tests) ────────────────────────────────────────


def test_parse_player_adrenaline():
    text = '''
script "AdrenalineTest" {
    trigger: None
    when {
        PlayerAdrenaline(skill: Eremites_Attack, adrenaline: 5, comp: <)
    }
    then {
        Wait(1000ms)
    }
}
'''
    ast = parse_sst(text)
    assert len(ast.conditions) == 1
    cond = ast.conditions[0]
    s = OutputStream()
    _serialize_condition(s, cond)
    output = str(s)
    assert "C 63 " in output


def test_parse_player_has_energy():
    text = '''
script "EnergyTest" {
    trigger: None
    when {
        PlayerHasEnergy(energy: 10, comp: >=)
    }
    then {
        Wait(1000ms)
    }
}
'''
    ast = parse_sst(text)
    assert len(ast.conditions) == 1
    s = OutputStream()
    _serialize_condition(s, ast.conditions[0])
    output = str(s)
    assert "C 17 " in output


def test_parse_remaining_cooldown():
    text = '''
script "CooldownTest" {
    trigger: None
    when {
        RemainingCooldown(id: Dark_Aura, hasMin: false, minCooldown: 0, hasMax: true, maxCooldown: 5000)
    }
    then {
        Wait(1000ms)
    }
}
'''
    ast = parse_sst(text)
    assert len(ast.conditions) == 1
    s = OutputStream()
    _serialize_condition(s, ast.conditions[0])
    output = str(s)
    assert "C 34 " in output


# ── 8. IsInCombat condition (3 tests) ──────────────────────────────────────


def test_is_in_combat_default_range():
    cond = IsInCombat()
    assert cond.range == 1012.0
    assert cond.comparison == ComparisonOperator.Less
    expected = AgentWithCharacteristicsCountCondition(
        characteristics=[
            AllegianceCharacteristic(agent_type=AgentType.Hostile, comparison=IsIsNot.Is_),
            DistanceToPlayerCharacteristic(value=1012.0, comparison=ComparisonOperator.Less),
        ],
        count=1,
        comparison=ComparisonOperator.GreaterOrEqual,
    )
    s1 = OutputStream()
    _serialize_condition(s1, cond)
    s2 = OutputStream()
    _serialize_condition(s2, expected)
    assert str(s1) == str(s2)


def test_is_in_combat_custom_range():
    cond = IsInCombat(range=500.0)
    expected = AgentWithCharacteristicsCountCondition(
        characteristics=[
            AllegianceCharacteristic(agent_type=AgentType.Hostile, comparison=IsIsNot.Is_),
            DistanceToPlayerCharacteristic(value=500.0, comparison=ComparisonOperator.Less),
        ],
        count=1,
        comparison=ComparisonOperator.GreaterOrEqual,
    )
    s1 = OutputStream()
    _serialize_condition(s1, cond)
    s2 = OutputStream()
    _serialize_condition(s2, expected)
    assert str(s1) == str(s2)


def test_parse_is_in_combat_bare():
    text = '''
script "CombatTest" {
    trigger: None
    when {
        IsInCombat
    }
    then {
        Wait(1000ms)
    }
}
'''
    ast = parse_sst(text)
    assert len(ast.conditions) == 1
    cond = ast.conditions[0]
    assert isinstance(cond, IsInCombatCondition)
    assert cond.range == 1012.0


def test_parse_is_in_combat_with_range():
    text = '''
script "CombatTest2" {
    trigger: None
    when {
        IsInCombat(range: 500)
    }
    then {
        Wait(1000ms)
    }
}
'''
    ast = parse_sst(text)
    assert len(ast.conditions) == 1
    cond = ast.conditions[0]
    assert isinstance(cond, IsInCombatCondition)
    assert cond.range == 500.0
