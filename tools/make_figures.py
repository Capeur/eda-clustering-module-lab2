#!/usr/bin/env python3
"""Draw the explanation figures used by the Lab 02 slides, in English and French.

    chip-to-graph.png      cells and wires on a chip -> the same thing as a weighted graph
    clustering-groups.png  two groups {A,B,C} and {D,E}; only the red edges cross
    worked-ac.png          the A–C shared-neighbor score computed step by step
    wide-nets.png          two 5-pin nets and one private net (the "group chat" picture)

Graphs are drawn with the course's own drawGraph (platform/assets/clustering-ui.js), the
netlist with the Lab 02 browser lab, so the figures look like the lab.

Needs Playwright + Chromium and two local servers:
    (cd ../eda-learning && python3 -m http.server 8080 --directory platform) &
    python3 -m http.server 8090 --directory docs &        # built site (for the French lab)
    python3 tools/make_figures.py --en-out ../eda-learning/courses/learn_clustering/module01-01-affinity-metrics/assets
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parents[1]
FR_OUT = HERE / "i18n/fr/module01-01-affinity-metrics/assets"

TEXT = {
    "en": {
        "chip_top": "On the chip: cells joined by wires",
        "chip_bottom": "As a graph: weight = number of wires",
        "groups": "Two groups (clusters). Only the red edges cross between them.",
        "worked_title": "Score of A–C, step by step",
        "worked": ["1. Direct edge A–C: 1",
                   "2. Common neighbor B: min(5, 4) = 4",
                   "3. Total: 1 + 4 = 5"],
        "nets_title": "Two wide nets (en, rst) touch five cells. One private net joins E and F.",
        "cell": "cell",
    },
    "fr": {
        "chip_top": "Sur la puce : des cellules reliées par des fils",
        "chip_bottom": "En graphe : poids = nombre de fils",
        "groups": "Deux groupes (clusters). Seules les arêtes rouges passent de l'un à l'autre.",
        "worked_title": "Score de A–C, étape par étape",
        "worked": ["1. Arête directe A–C : 1",
                   "2. Voisin commun B : min(5, 4) = 4",
                   "3. Total : 1 + 4 = 5"],
        "nets_title": "Deux nets larges (en, rst) touchent cinq cellules. Un net privé relie E et F.",
        "cell": "cellule",
    },
}

# Starter graph positions used by the lab (clustering-core starterLayout).
LAYOUT = {"A": [90, 80], "B": [220, 60], "C": [160, 160], "D": [280, 200], "E": [120, 240]}
WEIGHTS = [("A", "B", 5), ("A", "C", 1), ("B", "C", 4), ("C", "D", 2), ("D", "E", 5), ("C", "E", 1)]

FIG_JS = r"""
async ([kind, t, layoutArr, weights]) => {
  const { drawGraph } = await import('/assets/clustering-ui.js');
  const { TINY_GRAPH } = await import('/assets/clustering-core.js');
  const layout = Object.fromEntries(Object.entries(layoutArr).map(([k, [x, y]]) => [k, { x, y }]));
  document.body.innerHTML = '';
  document.body.style.background = '#fff';
  const wrap = document.createElement('div');
  wrap.id = 'fig';
  wrap.style.cssText = 'display:flex;flex-direction:column;gap:14px;padding:18px;background:#fff;width:640px;font:600 24px system-ui,sans-serif;color:#1c2421';
  document.body.append(wrap);
  const title = (txt) => { const h = document.createElement('div'); h.textContent = txt; wrap.append(h); };
  const canvas = (h = 360) => {
    const c = document.createElement('canvas');
    c.style.cssText = `width:600px;height:${h}px;display:block;border:1px solid #ccc;border-radius:6px`;
    wrap.append(c); return c;
  };
  const same = Object.fromEntries(TINY_GRAPH.nodes.map((n) => [n, '0']));

  if (kind === 'chip') {
    title(t.chip_top);
    const c = canvas(330);
    const dpr = 2, W = 600, H = 330;
    c.width = W * dpr; c.height = H * dpr;
    const ctx = c.getContext('2d'); ctx.scale(dpr, dpr);
    ctx.fillStyle = '#f7faf9'; ctx.fillRect(0, 0, W, H);
    // scale the graph layout into the box
    const xs = Object.values(layout).map(p => p.x), ys = Object.values(layout).map(p => p.y);
    const sx = (x) => 70 + (x - Math.min(...xs)) / (Math.max(...xs) - Math.min(...xs)) * (W - 140);
    const sy = (y) => 50 + (y - Math.min(...ys)) / (Math.max(...ys) - Math.min(...ys)) * (H - 100);
    // wires: one thin line per unit of weight, spread side by side
    for (const [u, v, w] of weights) {
      const ax = sx(layout[u].x), ay = sy(layout[u].y), bx = sx(layout[v].x), by = sy(layout[v].y);
      const len = Math.hypot(bx - ax, by - ay), nx = -(by - ay) / len, ny = (bx - ax) / len;
      for (let i = 0; i < w; i++) {
        const off = (i - (w - 1) / 2) * 5;
        ctx.beginPath(); ctx.moveTo(ax + nx * off, ay + ny * off); ctx.lineTo(bx + nx * off, by + ny * off);
        ctx.strokeStyle = '#b45309'; ctx.lineWidth = 1.6; ctx.stroke();
      }
    }
    // cells: small chip blocks
    for (const [n, p] of Object.entries(layout)) {
      const x = sx(p.x), y = sy(p.y);
      ctx.fillStyle = '#0f6b5c'; ctx.fillRect(x - 30, y - 22, 60, 44);
      ctx.strokeStyle = '#0b3f36'; ctx.lineWidth = 2; ctx.strokeRect(x - 30, y - 22, 60, 44);
      ctx.fillStyle = '#fff'; ctx.font = 'bold 18px system-ui'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(n, x, y - 4);
      ctx.font = '11px system-ui'; ctx.fillText(t.cell, x, y + 12);
    }
    title(t.chip_bottom);
    drawGraph(canvas(330), TINY_GRAPH, { layout, assignment: same });
  } else if (kind === 'groups') {
    title(t.groups);
    drawGraph(canvas(400), TINY_GRAPH, { layout, assignment: { A: '0', B: '0', C: '0', D: '1', E: '1' } });
  } else if (kind === 'worked') {
    title(t.worked_title);
    drawGraph(canvas(360), TINY_GRAPH, { layout, assignment: same, highlightPairs: ['A|C', 'A|B', 'B|C'] });
    const box = document.createElement('div');
    box.style.cssText = 'font:500 24px ui-monospace,Menlo,monospace;line-height:1.6;background:#f3efe6;border-radius:8px;padding:12px 16px';
    box.innerHTML = t.worked.map((l, i) => i === 2 ? `<b>${l}</b>` : l).join('<br>');
    wrap.append(box);
  }
}
"""


async def graph_figure(page, base, kind, lang, out: Path):
    await page.goto(f"{base}/tools/affinity-metrics/index.html", wait_until="networkidle")
    await page.evaluate(FIG_JS, [kind, TEXT[lang], LAYOUT, WEIGHTS])
    await page.wait_for_timeout(300)
    await page.locator("#fig").screenshot(path=str(out))
    print("wrote", out)


async def nets_figure(page, lab_url, lang, out: Path):
    """Netlist drawn by the Lab 02 lab itself (its labels are already in `lang`)."""
    await page.goto(lab_url, wait_until="networkidle")
    sel = 'select[aria-label="Graph"]' if lang == "en" else 'select[aria-label="Graphe"]'
    await page.select_option(sel, "netlist")
    await page.wait_for_timeout(300)
    data = await page.evaluate("document.querySelector('canvas').toDataURL('image/png')")
    await page.evaluate(
        """([src, title]) => {
          document.body.innerHTML = '';
          const w = document.createElement('div'); w.id = 'fig';
          w.style.cssText = 'display:flex;flex-direction:column;gap:12px;padding:18px;background:#fff;width:640px;font:600 24px system-ui,sans-serif;color:#1c2421';
          const h = document.createElement('div'); h.textContent = title;
          const img = document.createElement('img'); img.src = src; img.style.cssText = 'width:600px;border:1px solid #ccc;border-radius:6px';
          w.append(h, img); document.body.append(w);
        }""",
        [data, TEXT[lang]["nets_title"]],
    )
    await page.wait_for_timeout(300)
    await page.locator("#fig").screenshot(path=str(out))
    print("wrote", out)


async def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--en-out", required=True, type=Path, help="English assets folder (eda-learning module)")
    ap.add_argument("--course-base", default="http://127.0.0.1:8080")
    ap.add_argument("--site-base", default="http://127.0.0.1:8090/eda-clustering-module-lab2", help="served docs/ (French lab)")
    args = ap.parse_args()
    FR_OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        page = await b.new_page(viewport={"width": 1200, "height": 1600}, device_scale_factor=2)
        for lang, out in (("en", args.en_out), ("fr", FR_OUT)):
            for kind, name in (("chip", "chip-to-graph.png"), ("groups", "clustering-groups.png"), ("worked", "worked-ac.png")):
                await graph_figure(page, args.course_base, kind, lang, out / name)
        await nets_figure(page, f"{args.course_base}/tools/affinity-metrics/index.html", "en", args.en_out / "wide-nets.png")
        await nets_figure(page, f"{args.site_base}/fr/tools/affinity-metrics/index.html", "fr", FR_OUT / "wide-nets.png")
        await b.close()


if __name__ == "__main__":
    asyncio.run(main())
