# Overview

## What is SpeedrunScriptingTools?

A plugin that provides an in-game visual scripting engine for Guild Wars. Users create **Scripts** containing conditions and actions, triggered by game events, hotkeys, or always-on rules. Scripts are organized into **Groups** for bulk enable/disable.

## Core Data Structures

### Script

```cpp
struct Script {
    std::string name = "New script";
    bool enabled = true;

    // When to start running
    Trigger trigger = Trigger::None;
    TriggerData triggerData{};

    // Gate: script only runs if ALL conditions are true
    std::vector<ConditionPtr> conditions;

    // Actions executed in sequence
    std::vector<ActionPtr> actions;

    // Behavior flags
    bool showMessageWhenTriggered = false;  // Log to chat on trigger
    bool showMessageWhenToggled = false;    // Log to chat on enable/disable
    bool canLaunchInParallel = false;       // Allow running alongside other scripts
    bool globallyExclusive = false;         // Block all other scripts while running

    // Optional hotkey to toggle enabled/disabled
    Hotkey enabledToggleHotkey{};
};
```

### Group

```cpp
struct Group {
    std::string name = "New group";
    bool enabled = true;
    std::vector<ConditionPtr> conditions;  // Gate for ALL scripts in group
    std::vector<Script> scripts;
};
```

Groups act as a collective gate: if a group's conditions fail, none of its scripts can run.

## Execution Model

1. **Loading screen** clears all running scripts.
2. Each frame, the engine evaluates all enabled scripts:
   - Skips scripts with no conditions, no trigger, or no actions.
   - Skips scripts already running (unless `canLaunchInParallel`).
   - Checks `conditions` — if any fail, the script is skipped.
   - Checks `group.conditions` for grouped scripts.
3. Triggered scripts are added to `m_currentScripts`.
4. For each running script, the first action in the queue is processed:
   - `ImmediateFinish` actions: run `initialAction()` + `finalAction()` instantly, advance.
   - Other actions: call `initialAction()` once, then poll `isComplete()` each frame.
   - On `Complete`: call `finalAction()`, advance to next action.
   - On `Error`: abort the script.
   - `CompleteAndEnteringCriticalSection` / `CompleteAndLeavingCriticalSection`: toggle `globallyExclusive` dynamically.
5. Scripts with empty action queues are removed.

## Global Settings

| Setting | Description |
|---------|-------------|
| `runInOutposts` | Execute scripts in outpost areas (not just explorable) |
| `alwaysBlockHotkeyKeys` | Block hotkey keys from GW even if script conditions aren't met |
| `clearScriptsKey` | Hotkey to immediately clear all running scripts |

## Chat Commands

| Command | Effect |
|---------|--------|
| `/restore SST recent` | Restore most recent backup |
| `/restore SST largest` | Restore largest backup |
| `/restore SST list` | List available backups |
| `/restore SST <N>` | Restore backup by index |
| `/restore SST help` | Show help |

## API (for other plugins)

```cpp
// Trigger all scripts matching a trigger type
bool triggerScripts(
    Trigger triggerType,
    std::function<bool(const Script&)> extraConditions = [](const Script&) { return true; },
    bool checkConditions = true
);

// Load scripts from a ToolboxIni file
void loadFromIniFile(const ToolboxIni& ini);
```

## Key Source Files

| File | Key Classes/Functions |
|------|----------------------|
| `SpeedrunScriptingTools.h` | `Script`, `Group`, `SpeedrunScriptingTools` |
| `SpeedrunScriptingTools.cpp` | Serialization, Update loop, WndProc, hooks |
| `Action.h` | `Action` base class, `ActionType` enum |
| `ActionImpls.h` | All 47 concrete action classes |
| `Condition.h` | `Condition` base class, `ConditionType` enum |
| `ConditionImpls.h` | All 48 concrete condition classes |
| `Characteristic.h` | `Characteristic` base class, `CharacteristicType` enum |
| `CharacteristicImpls.h` | All 22 concrete characteristic classes |
| `Enums.h` | `Trigger`, `Hotkey`, `TriggerData`, `DoorID`, shared enums |
| `ScriptVariables.h` | `ScriptVariableManager` singleton |
| `InstanceInfo.h` | `InstanceInfo` singleton (doors, targets, names) |
| `QuestInfo.h` | `QuestInfo` singleton (quest/objective state) |
| `io.h` | `InputStream`/`OutputStream`, `logMessage()` |
