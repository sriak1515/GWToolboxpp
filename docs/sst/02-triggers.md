# Triggers

Triggers define when a script's conditions are evaluated and, if met, the script starts running.

## Trigger Types

| Trigger | Data Fields | Description |
|---------|------------|-------------|
| `None` | — | "Always on" — evaluated every frame, runs if conditions pass |
| `InstanceLoad` | — | Fires once when entering a new instance |
| `HardModePing` | — | Fires on the Hard Mode ping message (`\x8101\x7f84`) |
| `Hotkey` | `hotkey: Hotkey` | Fires when the specified key combination is pressed |
| `ChatMessage` | `message: string` | Fires when chat contains the specified substring |
| `BeginSkillCast` | `skillId: SkillID`, `hsr: AnyNoYes` | Fires when player starts casting a skill. `hsr` filters for fast-cast (Yes/No/Any) |
| `BeginCooldown` | `skillId: SkillID` | Fires when a skill finishes casting and enters cooldown |
| `SkillCastInterrupt` | `skillId: SkillID` | Fires when a skill cast is interrupted |
| `DisplayDialog` | `message: string` | Fires when an NPC dialog containing the substring is displayed |
| `DungeonReward` | — | Fires when a dungeon reward is received |
| `DoaZoneComplete` | `doaZone: DoaZone` | Fires when a DoA zone is completed (Foundry/Veil/Gloom/City) |

## TriggerData

```cpp
struct TriggerData {
    Hotkey hotkey{};                       // For Trigger::Hotkey
    std::string message{};                 // For Trigger::ChatMessage, Trigger::DisplayDialog
    GW::Constants::SkillID skillId{};      // For Trigger::BeginSkillCast/BeginCooldown/SkillCastInterrupt
    AnyNoYes hsr = AnyNoYes::Any;          // For Trigger::BeginSkillCast (fast-cast filter)
    DoaZone doaZone = DoaZone::Foundry;    // For Trigger::DoaZoneComplete
};
```

## Hotkey

```cpp
struct Hotkey {
    long keyData = 0;    // Virtual key code (VK_*)
    long modifier = 0;   // Bitmask: ModKey_Control, ModKey_Shift, ModKey_Alt
};
```

## Behavior Notes

- Scripts with `Trigger::None` are evaluated every frame but only run if no other script is already running (unless `canLaunchInParallel`).
- Hotkey triggers: if conditions aren't met, the keypress is still consumed if `alwaysBlockHotkeyKeys` is enabled.
- `ChatMessage` and `DisplayDialog` use substring matching (`contains()`).
- `BeginSkillCast` with `hsr = AnyNoYes::Yes` triggers only for fast-cast (activation time differs from base).
- `DoaZoneComplete` only triggers for the specific zone value set in `triggerData.doaZone`.
