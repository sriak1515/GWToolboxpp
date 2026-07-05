#!/usr/bin/env python3
"""CLI entry point for the SST script generator."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from .huffman import encode_string, decode_string
from .parser import parse_sst
from .ast import serialize_script

CURRENT_VERSION = 11
HEADER_MARKER = "// Clipboard import (paste into SST's Import field):"
HEADER_REPLACEMENT = HEADER_MARKER + "\n//   {}"


def read_file(filepath: str) -> str:
    """Read file content, raising on error."""
    try:
        with open(filepath) as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def generate_import(filepath: str) -> str:
    """Generate a clipboard import string from an .sst file."""
    text = read_file(filepath)
    ast = parse_sst(text)
    raw = serialize_script(ast)
    encoded = encode_string(raw)
    return f"{CURRENT_VERSION} {encoded}"


def cmd_generate(filepath: str, copy: bool) -> None:
    """Generate import string for a single file."""
    import_str = generate_import(filepath)
    if copy:
        try:
            subprocess.run(
                ["termux-clipboard-set", import_str],
                check=True,
                capture_output=True,
            )
            print(f"Copied to clipboard ({len(import_str)} chars)")
        except FileNotFoundError:
            print("Error: termux-clipboard-set not found", file=sys.stderr)
            print("Install with: pkg install termux-api", file=sys.stderr)
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Error copying to clipboard: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(import_str)


def cmd_regen_all(directory: str) -> None:
    """Regenerate import strings for all .sst files in a directory."""
    dir_path = Path(directory)
    if not dir_path.is_dir():
        print(f"Error: not a directory: {directory}", file=sys.stderr)
        sys.exit(1)

    sst_files = sorted(dir_path.glob("*.sst"))
    if not sst_files:
        print(f"No .sst files found in {directory}")
        return

    for filepath in sst_files:
        try:
            text = filepath.read_text()
        except IOError as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
            continue

        # Generate new import string
        try:
            ast = parse_sst(text)
            raw = serialize_script(ast)
            encoded = encode_string(raw)
        except Exception as e:
            print(f"Error processing {filepath.name}: {e}", file=sys.stderr)
            continue

        import_line = f"{CURRENT_VERSION} {encoded}"
        replacement = HEADER_REPLACEMENT.format(import_line)

        if HEADER_MARKER in text:
            # Replace existing header
            pattern = r"// Clipboard import \(paste into SST's Import field\):\n//   .+"
            new_text = re.sub(pattern, replacement, text)
            if new_text == text:
                print(f"Warning: could not update header in {filepath.name}")
                continue
        else:
            # Insert header before first 'script' keyword
            match = re.search(r"^(script\b)", text, re.MULTILINE)
            if match:
                insert_pos = match.start()
                new_text = text[:insert_pos] + replacement + "\n" + text[insert_pos:]
            else:
                # No 'script' keyword found, append at end
                new_text = text + replacement + "\n"

        try:
            filepath.write_text(new_text)
            print(f"Updated {filepath.name}")
        except IOError as e:
            print(f"Error writing {filepath}: {e}", file=sys.stderr)


def cmd_decode(encoded_str: str) -> None:
    """Decode an import string for debugging."""
    # Strip version prefix if present
    parts = encoded_str.split(" ", 1)
    if len(parts) == 2 and parts[0].isdigit():
        version = int(parts[0])
        print(f"Version: {version}")
        encoded_str = parts[1]

    # Huffman decode
    try:
        decoded = decode_string(encoded_str)
    except Exception as e:
        print(f"Error decoding: {e}", file=sys.stderr)
        sys.exit(1)

    # Label separator tokens for readability
    SEP_LABELS = {
        "\x7f": "<SEP1>",
        "\x04": "<SEP2>",
        "\x05": "<SEP3>",
        "\x06": "<SEP4>",
    }
    labeled = []
    for ch in decoded:
        if ch in SEP_LABELS:
            labeled.append(SEP_LABELS[ch])
        elif ch.isprintable():
            labeled.append(ch)
        else:
            labeled.append(f"<0x{ord(ch):02X}>")

    print("Decoded:")
    print("".join(labeled))


def main() -> None:
    """Parse CLI arguments and dispatch."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="sst_gen",
        description="SST script generator — generate clipboard import strings",
    )
    parser.add_argument("file", nargs="?", help="Path to .sst file")
    parser.add_argument("--copy", action="store_true", help="Copy to clipboard")
    parser.add_argument("--regen-all", metavar="DIR", help="Regenerate all .sst in directory")
    parser.add_argument("--decode", metavar="ENCODED", help="Decode an import string")

    args = parser.parse_args()

    if args.regen_all:
        cmd_regen_all(args.regen_all)
    elif args.decode:
        cmd_decode(args.decode)
    elif args.file:
        cmd_generate(args.file, args.copy)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
