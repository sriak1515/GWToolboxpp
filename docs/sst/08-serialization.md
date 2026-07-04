# Serialization Format

Scripts and groups are serialized to binary strings, then base64-encoded for clipboard and INI storage.

## Structure

### Script (`S` prefix)
```
S <name> <trigger> <enabled> <trigger-specific-data> <toggleHotkey> <showWhenTriggered> <showWhenToggled> <globallyExclusive> <canLaunchInParallel>
<C|A>... (conditions and actions, prefixed with C or A)
```

### Group (`G` prefix)
```
G <name> <enabled>
<C>... (group conditions)
<S>... (child scripts)
```

## Version History

| Version | Notes |
|---------|-------|
| 1-7 | Prerelease, unsupported |
| 8 | v1.0-1.2 (too old to import) |
| 9 | Skipped |
| 10 | v1.3-1.6 (pre-characteristic refactor) |
| 11 | Current (all conditions use characteristics) |

## Clipboard Operations

- **Export**: Base64-encode serialized string, copy to clipboard
- **Import**: Read clipboard, base64-decode, parse `S` or `G` prefix

## IO Utilities

```cpp
// Base64 encoding/decoding
std::optional<std::string> encodeString(const std::string&);
std::optional<std::string> decodeString(std::string&&);

// String with spaces handling
std::string readStringWithSpaces(InputStream&);
void writeStringWithSpaces(OutputStream&, const std::string&);

// Logging
void logMessage(std::string_view message, std::string_view pluginName = "SST");
```

## Persistence

Scripts are saved to the plugin's INI file as base64-encoded blobs under keys `scripts` and `groups`. On load, the plugin reads these blobs and deserializes them. Automatic backups are managed by `BackupManager`.
