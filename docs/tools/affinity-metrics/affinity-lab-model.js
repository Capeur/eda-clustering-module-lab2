/**
 * affinity-lab-model.js — pure state + rules for the Lab 02 affinity lab
 * (no DOM, so it can be unit-tested in Node).
 *
 * Mirrors Track A: courses/learn_clustering/common/graphutil.py (edge, shared)
 * and module01-01 examples/affinity_check.py (pin-count, raw net count).
 * Ranking order everywhere: score descending, then u, then v.
 */
import { TINY_GRAPH, affinityEdgeWeight, affinitySharedNeighbors } from "../../assets/clustering-core.js";

export const PRIORITY_GRAPH = {
  nodes: ["P", "Q", "R", "X", "Y"],
  edges: [
    { u: "P", v: "Q", w: 4 },
    { u: "P", v: "R", w: 4 },
    { u: "Q", v: "R", w: 4 },
    { u: "X", v: "Y", w: 5 },
  ],
};

export const TINY_NETLIST = {
  nodes: ["A", "B", "C", "D", "E", "F"],
  nets: [
    { id: "en", pins: ["A", "B", "C", "D", "E"], w: 1 },
    { id: "rst", pins: ["A", "B", "C", "D", "E"], w: 1 },
    { id: "n1", pins: ["E", "F"], w: 1 },
  ],
};

export const LAYOUTS = {
  starter: { A: { x: 90, y: 80 }, B: { x: 220, y: 60 }, C: { x: 160, y: 160 }, D: { x: 280, y: 200 }, E: { x: 120, y: 240 } },
  priority: { P: { x: 80, y: 60 }, Q: { x: 80, y: 260 }, R: { x: 240, y: 160 }, X: { x: 380, y: 80 }, Y: { x: 520, y: 240 } },
  netlist: { A: { x: 60, y: 60 }, B: { x: 200, y: 40 }, C: { x: 320, y: 90 }, D: { x: 300, y: 230 }, E: { x: 160, y: 250 }, F: { x: 110, y: 380 } },
};

export const GRAPHS = {
  starter: { label: "Starter graph (A–E)", kind: "graph", data: TINY_GRAPH },
  priority: { label: "Priority graph (triangle + lone pair)", kind: "graph", data: PRIORITY_GRAPH },
  netlist: { label: "Tiny netlist (wide nets)", kind: "netlist", data: TINY_NETLIST },
};

export const SCORES = {
  edge: { label: "Edge weight", kind: "graph" },
  shared: { label: "Shared neighbors + edge", kind: "graph" },
  pin: { label: "Pin-count w/(|e|−1)", kind: "netlist" },
  raw: { label: "Raw net count", kind: "netlist" },
};

export const pairKey = (u, v) => (u < v ? `${u}–${v}` : `${v}–${u}`);
const sortRank = (arr) =>
  arr.sort((x, y) => y[2] - x[2] || (x[0] < y[0] ? -1 : x[0] > y[0] ? 1 : 0) || (x[1] < y[1] ? -1 : 1));

/* ---------------- state ---------------- */

export function createState(graphKey = "starter", scoreKey = null) {
  const g = GRAPHS[graphKey];
  const data = JSON.parse(JSON.stringify(g.data));
  const s = {
    graphKey,
    scoreKey: scoreKey || (g.kind === "netlist" ? "pin" : "edge"),
    nodes: data.nodes,
    edges: data.edges || [],
    nets: data.nets || [],
    baseWeights: Object.fromEntries((data.edges || []).map((e) => [pairKey(e.u, e.v), e.w])),
    answers: {}, // "score|pair" -> { value, ok }
    revealedPairs: {}, // "score|pair" -> true (breakdown shown: answer no longer counts)
    rankingRevealed: {}, // score -> true
    myRanking: [], // [pairKey, ...] for the current score
  };
  return s;
}

export const cloneState = (s) => JSON.parse(JSON.stringify(s));

export function setScore(s, scoreKey) {
  const n = cloneState(s);
  n.scoreKey = scoreKey;
  n.myRanking = [];
  return n;
}

/* ---------------- scoring ---------------- */

