#!/usr/bin/env python3
"""Golden self-check for module01-01 affinity metrics (Track A).

    python3 examples/affinity_check.py                     # check the reference
    python3 examples/affinity_check.py --show              # also print every ranking
    python3 examples/affinity_check.py --impl my_aff.py    # check YOUR functions

Your file may define any of:
    affinity_edge_weight(edges)                 -> [(u, v, score), ...] sorted
    affinity_shared_neighbors(nodes, edges)     -> [(u, v, score), ...] sorted
    affinity_pin_count(nodes, hyperedges)       -> [(u, v, score), ...] sorted
with edges as (u, v, w) tuples (u < v) and hyperedges as {"pins": [...], "w": w}.
Sorted means: score descending, then u, then v alphabetically.
Functions you have not written yet are reported as SKIP.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "common"))

from graphutil import (  # noqa: E402
    affinity_edge_weight,
    affinity_shared_neighbors,
    load_graph,
)


def _ranked(scores: dict) -> list:
    return sorted(((u, v, s) for (u, v), s in scores.items()), key=lambda t: (-t[2], t[0], t[1]))


def affinity_pin_count(nodes, hyperedges):
    """Reference pin-count (clique-model) affinity for multi-pin nets.

    score(u,v) = sum over nets e containing both u and v of  w(e) / (|e| - 1)

    A 2-pin net gives its full weight; a 5-pin net spreads it thin
    (w/4 per pair). Wide nets such as reset or enable should not glue
    every cell they touch together.
    """
    scores: dict = {}
    for h in hyperedges:
        pins = sorted(set(h["pins"]))
        if len(pins) < 2:
            continue
        share = h.get("w", 1) / (len(pins) - 1)
        for u, v in combinations(pins, 2):
            scores[(u, v)] = scores.get((u, v), 0.0) + share
    return _ranked(scores)


def raw_net_count(nodes, hyperedges):
    """Naive version for comparison: every shared net adds its full weight."""
    scores: dict = {}
    for h in hyperedges:
        for u, v in combinations(sorted(set(h["pins"])), 2):
            scores[(u, v)] = scores.get((u, v), 0.0) + h.get("w", 1)
    return _ranked(scores)


def load_netlist(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {"nodes": data["nodes"], "hyperedges": data["hyperedges"]}


def fmt(r) -> str:
    return ", ".join(f"{u}-{v}:{s:g}" for u, v, s in r)


def same(got, want) -> bool:
    return len(got) == len(want) and all(
        g[0] == w[0] and g[1] == w[1] and abs(g[2] - w[2]) < 1e-9 for g, w in zip(got, want)
    )


# ---------------- goldens (also printed in EXAMPLES.md) ----------------
TINY_EDGE = [("A", "B", 5), ("D", "E", 5), ("B", "C", 4), ("C", "D", 2), ("A", "C", 1), ("C", "E", 1)]
TINY_SHARED = [
    ("A", "B", 6), ("D", "E", 6), ("A", "C", 5), ("B", "C", 5), ("C", "D", 3),
    ("C", "E", 3), ("B", "D", 2), ("A", "D", 1), ("A", "E", 1), ("B", "E", 1),
]
PRIORITY_EDGE_TOP = ("X", "Y", 5)
PRIORITY_SHARED_TOP = ("P", "Q", 8)
NET_PIN_TOP = ("E", "F", 1.0)
NET_PIN_AB = 0.5  # two 5-pin nets: 1/4 + 1/4


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--impl", help="your .py file with affinity functions")
    ap.add_argument("--show", action="store_true", help="print every ranking")
    args = ap.parse_args()

    fns = {
        "edge": affinity_edge_weight,
        "shared": affinity_shared_neighbors,
        "pin": affinity_pin_count,
    }
    name = "reference"
    if args.impl:
        spec = importlib.util.spec_from_file_location("learner_aff", args.impl)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fns = {
            "edge": getattr(mod, "affinity_edge_weight", None),
            "shared": getattr(mod, "affinity_shared_neighbors", None),
            "pin": getattr(mod, "affinity_pin_count", None),
        }
        name = args.impl
    print(f"checking {name}")

    tiny = load_graph(HERE / "tiny_graph.json")
    prio = load_graph(HERE / "priority_graph.json")
    net = load_netlist(HERE / "tiny_netlist.json")

    results = []

    def check(label, key, run, ok_fn, expect):
        fn = fns[key]
        if fn is None:
            results.append(None)
            print(f"SKIP  {label}   (function not defined yet)")
            return
        got = run(fn)
        ok = ok_fn(got)
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + ("" if ok else f"\n        got:      {fmt(got)}\n        expected: {expect}"))
        if args.show:
            print(f"        {fmt(got)}")

    # Edges are fed in reverse file order, so a missing tie-break is caught.
    check("tiny graph, edge weight: 6 pairs in golden order", "edge",
          lambda f: f(list(reversed(tiny["edges"]))), lambda g: same(g, TINY_EDGE), fmt(TINY_EDGE))
    check("tiny graph, shared neighbors: 10 pairs in golden order", "shared",
          lambda f: f(tiny["nodes"], tiny["edges"]), lambda g: same(g, TINY_SHARED), fmt(TINY_SHARED))
    check("priority graph, edge weight: first merge X-Y @ 5", "edge",
          lambda f: f(prio["edges"]), lambda g: same(g[:1], [PRIORITY_EDGE_TOP]), fmt([PRIORITY_EDGE_TOP]))
    check("priority graph, shared neighbors: first merge P-Q @ 8", "shared",
          lambda f: f(prio["nodes"], prio["edges"]), lambda g: same(g[:1], [PRIORITY_SHARED_TOP]),
          fmt([PRIORITY_SHARED_TOP]))
    check("netlist, pin-count: first merge E-F @ 1, A-B only 0.5", "pin",
          lambda f: f(net["nodes"], net["hyperedges"]),
          lambda g: same(g[:1], [NET_PIN_TOP])
          and any(u == "A" and v == "B" and abs(s - NET_PIN_AB) < 1e-9 for u, v, s in g),
          "E-F:1 first, A-B:0.5")

    if args.show:
        print(f"\nnetlist, raw net count (for comparison): {fmt(raw_net_count(net['nodes'], net['hyperedges']))}")

    fails = sum(r is False for r in results)
    skips = sum(r is None for r in results)
    if fails:
        print(f"{fails} check(s) differ")
    else:
        print("all goldens match" + (f" ({skips} skipped)" if skips else ""))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
