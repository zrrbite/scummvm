#!/usr/bin/env python3
"""Inspect and convert Eye of the Beholder level exports (from ScummVM's `export_level` console command).

Usage:
  eob_map.py LEVEL.json            ASCII render + summary
  eob_map.py LEVEL.json --grid     write LEVEL.grid.json: {"passable": [[...]], "doors": [...], "triggers": [...]}
  eob_map.py LEVEL.json --all      both

Block index = y * 32 + x. Wall sides are [north, east, south, west] and store a wall-type index into
`wallTypes`; wallTypes[w].flags bit 0 = passable, bit 3 = door, `special` 1 = door.
"""
import json
import sys


def load(path):
    with open(path) as f:
        return json.load(f)


def wall_kind(level, w):
    wt = level["wallTypes"][w]
    if w == 0:
        return "open"
    if wt["special"] == 1 or (wt["flags"] & 8):
        return "door"
    if wt["flags"] & 1:
        return "passable"  # illusion walls, pressure plates etc.
    return "wall"


def render(level):
    cells = level["cells"]
    monsters = {m["block"]: m for m in level["monsters"]}
    items = {}
    for it in level["items"]:
        items.setdefault(it["block"], []).append(it)
    rows = []
    for y in range(32):
        line = []
        for x in range(32):
            c = cells[y * 32 + x]
            kinds = [wall_kind(level, w) for w in c["w"]]
            solid = all(k == "wall" for k in kinds)
            if solid:
                ch = "#"
            elif (y * 32 + x) in monsters:
                ch = "M"
            elif (y * 32 + x) in items:
                ch = "i"
            elif any(k == "door" for k in kinds):
                ch = "+"
            elif c["s"]:
                ch = "?"  # scripted trigger
            else:
                ch = "."
            line.append(ch)
        rows.append("".join(line))
    return "\n".join(rows)


def summary(level):
    out = [f"{level['game']} level {level['level']} sub {level['sub']}  wallset {level['wallset']}"]
    out.append(f"  {len(level['items'])} items, {len(level['monsters'])} monsters, "
               f"{sum(1 for c in level['cells'] if c['s'])} scripted cells, "
               f"script {len(level['script']['bytes']) // 2} bytes")
    types = {}
    for m in level["monsters"]:
        p = m["props"]
        types.setdefault(m["type"], [0, p])
        types[m["type"]][0] += 1
    for t, (n, p) in sorted(types.items()):
        out.append(f"  monster type {t:2d} x{n:<2d} AC {p['ac']:3d} THAC0 {p['thac0']:2d} lvl {p['level']:2d} hp {p['hpDice']:>8s} "
                   f"atk {p['attacks']} dmg {p['dmg'][0]} xp {p['xp']}")
    names = {}
    for it in level["items"]:
        names[it["nameIdentified"] or it["name"]] = names.get(it["nameIdentified"] or it["name"], 0) + 1
    for n, c in sorted(names.items()):
        out.append(f"  item {c:2d}x {n}")
    return "\n".join(out)


def grid(level):
    cells = level["cells"]
    passable = [[0] * 32 for _ in range(32)]
    doors, triggers = [], []
    for y in range(32):
        for x in range(32):
            c = cells[y * 32 + x]
            kinds = [wall_kind(level, w) for w in c["w"]]
            passable[y][x] = 0 if all(k == "wall" for k in kinds) else 1
            for side, k in enumerate(kinds):
                if k == "door":
                    doors.append({"x": x, "y": y, "side": side, "wallType": c["w"][side]})
            if c["s"]:
                triggers.append({"x": x, "y": y, "flags": c["f"] >> 3, "scriptOffset": c["s"]})
    return {
        "game": level["game"], "level": level["level"], "sub": level["sub"], "wallset": level["wallset"],
        "width": 32, "height": 32, "passable": passable, "doors": doors, "triggers": triggers,
        "monsters": [{"x": m["block"] % 32, "y": m["block"] // 32, "type": m["type"], "hp": m["hpMax"]} for m in level["monsters"]],
        "items": [{"x": it["block"] % 32, "y": it["block"] // 32, "name": it["nameIdentified"] or it["name"], "type": it["type"]} for it in level["items"]],
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    path = sys.argv[1]
    level = load(path)
    want_grid = "--grid" in sys.argv or "--all" in sys.argv
    want_text = not ("--grid" in sys.argv) or "--all" in sys.argv
    if want_text:
        print(summary(level))
        print()
        print(render(level))
    if want_grid:
        out = path.rsplit(".", 1)[0] + ".grid.json"
        with open(out, "w") as f:
            json.dump(grid(level), f, indent=1)
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