function pinCount(nodes, nets) {
  const sc = {};
  for (const h of nets) {
    const pins = [...new Set(h.pins)].sort();
    if (pins.length < 2) continue;
    const share = (h.w ?? 1) / (pins.length - 1);
    for (let i = 0; i < pins.length; i++)
      for (let j = i + 1; j < pins.length; j++) {
        const k = `${pins[i]}|${pins[j]}`;
        sc[k] = (sc[k] || 0) + share;
      }
  }
  return sortRank(Object.entries(sc).map(([k, v]) => [...k.split("|"), v]));
}

function rawCount(nodes, nets) {
  const sc = {};
  for (const h of nets) {
    const pins = [...new Set(h.pins)].sort();
    for (let i = 0; i < pins.length; i++)
      for (let j = i + 1; j < pins.length; j++) {
        const k = `${pins[i]}|${pins[j]}`;
        sc[k] = (sc[k] || 0) + (h.w ?? 1);
      }
  }
  return sortRank(Object.entries(sc).map(([k, v]) => [...k.split("|"), v]));
}

/** Full ranking [[u, v, score], ...] for the current graph + score. */
export function ranking(s, scoreKey = s.scoreKey) {
  const edges = s.edges.filter((e) => e.w > 0);
  if (scoreKey === "edge") return sortRank(affinityEdgeWeight(edges).map((r) => [...r]));
  if (scoreKey === "shared") return sortRank(affinitySharedNeighbors(s.nodes, edges).map((r) => [...r]));
  if (scoreKey === "pin") return pinCount(s.nodes, s.nets);
  return rawCount(s.nodes, s.nets);
}

export function scoreOf(s, u, v, scoreKey = s.scoreKey) {
  const k = pairKey(u, v);
  const hit = ranking(s, scoreKey).find((r) => pairKey(r[0], r[1]) === k);
  return hit ? hit[2] : 0;
}

export function weightOf(s, u, v) {
  const e = s.edges.find((x) => pairKey(x.u, x.v) === pairKey(u, v));
  return e ? e.w : 0;
}

/** Step-by-step explanation of one pair's score (study aid). */
export function breakdown(s, u, v, scoreKey = s.scoreKey) {
  const [a, b] = u < v ? [u, v] : [v, u];
  const total = scoreOf(s, a, b, scoreKey);
  const fmt = (x) => (Number.isInteger(x) ? String(x) : String(+x.toFixed(4)));
  if (scoreKey === "edge") return [`w(${a},${b}) = ${fmt(weightOf(s, a, b))}`, `score = ${fmt(total)}`];
  if (scoreKey === "shared") {
    const lines = [`direct: w(${a},${b}) = ${fmt(weightOf(s, a, b))}`];
    for (const x of s.nodes) {
      if (x === a || x === b) continue;
      const wa = weightOf(s, a, x);
      const wb = weightOf(s, b, x);
      if (wa > 0 && wb > 0) lines.push(`via ${x}: min(w(${a},${x})=${fmt(wa)}, w(${b},${x})=${fmt(wb)}) = ${fmt(Math.min(wa, wb))}`);
    }
    lines.push(`score = ${fmt(total)}`);
    return lines;
  }
  const lines = [];
  for (const h of s.nets) {
    if (!h.pins.includes(a) || !h.pins.includes(b)) continue;
    const p = new Set(h.pins).size;
    lines.push(
      scoreKey === "pin"
        ? `net ${h.id} (${p} pins): ${fmt(h.w)}/(${p}−1) = ${fmt(h.w / (p - 1))}`
        : `net ${h.id} (${p} pins): +${fmt(h.w)}`
    );
  }
  if (!lines.length) lines.push(`no net contains both ${a} and ${b}`);
  lines.push(`score = ${fmt(total)}`);
  return lines;
}

/* ---------------- learner actions ---------------- */

/** Parse "5", "0.25", "1/4", "1/4 + 1/4". Returns NaN if unreadable. */
export function parseScore(text) {
  const t = String(text ?? "").trim();
  if (!t) return NaN;
  if (!/^[0-9+./\s]+$/.test(t)) return NaN;
  let sum = 0;
  for (const part of t.split("+")) {
    const p = part.trim();
    if (!p) return NaN;
    if (p.includes("/")) {
      const [n, d] = p.split("/").map(Number);
      if (!Number.isFinite(n) || !Number.isFinite(d) || d === 0) return NaN;
      sum += n / d;
    } else {
      const n = Number(p);
      if (!Number.isFinite(n)) return NaN;
      sum += n;
    }
  }
  return sum;
}

