# Task 5: CLI Entry Point

**Depends on:** Tasks 2 (Huffman), 3 (Serializer), 4 (Parser)  
**Output:** `tools/sst-import/sst_gen.py` (single executable file)

## What to build

A single-file CLI tool that wires parser, serializer, and encoder together.

## CLI interface

```
python3 sst_gen.py <file.sst>                    # Print import string
python3 sst_gen.py <file.sst> --copy             # Copy to clipboard (termux-clipboard-set)
python3 sst_gen.py --regen-all <dir>             # Regenerate all .sst in dir, update headers
python3 sst_gen.py --decode <encoded_string>     # Decode an import string for debugging
```

## Main flow

```python
def generate_import(filepath: str) -> str:
    text = read_file(filepath)
    ast = parse(text)                    # Task 4
    raw = serialize(ast)                 # Task 3
    encoded = encode_string(raw)         # Task 2
    return f"{CURRENT_VERSION} {encoded}"

if __name__ == "__main__":
    # parse args, dispatch to appropriate function
```

`CURRENT_VERSION = 11`

## --regen-all

For each `.sst` file in the directory:
1. Generate the import string
2. Read the file
3. Replace the clipboard import line in the header comment
4. Write the file back

Header format to match:
```
// Clipboard import (paste into SST's Import field):
//   <encoded_string>
```

If the header doesn't have this block yet, add it after the description comments and before the `script` keyword.

## --decode

Debug tool: decode an import string back to readable form.

1. Strip the version prefix
2. Huffman decode
3. Print the raw serialized string with separator tokens labeled:
   - `\x7F` -> `<SEP1>`
   - `\x04` -> `<SEP2>`
   - `\x05` -> `<SEP3>`
   - `\x06` -> `<SEP4>`
   - Non-printable hex -> `<0xNN>`

## Error handling

- If parsing fails, print the line number and the problematic text
- Never silently produce wrong output — fail loud

## File structure

Single file. Sections in order:
1. License/header comment
2. AST dataclasses (from Task 1)
3. Enum mappings
4. OutputStream class
5. Huffman encode/decode (from Task 2)
6. Serializer (from Task 3)
7. Tokenizer + Parser (from Task 4)
8. CLI entry point
