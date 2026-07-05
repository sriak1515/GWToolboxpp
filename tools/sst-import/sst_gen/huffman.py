"""Huffman encoder/decoder — faithful port of plugins/Scripting/io.cpp."""

from __future__ import annotations

from typing import Optional

# === frequentCharValue / valueToFrequentChar ===

_FREQ_MAP: dict[str, int] = {}
_REV_FREQ: dict[int, str] = {}

def _init_freq() -> None:
    for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
        _FREQ_MAP[c] = i
        _REV_FREQ[i] = c
    for i, c in enumerate("DEFGHIJKLMNOPQRSTUVWXYZ"):
        _FREQ_MAP[c] = 26 + i
        _REV_FREQ[26 + i] = c

    specials = [
        (49,  'B', 'B'),
        (50,  '!', 'Exclamation'),
        (51,  '"', 'Quote'),
        (52,  '_', 'Underscore'),
        (53,  '#', 'Hashtag'),
        (54,  '+', 'Plus'),
        (55,  '-', 'Minus'),
        (56,  '=', 'Equals'),
        (57,  '*', 'Star'),
        (58,  "'", 'Apostroph'),
        (59,  '&', 'Ampersand'),
        (60,  '/', 'Slash'),
        (61,  '\x7f', 'EndOfAC'),
        (62,  '<', 'EndOfString'),
        (63,  '>', 'EndOfList'),
    ]
    for val, ch, _name in specials:
        _FREQ_MAP[ch] = val
        _REV_FREQ[val] = ch

_init_freq()


def frequent_char_value(c: str) -> int:
    """Map a character to its compact 6-bit value (0–63), or 0xFF if unmapped."""
    return _FREQ_MAP.get(c, 0xFF)


def value_to_frequent_char(i: int) -> str:
    """Reverse map: 6-bit value back to character."""
    if i not in _REV_FREQ:
        raise ValueError(f"invalid frequent-char value: {i}")
    return _REV_FREQ[i]


# === Bit helpers ===

def _make_bits(value: int, length: int) -> list[int]:
    """Encode *value* as *length* bits, MSB first."""
    return [(value >> (length - 1 - shift)) & 1 for shift in range(length)]


# === huffmanEncode ===

def huffman_encode(s: str) -> list[int]:
    """Encode a string into a bit sequence (faithful port of io.cpp:201-260)."""
    result: list[int] = []

    encoding: dict[str, list[int]] = {
        ' ': [0, 0],
        '0': [0, 1, 0, 0],
        '1': [0, 1, 0, 1],
        '2': [0, 1, 1, 0, 0, 0],
        '3': [0, 1, 1, 0, 0, 1],
        '4': [0, 1, 1, 0, 1, 0],
        '5': [0, 1, 1, 0, 1, 1],
        '6': [0, 1, 1, 1, 0, 0],
        '7': [0, 1, 1, 1, 0, 1],
        '8': [0, 1, 1, 1, 1, 0],
        '9': [0, 1, 1, 1, 1, 1],
        'A': [1, 0, 0, 0],
        'C': [1, 0, 0, 1],
        '.': [1, 0, 1, 0],
    }

    for ch in s:
        if ch in encoding:
            result.extend(encoding[ch])
        else:
            fv = frequent_char_value(ch)
            if fv < 64:
                result.extend([1, 1])
                result.extend(_make_bits(fv, 6))
            else:
                result.extend([1, 0, 1, 1])
                result.extend(_make_bits(ord(ch), 8))
    return result


# === splitIntoReadableChars ===

def bits_to_readable(bits: list[int]) -> str:
    """Convert a bit sequence to a readable string of [a-z0-9A-Z_#] (io.cpp:262-284)."""
    seq = list(bits)
    while len(seq) % 12 != 0:
        seq.append(0)

    def _make_int(a: int, b: int, c: int, d: int, e: int, f: int) -> int:
        return (a << 5) | (b << 4) | (c << 3) | (d << 2) | (e << 1) | f

    def _make_char(i: int) -> str:
        if i < 26:
            return chr(ord('a') + i)
        if i < 52:
            return chr(ord('A') + i - 26)
        if i < 62:
            return chr(ord('0') + i - 52)
        if i == 62:
            return '_'
        if i == 63:
            return '#'
        raise ValueError(f"invalid readable-char value: {i}")

    result: list[str] = []
    for i in range(0, len(seq), 6):
        result.append(_make_char(_make_int(
            seq[i+0], seq[i+1], seq[i+2],
            seq[i+3], seq[i+4], seq[i+5],
        )))
    return ''.join(result)