export function answer(s, u, v, text) {
  const value = parseScore(text);
  const n = cloneState(s);
  if (!Number.isFinite(value)) return { state: s, ok: null, msg: "Type a number such as 5, 0.5 or 1/4." };
  const truth = scoreOf(s, u, v);
  const ok = Math.abs(value - truth) < 1e-9;
  n.answers[`${s.scoreKey}|${pairKey(u, v)}`] = { value, ok };
  return { state: n, ok, msg: ok ? `Correct: ${pairKey(u, v)} = ${value}` : `Not quite: ${pairKey(u, v)} is not ${value}. Recount, or open the breakdown (study).` };
}

export function revealPair(s, u, v) {
  const n = cloneState(s);
  n.revealedPairs[`${s.scoreKey}|${pairKey(u, v)}`] = true;
  return n;
}

export function revealRanking(s) {
  const n = cloneState(s);
  n.rankingRevealed[s.scoreKey] = true;
  return n;
}

export function addToRanking(s, u, v) {
  const k = pairKey(u, v);
  if (s.myRanking.includes(k)) return { state: s, msg: `${k} is already in your ranking.` };
  const n = cloneState(s);
  n.myRanking.push(k);
  return { state: n, msg: `Added ${k} at position ${n.myRanking.length}.` };
}

export function undoRanking(s) {
  const n = cloneState(s);
  n.myRanking.pop();
  return n;
}

/** Change an existing edge's weight (or create one); weight never below 0. */
export function editWeight(s, u, v, delta) {
  if (GRAPHS[s.graphKey].kind !== "graph") return { state: s, msg: "Weights are edited on graphs, not the netlist." };
  const n = cloneState(s);
  const k = pairKey(u, v);
  let e = n.edges.find((x) => pairKey(x.u, x.v) === k);
  if (!e) {
    if (delta < 0) return { state: s, msg: `${k} has no edge to lower.` };
    const [a, b] = u < v ? [u, v] : [v, u];
    e = { u: a, v: b, w: 0 };
    n.edges.push(e);
  }
  e.w = Math.max(0, e.w + delta);
  n.edges = n.edges.filter((x) => x.w > 0 || n.baseWeights[pairKey(x.u, x.v)] != null);
  n.answers = {}; // scores changed: old answers no longer apply
  n.myRanking = [];
  return { state: n, msg: `${k} weight is now ${e.w}.` };
}

/** Edits relative to the original graph: [{pair, from, to}] and total |change|. */
export function edits(s) {
  const out = [];
  const keys = new Set([...Object.keys(s.baseWeights), ...s.edges.map((e) => pairKey(e.u, e.v))]);
  for (const k of keys) {
    const from = s.baseWeights[k] ?? 0;
    const e = s.edges.find((x) => pairKey(x.u, x.v) === k);
    const to = e ? e.w : 0;
    if (from !== to) out.push({ pair: k, from, to });
  }
  return { list: out, total: out.reduce((t, x) => t + Math.abs(x.to - x.from), 0) };
}

/* ---------------- challenge predicates (read learner state only) ---------------- */

/** Learner typed the correct value for this pair under this score, without opening its breakdown. */
export function answeredOwn(s, scoreKey, u, v) {
  const k = `${scoreKey}|${pairKey(u, v)}`;
  return !!s.answers[k]?.ok && !s.revealedPairs[k];
}

/** Learner's ranking starts with the true top-n, in order, and the full ranking was not revealed. */
export function rankingPrefixOk(s, n) {
  if (s.rankingRevealed[s.scoreKey]) return false;
  const truth = ranking(s).slice(0, n).map((r) => pairKey(r[0], r[1]));
  return s.myRanking.length >= n && truth.every((k, i) => s.myRanking[i] === k);
}

export function topPair(s, scoreKey = s.scoreKey) {
  const r = ranking(s, scoreKey)[0];
  return r ? pairKey(r[0], r[1]) : null;
}
