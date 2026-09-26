# Testing the EOB 5e mod

## 1. Setup (once)

1. Buy/install *Forgotten Realms: The Archives — Collection One* (GOG). You need the folder with
   `EOBDATA*.PAK`, `LEVEL*.INF/MAZ` etc. for EOB1, and the EOB2 folder likewise.
2. Build the fork:
   ```
   git clone https://github.com/scummvm/scummvm.git && cd scummvm
   git am eob-5e-rules-v0.4.patch          # or check out the eob-5e-rules branch
   ./configure --disable-all-engines --enable-engine=kyra,eob,lol --enable-release
   make -j$(nproc)
   ```
   On Windows use the MSYS2/mingw toolchain or the Visual Studio projects under `devtools/create_project`;
   on macOS `brew install sdl2` then the same configure/make.
3. Copy `dists/engine-data/kyra.dat` next to the binary (or set Extra Path to that folder in the
   launcher's Paths tab).
4. Launch, **Add Game**, point at the EOB1 folder. Then Edit Game → **Engine** tab → tick
   **"5th Edition rules (mod)"**. Leave "Faithful AD&D rules" as you like; they stack.
5. Run with roll logging on so you can see the math:
   ```
   ./scummvm --debuglevel=2 --debugflags=Main eob
   ```
   (`eob2` for Darkmoon.) Every attack and save prints `5e attack: d20=14 +5 vs AC 13` or
   `5e save: d20=… +… vs DC …` to the terminal.

## 2. The debug console

Press **Ctrl+Alt+D** in game. Commands added by the mod:

| Command | What it does |
|---|---|
| `show_5e` | One line per character: level, hp, AC (both scales), proficiency, stats, Hit Dice left, death-save tally |
| `set_hp <c> <hp>` | Set current hp directly (no death-save logic). Characters are numbered 0–5, top-left to bottom-right |
| `damage <c> <n>` | Deal n damage *through the real damage path* — death saves, massive damage etc. apply |
| `give_xp <c> <n>` | Add XP; triggers level-ups immediately |

Also useful from stock ScummVM: `list_monsters`, `set_position`, `open_door`.

## 3. Test checklist

Make a fresh party with a fighter, cleric, mage and thief so every rule branch gets exercised.
Save right after creation so you can reload for each block.

### Sanity: toggle actually does something
- [ ] `show_5e` reports `5e rules: ON`.
- [ ] Turn the option **off**, restart, hit a monster: terminal shows no `5e attack:` lines.
- [ ] Turn it on again: lines appear, and the +N in the log = proficiency (+2 at lvl 1) + STR mod
      (+3 for STR 16–17, +4 for 18) + magic weapon bonus.

### Attack rolls (level 1 sewer)
- [ ] Fighter with STR 17 vs a kobold (AD&D AC 7 → 5e AC 13): expect ~65% hit rate over 20 swings
      (needs 8+ on d20 with +5). With AD&D rules the same swing needs 13+ (~40%).
- [ ] Walk *behind* a monster (it's facing away) and attack: log shows two d20s picked max, i.e.
      hits noticeably more often. Cast Invisibility on the attacker for the same effect.
- [ ] Natural 20 hits a Beholder-level AC; natural 1 misses a kobold.
- [ ] Get hit by a monster while under Blur or Protection from Evil: their hit rate drops a lot
      (disadvantage), not just by 10%.

### Saving throws
- [ ] Walk into the poison-dart traps on level 1 / get bitten by a giant spider. Log shows
      `5e save: … vs DC 12` (DC 13 from level 4, 14 from level 8). Fighter and cleric should have
      +2 more than mage/thief on CON (poison) saves; the mage's WIS (spell) save should be the good one.
- [ ] Cast Hold Person / Fear on a monster: it now rolls d20 + level/2 vs 13 (8 + 2 + 3 at party
      level 1–4). Higher-level monsters resist more.

### Death saves
- [ ] `damage 0 <hp-1>` then `damage 0 1`: fighter drops to **0** (not negative), message
      "falls unconscious and is dying!", portrait shows 0.
- [ ] Wait ~6 s per round. You'll see "clings to life (n of 3)" / "slips closer to death (n of 3)"
      until either "is stable." or "has died." — `show_5e` tracks the tally.
- [ ] While dying, `damage 0 1`: hp stays 0, one more failure. Three total = dead.
- [ ] While dying, cast Cure Light Wounds on them: they get up with the healed amount, `show_5e`
      shows 0/0 death saves, no further messages.
- [ ] Massive damage: fighter with 12 max hp at 12 hp, `damage 0 24` → straight to dead (−10).
- [ ] Reload a save where someone was at 0: death saves restart (message appears again).
- [ ] With the option **off**, `damage 0 <lots>` still gives the old −1…−9 unconscious behaviour.

### Rests
- [ ] Injure the party (`set_hp` everyone to 3), camp. Every hour each injured character prints
      "spends a Hit Die and recovers N hp" (N = d10/d8/d6 + CON mod, min 1) and `show_5e` shows
      Hit Dice decreasing.
- [ ] Rest 8 hours: everyone at full hp, Hit Dice back up by half level (level 1: back to 1).
- [ ] A character with 0 Hit Dice left gets nothing per hour until the 8-hour mark.
- [ ] Dying (0 hp) characters are healed by rests too.
- [ ] Starvation, poison ticks, spell memorisation during rest all still work as before.

### Spells
- [ ] Memorise 2× Magic Missile, 1× Armor. Cast Magic Missile repeatedly: it never leaves the
      book, and Armor is untouched. (Cantrip.)
- [ ] Memorise 1× Burning Hands, 1× Shield, 1× Armor. Cast Shield: **Shield stays**, Armor (the
      last other level-1 spell) turns grey. Cast Shield again: Burning Hands goes. Cast a third time:
      Shield itself goes. The list selection stays on Shield throughout, no crash on the page 2
      (7th/8th entry) boundary — memorise 8 spells to check that.
- [ ] Cleric equivalents with Bless / Cure Light Wounds.
- [ ] Casting from a scroll consumes the scroll exactly as before.
- [ ] Rest: expended entries come back one at a time as before.

### Level-up
- [ ] `give_xp 0 2000` (fighter level 2): hp max goes up by exactly 6 + CON mod (CON 16 → +9),
      and `show_5e` Hit Dice +1. Mage: +4 + CON mod. Cleric/thief: +5 + CON mod.
- [ ] `give_xp 0 8000`: level 4 → message "X's Strength rises to N." STR +2 (cap 18). A mage gets
      INT, cleric WIS, thief DEX. If the stat is already 18, CON goes up instead.
- [ ] Multiclass fighter/mage: each class level-up prints once; hp grows by the average of the two
      shares (no ping-pong or double gain — compare to the "faithful rules" behaviour).
- [ ] Level 8 and 12 also trigger an ASI; levels 5/6/7 don't.

### Regression (option off)
- [ ] Play 10 minutes of level 1 with the option **off**: nothing above should be observable;
      original tables apply. This is the "did I break stock ScummVM" check.

## 4. Reporting

For anything that looks wrong, the useful bits are: the terminal log around the moment (the
`5e …` lines), `show_5e` output, and whether "Faithful AD&D rules" was also on.
