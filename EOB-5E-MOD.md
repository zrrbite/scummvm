# Eye of the Beholder — 5e Rules Mod

A ScummVM fork that replaces Eye of the Beholder I/II's AD&D 2nd Edition
mechanics with D&D 5th Edition rules, switchable per game from the ScummVM
options dialog ("5th Edition rules (mod)" under the game's Engine tab).

Everything lives in `engines/kyra/`. The original game data files are
required (GOG's *Forgotten Realms: The Archives — Collection One* works).
See `TESTING.md` for setup and a per-feature test checklist.

## What changes, by version

### v0.1 — Attack rolls and saving throws

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

Proficiency bonus: +2 at levels 1–4, +3 at 5–8, +4 at 9–12, +5 at 13–16.
Ability modifier: floor((score − 10) / 2); exceptional strength (18/xx) counts as 18.
The "Faithful AD&D rules" option still stacks on top (e.g. elven +1 with swords/bows).

### v0.2 — Death saves and rests

- Dropping to 0 hp no longer means −1…−9 "unconscious". The character is at **0 hp and dying**.
  Every round (~6 s) they roll a death save: 10+ is a success, 9− a failure, natural 1 counts as
  two failures, natural 20 = back up with 1 hp. Three successes = **stable** (stays at 0 hp until
  healed); three failures = dead. Messages appear in the text window.
- Damage taken while at 0 hp does not lower hp; it adds a failed death save (and un-stabilises).
- **Massive damage**: if the damage that drops you to 0 has enough left over to equal your max hp,
  you die outright.
- Any healing on a dying character clears the death-save counters.
- **Short rest**: each hour of camping, every injured character automatically spends one Hit Die
  (d10 fighter types, d8 cleric/thief, d6 mage) + CON mod. You start with one die per level.
- **Long rest**: every 8 hours of camping, full hp and half your Hit Dice (min 1) come back.
  Replaces the old +1 hp per 8 hours.
- Hit dice and death-save counters are per session, not stored in saves. Loading a game with a
  character at 0 hp restarts their death saves from zero.

### v0.3 — Cantrips and flexible spell slots

- **Magic Missile is a cantrip**: it never leaves the spellbook when cast.
- **Flexible slots**: casting a prepared spell keeps that spell in the book and expends one
  *other* prepared entry of the same level (a duplicate of the same spell first, otherwise the
  last other spell of that level; the spell itself only when it is the last one). Net effect: the
  entries you memorise for a level act as slots, and any prepared spell of that level can use them.
- Scrolls and the memorise/pray UI are unchanged.

### v0.4 — Level-up

- Hp per level is the 5e fixed average by class (fighter/paladin/ranger 6, cleric/thief 5, mage 4)
  + CON mod, min 1. Multiclass characters get each class's share via the same dividend scheme the
  "faithful rules" option uses, so no round-off drift.
- +1 Hit Die per level (for short rests).
- **Ability Score Improvement** at levels 4, 8, 12, 16: +2 to the class's primary ability (STR for
  fighter types, INT mage, WIS cleric, DEX thief), capped at 18, spilling into CON when maxed.

## Where the code is

- `engines/kyra/engine/eobcommon.cpp`
  - `characterAttackHitTest`, `monsterAttackHitTest`, `trySavingThrow` — rolls
  - `inflictCharacterDamage`, `modifyCharacterHitpoints` — death-save entry/exit
  - `startDying5e`, `deathSaveTick5e`, `deathSaveFail5e`, `killCharacter5e`, `reviveCheck5e`
  - `hitDieSize5e`, `resetHitDice5e`, `spendHitDie5e`, `levelUp5e`
  - `abilityMod5e`, `profBonus5e`, `rollD20_5e`, `isSaveProficient5e`
- `engines/kyra/engine/timer_eob.cpp` — character event 13 = death-save tick
- `engines/kyra/engine/magic_eob.cpp` — `castSpell` (cantrip / flexible slot), `isCantrip5e`
- `engines/kyra/gui/gui_eob.cpp` — `restParty` (short/long rest blocks)
- `engines/kyra/gui/saveload_eob.cpp` — per-session state reset on load
- `engines/kyra/gui/debugger.cpp` — `set_hp`, `damage`, `give_xp`, `show_5e` console commands
- `engines/kyra/engine/eobcommon.h` — `_config5eRules` and declarations
- `engines/kyra/metaengine.cpp`, `detection.h`, `detection_tables.h` — the options checkbox (`rules5e` in scummvm.ini)

## Building

```
./configure --disable-all-engines --enable-engine=kyra,eob,lol --enable-release
make -j$(nproc)
```

Needs `libsdl2-dev`. The binary needs `kyra.dat` from `dists/engine-data/` in its extrapath.

## Tuning knobs

- Early game feels easier than AD&D because of bounded accuracy. `targetAC = 20 - armorClass`
  in `characterAttackHitTest` is the knob; `22 -` restores roughly AD&D hit rates.
- Save DC: `12 + _currentLevel / 4` in `trySavingThrow`.
- Death-save round length: `110` ticks in `startDying5e` / `deathSaveTick5e`.
- Cantrip list: `isCantrip5e`.

## Still to do

- Show remaining Hit Dice / death-save pips in the character sheet (currently console only)
- Concentration for buff spells; upcasting
- Monster stat rescale to 5e bounded accuracy (monster AC/HP tables come from kyra.dat)
- Turn-based mode toggle; new campaign on the original tilesets
