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
    const label = `${net.id} (${net.pins.length} broches)`;
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
    title: "Le trio de tête par poids d'arête",
    level: "Initiation",
    prompt: "Poids d'arête, graphe de départ. Construisez VOTRE classement : cliquez sur une paire, puis sur « Ajouter à mon classement », dans l'ordre. Les trois premières doivent être justes, égalités départagées par ordre alphabétique.",
    hint: "A–B et D–E pèsent toutes les deux 5. Ordre alphabétique : A avant D. Ensuite, l'arête la plus lourde suivante.",
    setup: setup("starter", "edge"),
    check: () => state.scoreKey === "edge" && M.rankingPrefixOk(state, 3),
  },
  {
    id: "shared-ab",
    title: "Le score de A–B par voisins communs",
    level: "Initiation",
    prompt: "Voisins communs, graphe de départ. Choisissez A et B, calculez le score à la main, saisissez-le puis cliquez sur « Vérifier mon score ».",
    hint: "Poids direct 5, plus, pour chaque voisin commun, la PLUS PETITE de ses deux arêtes. A et B ont C en commun.",
    setup: setup("starter", "shared"),
    check: () => own("shared", ["A", "B"]),
  },
  {
    id: "ac-climbs",
    title: "L'arête faible remonte",
    level: "Pratique",
    prompt: "A–C ne vaut que 1 en poids d'arête. Calculez vous-même son score par voisins communs.",
    hint: "A et C ont B en commun : min(w(A,B), w(C,B)).",
    setup: setup("starter", "shared"),
    check: () => own("shared", ["A", "C"]),
  },
  {
    id: "invented-bd",
    title: "Une paire sans arête",
    level: "Pratique",
    prompt: "B et D n'ont pas d'arête. Choisissez-les quand même (ligne pointillée) et calculez leur score par voisins communs.",
    hint: "La partie directe vaut 0. Ils ont C en commun : min(w(B,C), w(D,C)).",
    setup: setup("starter", "shared"),
    check: () => own("shared", ["B", "D"]),
  },
  {
    id: "all-invented",
    title: "Trouver les quatre paires sans arête",
    level: "Pratique",
    prompt: "Quatre paires sans arête obtiennent un score par voisins communs supérieur à 0. Trouvez-les toutes et donnez le bon score à chacune.",
    hint: "Toutes passent par C. En plus de B–D, regardez A–D, A–E et B–E.",
    setup: setup("starter", "shared"),
    check: () => own("shared", ["B", "D"], ["A", "D"], ["A", "E"], ["B", "E"]),
  },
  {
    id: "shared-top4",
    title: "Classement par voisins communs, les quatre premières",
    level: "Pratique",
    prompt: "Voisins communs, graphe de départ. Construisez votre classement : les quatre premières paires, dans l'ordre.",
    hint: "Deux paires valent 6 et deux valent 5. Dans chaque égalité, ordre alphabétique.",
    setup: setup("starter", "shared"),
    check: () => state.scoreKey === "shared" && M.rankingPrefixOk(state, 4),
  },
  {
    id: "priority-flip",
    title: "La première fusion s'inverse",
    level: "Pratique",
    prompt: "Graphe de priorité, voisins communs. Calculez vous-même P–Q et X–Y. Laquelle fusionne en premier maintenant, et laquelle fusionnait en premier avec le poids d'arête ?",
    hint: "P–Q : 4 plus, via R, min(4,4). X–Y n'a aucun voisin commun.",
    setup: setup("priority", "shared"),
    check: () => own("shared", ["P", "Q"], ["X", "Y"]),
  },
  {
    id: "de-wins",
    title: "Faire gagner D–E",
    level: "Approfondissement",
    prompt: "Graphe de départ, poids d'arête. Modifiez les poids pour que D–E passe EN PREMIER, en changeant le poids total d'exactement 1.",
    hint: "D–E ne perd qu'au départage. Augmentez D–E ou diminuez A–B de un.",
    setup: setup("starter", "edge"),
    check: () => M.topPair(state, "edge") === "D–E" && M.edits(state).total === 1,
  },
  {
    id: "beat-triangle",
    title: "Battre le triangle",
    level: "Approfondissement",
    prompt: "Graphe de priorité. Augmentez UNIQUEMENT X–Y jusqu'à ce que X–Y passe en premier avec les voisins communs. Utilisez le plus petit poids qui fonctionne.",
    hint: "Les paires du triangle valent 8. Une égalité revient à P–Q (P avant X), donc 8 ne suffit pas.",
    setup: setup("priority", "shared"),
    check: () => {
      const e = M.edits(state).list;
      return e.length === 1 && e[0].pair === "X–Y" && e[0].to === 9 && M.topPair(state, "shared") === "X–Y";
    },
  },
  {
    id: "wide-nets",
    title: "Les nets larges comptent moins",
    level: "Approfondissement",
    prompt: "Petite netlist, score par nombre de broches. Calculez vous-même A–B et E–F (les fractions comme 1/4 sont acceptées). Quelle paire fusionne en premier ?",
    hint: "Chaque net donne w/(broches − 1) à chaque paire qu'il relie. A–B partage deux nets à 5 broches ; E–F partage un net à 2 broches.",
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
    selectEl("Graphe", Object.entries(M.GRAPHS).map(([k, g]) => [k, g.label]), state.graphKey, (v) => {
      reset(v);
      ctx.rerender();
    }),
    selectEl("Score", scoreOptions, state.scoreKey, (v) => {
      state = M.setScore(state, v);
      lastMsg = "Score changé : votre classement a été effacé.";
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
    ? `<strong>Paire ${M.pairKey(...pair)}</strong> · score : ${scoreLabel}`
    : picked.length === 1
      ? `<strong>${picked[0]}</strong> + … cliquez sur un second nœud`
      : "Cliquez sur deux nœuds du graphe pour choisir une paire.";
  box.append(head);

  if (pair) {
    const input = el("input", {
      type: "text",
      className: "aff-input",
      placeholder: "ex. 5 ou 1/4",
      "aria-label": "Votre score pour la paire choisie",
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
      btn("Vérifier mon score", "btn-primary", checkScore),
      btn("Ajouter à mon classement", "btn-secondary", () => {
        const r = M.addToRanking(state, pair[0], pair[1]);
        state = r.state;
        lastMsg = r.msg;
        ctx.rerender();
      }),
      btn(state.revealedPairs[key] ? "Détail affiché" : "Afficher le détail (révision)", "btn-ghost", () => {
        state = M.revealPair(state, pair[0], pair[1]);
        lastMsg = "Détail affiché : votre réponse pour cette paire ne compte plus pour les défis.";
        ctx.rerender();
      }),
    ]);
    box.append(row);
    if (isGraph()) {
      box.append(
        el("div", { className: "tool-actions aff-row" }, [
          el("span", { className: "aff-muted", text: `poids d'arête ${M.weightOf(state, pair[0], pair[1])} :` }),
          btn("− 1", "btn-ghost", () => {
            const r = M.editWeight(state, pair[0], pair[1], -1);
            state = r.state;
            lastMsg = r.msg + " Scores modifiés : réponses et classement effacés.";
            ctx.rerender();
          }),
          btn("+ 1", "btn-ghost", () => {
            const r = M.editWeight(state, pair[0], pair[1], +1);
            state = r.state;
            lastMsg = r.msg + " Scores modifiés : réponses et classement effacés.";
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
      const tag = state.revealedPairs[k] ? " (détail vu)" : "";
      return `  ${p}: ${+a.value.toFixed(4)} ${a.ok ? "✓" : "✗"}${tag}`;
    });
  const ed = M.edits(state);
  const lines = [
    `graphe : ${M.GRAPHS[state.graphKey].label} · score : ${scoreLabel}`,
    "",
    "vos scores :",
    ...(sheet.length ? sheet : ["  (aucun pour l'instant)"]),
    "",
    "votre classement :",
    ...(state.myRanking.length ? state.myRanking.map((p, i) => `  ${i + 1}. ${p}`) : ["  (vide)"]),
  ];
  if (isGraph()) {
    lines.push("", `poids modifiés (changement total ${ed.total}) :`);
    lines.push(...(ed.list.length ? ed.list.map((x) => `  ${x.pair}: ${x.from} → ${x.to}`) : ["  (aucun)"]));
  } else {
    lines.push("", "nets :", ...state.nets.map((n) => `  ${n.id}: {${n.pins.join(",")}} w=${n.w}`));
  }
  box.append(metricsBlock(lines));

  const shown = !!(state.rankingRevealed[state.scoreKey] && state.showRanking);
  box.append(
    el("div", { className: "tool-actions aff-row" }, [
      btn("Annuler le dernier ajout", "btn-ghost", () => {
        state = M.undoRanking(state);
        ctx.rerender();
      }, !state.myRanking.length),
      btn(shown ? "Masquer le classement complet" : "Révéler le classement complet (révision)", "btn-ghost", () => {
        if (shown) {
          state = M.cloneState(state);
          state.showRanking = false;
        } else {
          state = M.revealRanking(state);
          state.showRanking = true;
          lastMsg = "Classement complet révélé : les défis de classement pour ce score ne passent plus tant que vous ne réinitialisez pas.";
        }
        ctx.rerender();
      }),
    ])
  );
  if (shown) {
    const r = M.ranking(state);
    box.append(metricsBlock(["classement complet (révision) :", ...r.map(([u, v, s], i) => `  ${i + 1}. ${u}–${v}: ${+s.toFixed(4)}`)]));
  }

  ctx.metrics.innerHTML = "";
  ctx.metrics.append(box);
}

createChallengeLab(root, {
  starterButtonLabel: "Réinitialiser",
  workspaceBeforeActions: false,
  idlePromptHtml:
    "Choisissez un défi et cliquez sur <strong>Commencer</strong>. Faites le travail vous-même, puis <strong>Vérifier</strong>. Les aides à la révision sont permises, mais ce qu'elles révèlent ne compte plus.",
  starterHtml: `
    <p><strong>Votre espace de travail :</strong> cliquez sur deux nœuds pour choisir une paire (n'importe laquelle, même sans arête).
    Calculez son score <em>à la main</em> et saisissez-le, ajoutez des paires à <em>votre</em> classement dans l'ordre,
    ou modifiez les poids des arêtes avec − / + pour voir qui fusionne en premier.</p>
    <p>Les défis vérifient les scores que vous saisissez, votre classement et vos modifications. « Afficher le détail » et
    « Révéler le classement complet » sont permis pour réviser, mais ces réponses ne comptent plus.</p>
  `,
  challenges,
  loadStarter() {
    reset(state.graphKey);
  },
  extraActions,
  renderWorkspace,
});
