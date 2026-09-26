# Eye of the Beholder — level exporter

Branch `eob-export`. Adds two debug-console commands to ScummVM's EOB engine that dump the
campaign to JSON, so the levels, items, monsters and scripts can be rebuilt in another engine
(the isometric / turn-based rebuild). Nothing here changes gameplay.

The data comes straight out of the engine's own loaders — it's exactly what the game plays,
not a re-implementation of the file formats.

## Use

1. Build (`./configure --disable-all-engines --enable-engine=kyra,eob,lol && make`), run EOB1 or EOB2
   with your own game data, start or load a game.
2. Press **Ctrl+Alt+D** for the console.
3. `export_level` writes `eob1_level03_sub0.json` (current level) to ScummVM's working directory.
   `export_level foo.json` picks the name.
4. `export_campaign` loads every level in turn (1–12 for EOB1, 1–16 for EOB2, or `export_campaign N`)
   and writes one file each. It restores your level afterwards, but **don't save the game after
   running it — reload instead**; loading levels has side effects on monster state.
5. `python3 devtools/eob_export/eob_map.py eob1_level01_sub0.json` prints a summary and an ASCII map;
   `--grid` writes `*.grid.json`, a flat 32×32 passability grid with doors, triggers, monster and item
   positions — the shape an importer wants.

Sub-levels (EOB2 has several) are only exported for the sub you're standing in with `export_level`;
`export_campaign` does sub 0. Walk into the sub-level and run `export_level` for the rest.

## What's in the JSON

| Key | Contents |
|---|---|
| `game`, `level`, `sub`, `wallset` | Identification; `wallset` is the graphics file name (e.g. `SEWER`, `DUNGEON`) — tells you which tile kit the level uses |
| `wallTypes[w]` | For each wall-type index: engine `flags` (bit 0 passable, bit 3 door) and `special` (1 = door) |
| `cells[1024]` | Block `b = y*32 + x`: `w` = wall type on [N, E, S, W]; `f` = flags (`f >> 3` = trigger mask: which events fire a script here); `s` = script offset for this cell (0 = none) |
| `items[]` | Every item lying on this level: unidentified/identified names, type, block, position in cell (0–3 = corners, 4 = centre), magic value, and the item type's AC/damage dice/allowed classes |
| `monsters[]` | Live monsters: type, block, cell position, facing, hp, plus the type's AC, THAC0, level, hit dice, attacks, damage dice, immunity/caps flags, XP |
| `script` | The level's INF bytecode as hex, plus the opcode name table and `commandMin` so it can be disassembled: opcodes are negative bytes `cmd`, index `-(cmd+1)` into `opcodes` |

Wall-type indices are per wall set; open the wall set's `.VMP`/`.VCN` in ScummVM if you need to know
what index 17 *looks* like. For a rebuild you mostly need "wall / door / open / special", which
`eob_map.py` derives.

## What it does not do (yet)

- **Disassemble scripts.** Operand lengths live inside each opcode handler in `script/script_eob.cpp`,
  so a decoder needs a per-opcode length table. The raw bytes plus opcode names are exported so that
  can be written outside the engine.
- **Export graphics.** Wall sets, monster sprites and item icons stay in the game files; the rebuild
  needs new art anyway.
- **Dialogue / text.** Strings are referenced by index from the script; the string table is in
  `kyra.dat` / the level file and isn't dumped yet.

## Code

- `engines/kyra/gui/debugger.cpp` — `exportLevelJson`, `cmdExportLevel`, `cmdExportCampaign`
- `engines/kyra/script/script_eob.h` — read-only accessors on `EoBInfProcessor`
- `devtools/eob_export/eob_map.py` — viewer / grid converter
