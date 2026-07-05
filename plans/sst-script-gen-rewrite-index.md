# SST Script Generator Rewrite — Index

## Context

`tools/sst-import/sst_script_gen.py` converts `.sst` text files into clipboard-importable strings for SST's GUI import. The existing script has fundamental architectural bugs. **Do not use the existing script as reference code.** Write everything from scratch, using only the C++ source in `plugins/Scripting/` as the source of truth for the binary serialization format.

## Recent Changes (as of 2026-07-05)

- Added `PlayerAdrenaline` condition type (ID 63) for checking adrenaline of specific skills
- Added `PlayerHasEnergy` condition parser support
- Added `RemainingCooldown` condition parser support
- New script: `dervish-attack-optimizer.sst` (9 total SST files now)

## Goal

A single-file Python tool (`tools/sst-import/sst_gen.py`) that:
- Parses `.sst` text files into an AST
- Serializes the AST to the v11 binary format (bit-identical to C++)
- Huffman-encodes the result for clipboard import
- Covers 100% of conditions, actions, and characteristics

## Files

| File | Description |
|------|-------------|
| `plans/sst-script-gen-rewrite-index.md` | This file |
| `plans/tasks/00-ast.md` | Task 1: AST type definitions |
| `plans/tasks/01-huffman.md` | Task 2: Huffman encoder/decoder |
| `plans/tasks/02-serializer.md` | Task 3: Binary serializer |
| `plans/tasks/03-parser.md` | Task 4: Text parser |
| `plans/tasks/04-cli.md` | Task 5: CLI entry point |
| `plans/tasks/05-tests.md` | Task 6: Tests |
| `plans/tasks/06-migrate.md` | Task 7: One-time migration of existing files |

## Implementation Order

```
1. AST (00-ast.md)          ─┐
                              ├─> 3. Serializer (02-serializer.md)
2. Huffman (01-huffman.md)  ─┘         │
                                       ├─> 5. CLI (04-cli.md)
                              ┌────────┘         │
4. Parser (03-parser.md) ────┘                  ├─> 6. Tests (05-tests.md)
                                                │         │
                                                └─────────┴─> 7. Migrate (06-migrate.md)
```

Tasks 1 and 2 are independent. Task 3 depends on 1. Task 4 depends on 1. Task 5 depends on 2, 3, 4. Task 6 depends on 5. Task 7 depends on 6.
