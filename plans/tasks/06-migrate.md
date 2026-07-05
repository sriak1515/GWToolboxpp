# Task 6: Migrate Existing Files

**Depends on:** Task 5 (CLI working)  
**Output:** Updated `scripts/sst/*.sst` files in new format with correct import strings

## What to do

This is a one-time operation. Write a short standalone script (or do it by hand), not part of `sst_gen.py`.

## Steps

1. Write a one-time migration script or convert each file by hand
2. Run `python3 sst_gen.py --regen-all scripts/sst/` to generate correct import strings
3. Manually review each file
4. Run the test suite to verify

## Files to migrate (9 total)

- `dark-aura-maintainer.sst`
- `dervish-attack-optimizer.sst` (newest, added 2026-07-05)
- `drunken-master-maintainer.sst`
- `flag-formation-auto.sst`
- `flag-narrow-formation.sst`
- `flag-wide-formation.sst`
- `soh-maintainer.sst`
- `soul-taker-self-buff-maintainer.sst`
- `st-combat-prep.sst`

## What changes per file

| Old syntax | New syntax |
|------------|-----------|
| `when {` / `}` | `when:` (indent-based) |
| `then {` / `}` | `then:` (indent-based) |
| `Conditioned(cond: X, then: { ... }, else: { ... })` | `if X: ... else: ...` (indent-based) |
| `PlayerHasBuff(Dark_Aura)` | `PlayerHasBuff(id: Dark_Aura)` |
| `Throttle(5000ms)` | `Throttle(ms: 5000)` |

## Verification

After migration, `python3 sst_gen.py --dry-run <file>` must produce the exact same import string as the old tool did for each file. The binary output must not change.

Note: `dervish-attack-optimizer.sst` is new and won't have an old import string to compare against. Verify it generates a valid import string that can be decoded back to the same binary.
