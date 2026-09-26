# Eye of the Beholder — 5e Rules Mod

A ScummVM fork that replaces Eye of the Beholder I/II's AD&D 2nd Edition
mechanics with D&D 5th Edition rules, switchable per game from the ScummVM
options dialog ("5th Edition rules (mod)" under the Engine tab).

Everything lives in `engines/kyra/`. The original game data files are
required (GOG's *Forgotten Realms: The Archives — Collection One* works).

## What v0.1 changes

| Mechanic | AD&D (original) | 5e (this mod) |
|---|---|---|
| Party attack roll | d20 ≥ THAC0 − AC, THAC0 from class/level table | d20 + proficiency + STR/DEX mod (+ magic weapon) ≥ 20 − AC |
| Natural 1 / 20 | 1 always misses, 20 always hits (mostly) | Same, explicitly |
| Advantage | — | Attacking a monster that faces away from the party, or while invisible |
| Monster attack roll | d20 ≥ monster THAC0 − char AC, flat −2 for Blur / Prot. from Evil | d20 + (20 − THAC0) ≥ 20 − AC; Blur / Prot. from Evil give **disadvantage**; Prayer subtracts 1d4 like Bless |
| Saving throws (party) | Class/level table lookup, race bonuses | d20 + ability mod (+ proficiency if the class has that save) ≥ DC 12 + dungeon depth/4 |
| Save categories | Para/Poison/Death, Rod/Staff/Wand, Petrify/Poly, Breath, Spell | → CON, DEX, CON, DEX, WIS |
| Save proficiencies | — | Fighter STR/CON · Ranger STR/DEX · Paladin WIS/CHA · Mage INT/WIS · Cleric WIS/CHA · Thief DEX/INT (multiclass = union) |
| Monster saves vs. party spells | Table by monster level | d20 + level/2 ≥ 8 + party proficiency + 3 |

Proficiency bonus is the standard 5e progression: +2 at levels 1–4, +3 at 5–8, +4 at 9–12, +5 at 13–16.
Ability modifier is floor((score − 10) / 2); exceptional strength (18/xx) counts as 18.

The AD&D "Faithful rules" option still stacks on top (e.g. elven +1 with swords/bows).

## Where the code is

- `engines/kyra/engine/eobcommon.cpp`
  - `characterAttackHitTest` — party to-hit
  - `monsterAttackHitTest` — monster to-hit
  - `trySavingThrow` — all saves
  - `abilityMod5e`, `profBonus5e`, `rollD20_5e`, `isSaveProficient5e` — helpers, near `getMonsterAcHitChanceModifier`
- `engines/kyra/engine/eobcommon.h` — `_config5eRules` flag and helper declarations
- `engines/kyra/metaengine.cpp`, `detection.h`, `detection_tables.h` — the options-dialog checkbox (`rules5e` in scummvm.ini)

Run with `--debuglevel=2` to see every attack/save roll logged (`5e attack: d20=14 +5 vs AC 13`).

## Building

```
./configure --disable-all-engines --enable-engine=kyra,eob,lol --enable-release
make -j$(nproc)
```

Needs `libsdl2-dev`. The ScummVM engine also needs `kyra.dat` from `dists/engine-data/`
next to the binary (or in the extrapath).

## Roadmap

- v0.2 — Death saves instead of instant death below 0 HP; short rest (hit dice) vs. long rest
- v0.3 — Spell slots + cantrips: prepared casting replaces per-slot memorization, Magic Missile / Fire Bolt at will
- v0.4 — Level-up: hit dice by class (d10 fighter, d8 cleric/thief, d6 mage) with CON mod; ASI at 4/8/12
- Later — Turn-based mode toggle, monster stat rescaling to 5e bounded accuracy, new campaign on the original tilesets