# === encodeString ===

def encode_string(s: str) -> str:
    """Combine huffman_encode and bits_to_readable."""
    return bits_to_readable(huffman_encode(s))


# === Decode side ===

def _combine_into_bit_sequence(s: str) -> list[int]:
    """Reverse of bits_to_readable — readable chars back to bits (io.cpp:295-328)."""
    result: list[int] = []
    for ch in s:
        if 'a' <= ch <= 'z':
            result.extend(_make_bits(ord(ch) - ord('a'), 6))
        elif 'A' <= ch <= 'Z':
            result.extend(_make_bits(ord(ch) - ord('A') + 26, 6))
        elif '0' <= ch <= '9':
            result.extend(_make_bits(ord(ch) - ord('0') + 52, 6))
        elif ch == '_':
            result.extend(_make_bits(62, 6))
        elif ch == '#':
            result.extend(_make_bits(63, 6))
        else:
            raise ValueError(f"invalid readable character: {ch!r}")
    return result


def _huffman_decode(seq: list[int]) -> str:
    """Decode a bit sequence back to a string (io.cpp:330-393)."""
    result: list[str] = []
    idx = 0
    while idx < len(seq):
        if seq[idx] == 0:
            if seq[idx + 1] == 0:
                result.append(' ')
                idx += 2
            else:
                if seq[idx + 2] == 0:
                    if seq[idx + 3] == 0:
                        result.append('0')
                        idx += 4
                    else:
                        result.append('1')
                        idx += 4
                else:
                    val = (seq[idx+3] << 2) | (seq[idx+4] << 1) | seq[idx+5]
                    result.append(chr(ord('2') + val))
                    idx += 6
        else:
            if seq[idx + 1] == 0:
                if seq[idx + 2] == 0:
                    if seq[idx + 3] == 0:
                        result.append('A')
                        idx += 4
                    else:
                        result.append('C')
                        idx += 4
                else:
                    if seq[idx + 3] == 0:
                        result.append('.')
                        idx += 4
                    else:
                        raw = (
                            (seq[idx+4] << 7) | (seq[idx+5] << 6) |
                            (seq[idx+6] << 5) | (seq[idx+7] << 4) |
                            (seq[idx+8] << 3) | (seq[idx+9] << 2) |
                            (seq[idx+10] << 1) | seq[idx+11]
                        )
                        result.append(chr(raw))
                        idx += 12
            else:
                value = (
                    (seq[idx+2] << 5) | (seq[idx+3] << 4) |
                    (seq[idx+4] << 3) | (seq[idx+5] << 2) |
                    (seq[idx+6] << 1) | seq[idx+7]
                )
                result.append(value_to_frequent_char(value))
                idx += 8
    return ''.join(result)


def decode_string(s: str) -> str:
    """Decode an encoded readable string back to the original text (io.cpp:395-403)."""
    valid = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_#')
    filtered = ''.join(ch for ch in s if ch in valid)
    return _huffman_decode(_combine_into_bit_sequence(filtered))


# === Self-test ===

if __name__ == '__main__':
    test_strings = [
        "S Test  0 1 0 0 0 0 0 0 \x7f C 38 \x7f A 14 1000 \x7f",
        "Hello World",
        "dark-aura-maintainer",
    ]

    for s in test_strings:
        enc = encode_string(s)
        dec = decode_string(enc)
        ok = dec == s
        print(f"{'OK' if ok else 'FAIL'}: {s!r}")
        print(f"  encoded -> {enc}")
        print(f"  decoded -> {dec!r}")
        print()

    # Round-trip the known header from dark-aura-maintainer.sst
    known = "11 6tAWnhki1nhaopaYm3tWmJnXnh_efeeeeefp2rLSuAp2rcrwrvCeeeelbF2rTWqvxbG#zgMHTeq#ygvp2bSqqqq7HvfelbF2bHKqvxd9Gzyp0a"
    decoded_known = decode_string(known)
    re_encoded = encode_string(decoded_known)
    rt_ok = re_encoded == known
    print(f"{'OK' if rt_ok else 'FAIL'}: round-trip on known SST header")
    print(f"  decoded -> {decoded_known!r}")
    print(f"  re-encoded -> {re_encoded}")
    print(f"  matches  -> {rt_ok}")
