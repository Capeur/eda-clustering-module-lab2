/**
 * Affinity metrics — learner-driven lab (Lab 02).
 *
 * The learner picks a pair on the canvas, computes its score by hand and
 * types it in, builds the ranking in order, and edits edge weights to change
 * who merges first. Challenges read that learner state. Study aids (pair
 * breakdown, full ranking) are allowed, but anything revealed no longer counts.
 */
import { fitGraphLayout, fitHiDpiCanvas } from "../../assets/canvas-hires.js";
import { hitNode } from "../../assets/interactive-graph-lab.js";
import { PALETTE, createChallengeLab, drawGraph, el, metricsBlock } from "../../assets/clustering-ui.js";
import * as M from "./affinity-lab-model.js";

const root = document.getElementById("lab-root");

let state = M.createState("starter");
let picked = []; // up to two node ids
let typed = ""; // text in the score box (kept across rerenders)
let lastMsg = "";

const pairOf = () => (picked.length === 2 ? [picked[0], picked[1]] : null);
const isGraph = () => M.GRAPHS[state.graphKey].kind === "graph";

function reset(graphKey = state.graphKey, scoreKey = null) {
  state = M.createState(graphKey, scoreKey);
  picked = [];
  typed = "";
  lastMsg = "";
}

/* ---------------- drawing ---------------- */

// Fixed hub positions (design coords) so each net is drawn as its own star.
const NET_HUBS = { en: { x: 130, y: 150 }, rst: { x: 260, y: 170 }, n1: { x: 135, y: 315 } };

