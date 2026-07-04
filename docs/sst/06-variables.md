# Script Variables

## ScriptVariableManager

A global singleton key-value store for script variables.

```cpp
struct Variable {
    int value = 0;
    bool preserveThroughInstanceLoad = false;  // Survives loading screens
};

class ScriptVariableManager {
    void set(const std::string& name, Variable var);
    std::optional<Variable> get(const std::string& name) const;
    void clear();  // Removes non-preserved variables
    const std::unordered_map<std::string, Variable>& list() const;
};
```

## Usage in Scripts

### Actions

| Action | Effect |
|--------|--------|
| `SetVariable` | Sets `name` to `value`. If `preserveThroughInstanceLoad`, survives loading screens |
| `IncrementVariable` | Increments `name` by 1 |
| `DecrementVariable` | Decrements `name` by 1 |

### Conditions

| Condition | Effect |
|-----------|--------|
| `ScriptVariableValue` | True if variable `name` value meets `comp` with `value` |
| `ScriptVariableIsSet` | True if variable `name` is/is not set (`IsIsNot`) |

## Behavior

- Variables are cleared on instance load unless `preserveThroughInstanceLoad = true`.
- Variables default to value `0` if not set (for `ScriptVariableValue` condition).
- `ScriptVariableIsSet` checks if the variable exists in the map, not its value.
