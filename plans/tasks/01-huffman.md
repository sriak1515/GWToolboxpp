# Task 2: Huffman Encoder/Decoder

**Depends on:** nothing  
**Output:** pure functions in `sst_gen.py`

## What to build

A direct port of the Huffman encoding from `plugins/Scripting/io.cpp`. No changes to the algorithm — translate C++ to Python faithfully.

## Functions to implement

### `frequent_char_value(c: str) -> int`

Maps common characters to compact 6-bit values. From `io.cpp:112-150`.

```
a-z  -> 0-25
D-Z  -> 26-48
B    -> 49
!    -> 50
"    -> 51
_    -> 52
#    -> 53
+    -> 54
-    -> 55
=    -> 56
*    -> 57
'    -> 58
&    -> 59
/    -> 60
0x7F -> 61
<    -> 62
>    -> 63
```

### `huffman_encode(s: str) -> list[int]`

Encodes a string into a bit sequence. From `io.cpp:201-260`.

Encoding rules per character:
- `' '` (space) -> `[0, 0]`
- `'0'` -> `[0, 1, 0, 0]`
- `'1'` -> `[0, 1, 0, 1]`
- `'2'-'9'` -> `[0, 1, 1]` + 3-bit value (n-2)
- `'A'` -> `[1, 0, 0, 0]`
- `'C'` -> `[1, 0, 0, 1]`
- `'.'` -> `[1, 0, 1, 0]`
- Frequent char (value < 64) -> `[1, 1]` + 6-bit value
- Raw char -> `[1, 0, 1, 1]` + 8-bit raw value

Pad result to multiple of 12 bits with 0s.

### `split_into_readable_chars(bits: list[int]) -> str`

Converts bit sequence to readable string. From `io.cpp:262-284`.

Groups bits into 6-bit chunks. Maps each chunk:
- 0-25 -> `'a'-'z'`
- 26-51 -> `'A'-'Z'`
- 52-61 -> `'0'-'9'`
- 62 -> `'_''`
- 63 -> `'#''`

### `encode_string(s: str) -> str`

Combines the above: `huffman_encode` -> `split_into_readable_chars`.

### `decode_string(s: str) -> str`

Reverses the encoding. From `io.cpp:295-403`.

1. Strip invalid chars (only keep `a-z`, `A-Z`, `0-9`, `_`, `#`)
2. `combine_into_bit_sequence` — convert readable chars back to bits (reverse of `split_into_readable_chars`)
3. `huffman_decode` — decode bit sequence back to string (reverse of `huffman_encode`)

## Verification

After implementing, test round-trip on these strings:
- `"S Test  0 1 0 0 0 0 0 0 \x7f C 38 \x7f A 14 1000 \x7f"`
- The known encoded string from `dark-aura-maintainer.sst` header — decode it, re-encode it, verify identity

## Reference

- `plugins/Scripting/io.cpp:112-150` — `frequentCharValue`
- `plugins/Scripting/io.cpp:152-190` — `valueToFrequentChar`
- `plugins/Scripting/io.cpp:192-260` — `huffmanEncode`
- `plugins/Scripting/io.cpp:262-284` — `splitIntoReadableChars`
- `plugins/Scripting/io.cpp:286-293` — `encodeString`
- `plugins/Scripting/io.cpp:295-403` — `combineIntoBitSequence`, `huffmanDecode`, `decodeString`