function drawNetlist(canvas) {
  const { ctx, w, h } = fitHiDpiCanvas(canvas);
  const design = { ...M.LAYOUTS.netlist };
  for (const [id, p] of Object.entries(NET_HUBS)) design[`#${id}`] = p;
  const { layout, nodeR, fontPx, edgeW } = fitGraphLayout(design, w, h);
  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = "#f7faf9";
  ctx.fillRect(0, 0, w, h);
  const labelDy = { en: -12, rst: 22, n1: -12 };
  state.nets.forEach((net, i) => {
    const color = PALETTE[(i + 2) % PALETTE.length];
    const hub = layout[`#${net.id}`];
    ctx.strokeStyle = color;
    ctx.lineWidth = edgeW;
    for (const pin of net.pins) {
      ctx.beginPath();
      ctx.moveTo(hub.x, hub.y);
      ctx.lineTo(layout[pin].x, layout[pin].y);
      ctx.stroke();
    }
    ctx.fillStyle = color;
    ctx.fillRect(hub.x - 7, hub.y - 7, 14, 14);
    ctx.font = `bold ${Math.max(11, fontPx - 1)}px ui-monospace, Menlo, Consolas, monospace`;
    const label = `${net.id} (${net.pins.length} pins)`;
    const ly = hub.y + (labelDy[net.id] ?? -12);
    ctx.lineWidth = 4;
    ctx.strokeStyle = "#f7faf9";
    ctx.strokeText(label, hub.x + 10, ly); // halo keeps the label readable over lines
    ctx.fillText(label, hub.x + 10, ly);
  });
  const sel = new Set(picked);
  for (const n of state.nodes) {
    const p = layout[n];
    ctx.beginPath();
    ctx.arc(p.x, p.y, sel.has(n) ? nodeR + 2 : nodeR, 0, Math.PI * 2);
    ctx.fillStyle = PALETTE[0];
    ctx.fill();
    ctx.strokeStyle = sel.has(n) ? "#b45309" : "#0f172a";
    ctx.lineWidth = sel.has(n) ? 3 : 1.5;
    ctx.stroke();
    ctx.fillStyle = "#fff";
    ctx.font = `bold ${fontPx}px system-ui, sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(n, p.x, p.y);
    ctx.textAlign = "start";
    ctx.textBaseline = "alphabetic";
  }
}

function drawWorkspace(canvas) {
  if (!isGraph()) return drawNetlist(canvas);
  const layout = M.LAYOUTS[state.graphKey];
  const pair = pairOf();
  const edges = state.edges.filter((e) => e.w > 0);
  const hasEdge = pair && M.weightOf(state, pair[0], pair[1]) > 0;
  drawGraph(canvas, { nodes: state.nodes, edges }, {
    layout,
    assignment: Object.fromEntries(state.nodes.map((n) => [n, "0"])),
    selectedNodes: picked,
    highlightPairs: hasEdge ? [pair[0] < pair[1] ? `${pair[0]}|${pair[1]}` : `${pair[1]}|${pair[0]}`] : [],
  });
  if (pair && !hasEdge) {
    // Non-edge pair (e.g. B–D): dashed line, it can still score via neighbors.
    const ctx = canvas.getContext("2d");
    const { layout: scr } = fitGraphLayout(layout, canvas.clientWidth || 640, canvas.clientHeight || 480);
    ctx.save();
    ctx.setLineDash([8, 6]);
    ctx.strokeStyle = "#b45309";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(scr[pair[0]].x, scr[pair[0]].y);
    ctx.lineTo(scr[pair[1]].x, scr[pair[1]].y);
    ctx.stroke();
    ctx.restore();
  }
}

/* ---------------- challenges (all read learner state) ---------------- */

const setup = (graphKey, scoreKey) => () => reset(graphKey, scoreKey);
const own = (score, ...pairs) => pairs.every(([u, v]) => M.answeredOwn(state, score, u, v));

const challenges = [
  {
    id: "edge-top3",
    title: "Top three by edge weight",
    level: "Intro",
    prompt: "Edge weight, starter graph. Build YOUR ranking: click a pair, press “Add to my ranking”, in order. The first three must be right, ties broken alphabetically.",
    hint: "A–B and D–E both weigh 5. Alphabetical order: A before D. Then the next heaviest edge.",
    setup: setup("starter", "edge"),
    check: () => state.scoreKey === "edge" && M.rankingPrefixOk(state, 3),
  },
  {
    id: "shared-ab",
    title: "Score A–B with shared neighbors",
    level: "Intro",
    prompt: "Shared neighbors, starter graph. Pick A and B, compute the score by hand, type it in and press “Check my score”.",
    hint: "Direct weight 5, plus for each common neighbor the SMALLER of its two edges. A and B share C.",
    setup: setup("starter", "shared"),
    check: () => own("shared", ["A", "B"]),
  },
  {
    id: "ac-climbs",
    title: "The weak edge climbs",
    level: "Practice",
    prompt: "A–C is only 1 by edge weight. Compute its shared-neighbor score yourself.",
    hint: "A and C share B: min(w(A,B), w(C,B)).",
    setup: setup("starter", "shared"),
    check: () => own("shared", ["A", "C"]),
  },
  {
    id: "invented-bd",
    title: "A pair with no edge",
    level: "Practice",
    prompt: "B and D have no edge. Pick them anyway (dashed line) and compute their shared-neighbor score.",
    hint: "Direct part is 0. They share C: min(w(B,C), w(D,C)).",
    setup: setup("starter", "shared"),
    check: () => own("shared", ["B", "D"]),
  },
  {
    id: "all-invented",
    title: "Find all four invented pairs",
    level: "Practice",
    prompt: "Four pairs without an edge get a shared-neighbor score above 0. Find them all and score each one correctly.",
    hint: "All four go through C. Besides B–D, look at A–D, A–E and B–E.",
    setup: setup("starter", "shared"),
    check: () => own("shared", ["B", "D"], ["A", "D"], ["A", "E"], ["B", "E"]),
  },
  {
    id: "shared-top4",
    title: "Shared ranking, top four",
    level: "Practice",
    prompt: "Shared neighbors, starter graph. Build your ranking: the first four pairs, in order.",
    hint: "Two pairs score 6 and two score 5. Inside each tie, alphabetical order.",
    setup: setup("starter", "shared"),
    check: () => state.scoreKey === "shared" && M.rankingPrefixOk(state, 4),
  },
  {
    id: "priority-flip",
    title: "The first merge flips",
    level: "Practice",
    prompt: "Priority graph, shared neighbors. Score P–Q and X–Y yourself. Which one merges first now, and which one did under edge weight?",
    hint: "P–Q: 4 plus via R min(4,4). X–Y has no common neighbor.",
    setup: setup("priority", "shared"),
    check: () => own("shared", ["P", "Q"], ["X", "Y"]),
  },
  {
    id: "de-wins",
    title: "Make D–E win",
    level: "Stretch",
    prompt: "Starter graph, edge weight. Edit weights so D–E ranks FIRST, changing the total weight by exactly 1.",
    hint: "D–E loses only on the tie-break. Either raise D–E or lower A–B by one.",
    setup: setup("starter", "edge"),
    check: () => M.topPair(state, "edge") === "D–E" && M.edits(state).total === 1,
  },
  {
    id: "beat-triangle",
    title: "Out-score the triangle",
    level: "Stretch",
    prompt: "Priority graph. Raise ONLY X–Y until X–Y ranks first under shared neighbors. Use the smallest weight that works.",
    hint: "The triangle pairs score 8. A tie goes to P–Q (P before X), so 8 is not enough.",
    setup: setup("priority", "shared"),
    check: () => {
      const e = M.edits(state).list;
      return e.length === 1 && e[0].pair === "X–Y" && e[0].to === 9 && M.topPair(state, "shared") === "X–Y";
    },
  },
  {
    id: "wide-nets",
    title: "Wide nets count less",
    level: "Stretch",
    prompt: "Tiny netlist, pin-count score. Score A–B and E–F yourself (fractions like 1/4 are fine). Which pair merges first?",
    hint: "Each net gives w/(pins − 1) to every pair it connects. A–B shares two 5-pin nets; E–F shares one 2-pin net.",
    setup: setup("netlist", "pin"),
    check: () => own("pin", ["A", "B"], ["E", "F"]),
  },
];

/* ---------------- controls ---------------- */

function selectEl(labelText, options, value, onChange) {
  const sel = el("select", { "aria-label": labelText, onChange: (e) => onChange(e.target.value) });
  for (const [v, t] of options) {
    const o = el("option", { value: v, text: t });
    if (v === value) o.selected = true;
    sel.append(o);
  }
  return el("label", { className: "aff-control" }, [`${labelText} `, sel]);
}

function extraActions(ctx) {
  const kind = M.GRAPHS[state.graphKey].kind;
  const scoreOptions = Object.entries(M.SCORES)
    .filter(([, sc]) => sc.kind === kind)
    .map(([k, sc]) => [k, sc.label]);
  return [
    selectEl("Graph", Object.entries(M.GRAPHS).map(([k, g]) => [k, g.label]), state.graphKey, (v) => {
      reset(v);
      ctx.rerender();
    }),
    selectEl("Score", scoreOptions, state.scoreKey, (v) => {
      state = M.setScore(state, v);
      lastMsg = "Score changed: your ranking was cleared.";
      ctx.rerender();
    }),
  ];
}

/* ---------------- workspace panel ---------------- */

function btn(text, cls, onClick, disabled = false) {
  return el("button", { className: `btn ${cls}`, type: "button", text, onClick, disabled });
}

function renderWorkspace(ctx) {
  drawWorkspace(ctx.canvas);
  ctx.canvas.onclick = (ev) => {
    const design = isGraph()
      ? M.LAYOUTS[state.graphKey]
      : { ...M.LAYOUTS.netlist, ...Object.fromEntries(Object.entries(NET_HUBS).map(([k, p]) => [`#${k}`, p])) };
    let hit = hitNode(ctx.canvas, ev.clientX, ev.clientY, design);
    if (hit && hit.startsWith("#")) hit = null;
    if (!hit) return;
    if (picked.length === 1 && picked[0] !== hit) picked = [picked[0], hit];
    else picked = [hit];
    typed = "";
    lastMsg = "";
    ctx.rerender();
  };

  const pair = pairOf();
  const scoreLabel = M.SCORES[state.scoreKey].label;
  const box = el("div", { className: "aff-panel" });

  // 1. Selected pair + score entry
  const head = el("p", { className: "aff-pair" });
  head.innerHTML = pair
    ? `<strong>Pair ${M.pairKey(...pair)}</strong> · score: ${scoreLabel}`
    : picked.length === 1
      ? `<strong>${picked[0]}</strong> + … click a second node`
      : "Click two nodes on the canvas to pick a pair.";
  box.append(head);

  if (pair) {
    const input = el("input", {
      type: "text",
      className: "aff-input",
      placeholder: "e.g. 5 or 1/4",
      "aria-label": "Your score for the selected pair",
      value: typed,
      onInput: (e) => {
        typed = e.target.value;
      },
      onKeydown: (e) => {
        if (e.key === "Enter") checkScore();
      },
    });
    const checkScore = () => {
      const res = M.answer(state, pair[0], pair[1], typed);
      state = res.state;
      lastMsg = res.msg;
      ctx.rerender();
    };
    const key = `${state.scoreKey}|${M.pairKey(...pair)}`;
    const row = el("div", { className: "tool-actions aff-row" }, [
      input,
      btn("Check my score", "btn-primary", checkScore),
      btn("Add to my ranking", "btn-secondary", () => {
        const r = M.addToRanking(state, pair[0], pair[1]);
        state = r.state;
        lastMsg = r.msg;
        ctx.rerender();
      }),
      btn(state.revealedPairs[key] ? "Breakdown shown" : "Show breakdown (study)", "btn-ghost", () => {
        state = M.revealPair(state, pair[0], pair[1]);
        lastMsg = "Breakdown shown: your answer for this pair no longer counts for challenges.";
        ctx.rerender();
      }),
    ]);
    box.append(row);
    if (isGraph()) {
      box.append(
        el("div", { className: "tool-actions aff-row" }, [
          el("span", { className: "aff-muted", text: `edge weight ${M.weightOf(state, pair[0], pair[1])}:` }),
          btn("− 1", "btn-ghost", () => {
            const r = M.editWeight(state, pair[0], pair[1], -1);
            state = r.state;
            lastMsg = r.msg + " Scores changed: answers and ranking cleared.";
            ctx.rerender();
          }),
          btn("+ 1", "btn-ghost", () => {
            const r = M.editWeight(state, pair[0], pair[1], +1);
            state = r.state;
            lastMsg = r.msg + " Scores changed: answers and ranking cleared.";
            ctx.rerender();
          }),
        ])
      );
    }
    if (state.revealedPairs[key]) box.append(metricsBlock(M.breakdown(state, pair[0], pair[1])));
  }
  if (lastMsg) box.append(el("p", { className: "aff-msg", text: lastMsg }));

  // 2. Learner state: score sheet, ranking, edits
  const sheet = Object.entries(state.answers)
    .filter(([k]) => k.startsWith(`${state.scoreKey}|`))
    .map(([k, a]) => {
      const p = k.split("|")[1];
      const tag = state.revealedPairs[k] ? " (breakdown seen)" : "";
      return `  ${p}: ${+a.value.toFixed(4)} ${a.ok ? "✓" : "✗"}${tag}`;
    });
  const ed = M.edits(state);
  const lines = [
    `graph: ${state.graphKey} · score: ${scoreLabel}`,
    "",
    "your scores:",
    ...(sheet.length ? sheet : ["  (none yet)"]),
    "",
    "your ranking:",
    ...(state.myRanking.length ? state.myRanking.map((p, i) => `  ${i + 1}. ${p}`) : ["  (empty)"]),
  ];
  if (isGraph()) {
    lines.push("", `weight edits (total change ${ed.total}):`);
    lines.push(...(ed.list.length ? ed.list.map((x) => `  ${x.pair}: ${x.from} → ${x.to}`) : ["  (none)"]));
  } else {
    lines.push("", "nets:", ...state.nets.map((n) => `  ${n.id}: {${n.pins.join(",")}} w=${n.w}`));
  }
  box.append(metricsBlock(lines));

  const shown = !!(state.rankingRevealed[state.scoreKey] && state.showRanking);
  box.append(
    el("div", { className: "tool-actions aff-row" }, [
      btn("Undo last ranking entry", "btn-ghost", () => {
        state = M.undoRanking(state);
        ctx.rerender();
      }, !state.myRanking.length),
      btn(shown ? "Hide full ranking" : "Reveal full ranking (study)", "btn-ghost", () => {
        if (shown) {
          state = M.cloneState(state);
          state.showRanking = false;
        } else {
          state = M.revealRanking(state);
          state.showRanking = true;
          lastMsg = "Full ranking revealed: ranking challenges for this score no longer pass until you reset.";
        }
        ctx.rerender();
      }),
    ])
  );
  if (shown) {
    const r = M.ranking(state);
    box.append(metricsBlock(["full ranking (study):", ...r.map(([u, v, s], i) => `  ${i + 1}. ${u}–${v}: ${+s.toFixed(4)}`)]));
  }

  ctx.metrics.innerHTML = "";
  ctx.metrics.append(box);
}

createChallengeLab(root, {
  starterButtonLabel: "Reset workspace",
  workspaceBeforeActions: false,
  idlePromptHtml:
    "Pick a challenge and click <strong>Start</strong>. Work it out yourself, then <strong>Check</strong>. Study aids are allowed, but what they reveal stops counting.",
  starterHtml: `
    <p><strong>Your workspace:</strong> click two nodes to pick a pair (any pair, even without an edge).
    Compute its score <em>by hand</em> and type it in, add pairs to <em>your</em> ranking in order,
    or change edge weights with − / + to see who merges first.</p>
    <p>Challenges check your typed scores, your ranking and your edits. Using “Show breakdown” or
    “Reveal full ranking” is fine for study, but those answers no longer count.</p>
  `,
  challenges,
  loadStarter() {
    reset(state.graphKey);
  },
  extraActions,
  renderWorkspace,
});
