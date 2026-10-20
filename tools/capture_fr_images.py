#!/usr/bin/env python3
"""Re-capture the French images used by the French slides (optional).

The images are already committed in i18n/fr/module01-01-affinity-metrics/assets/.
Run this only if the walkthrough or the lab changes. It needs Playwright + Chromium
and a local server for the course site:

    (cd ../eda-learning && python3 -m http.server 8080 --directory platform) &
    python3 tools/capture_fr_images.py --lab-base http://127.0.0.1:8000

The French lab screenshot is taken from the built site (docs/fr/...), so build the
site first and serve docs/ on port 8000.

Walkthrough frames: the teacher's walkthrough page draws the graph; this script
replaces its English text with i18n/fr/walkthrough-steps.json before each capture
(same 1100x900 viewport as capture_algorithm_walkthrough.py).
"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parents[1]
FR = HERE / "i18n/fr"
OUT = FR / "module01-01-affinity-metrics/assets"


async def walkthrough(page, base: str) -> None:
    data = json.loads((FR / "walkthrough-steps.json").read_text(encoding="utf-8"))
    (OUT / "steps").mkdir(parents=True, exist_ok=True)
    n = len(data["steps"])
    for i, st in enumerate(data["steps"], 1):
        await page.goto(f"{base}/tools/algorithm-walkthrough/index.html?algo=affinity-metrics&step={i}",
                        wait_until="networkidle")
        await page.wait_for_selector("#walk-frame[data-ready='1']")
        await page.evaluate(
            """([d, st, i, n]) => {
              const f = document.getElementById('walk-frame');
              f.querySelector('.walk-banner .algo').textContent = d.algo;
              f.querySelector('.walk-banner h1').textContent = st.title;
              const meta = f.querySelector('.step-meta');
              meta.textContent = meta.textContent.replace(/^Step \\d+ \\/ \\d+/, `${d.step_word} ${i} / ${n}`);
              f.querySelector('.walk-explain h2').textContent = d.explanation;
              f.querySelector('.walk-explain .caption').textContent = st.caption;
              const lis = f.querySelectorAll('.walk-explain li');
              st.bullets.forEach((b, k) => { if (lis[k]) lis[k].textContent = b; });
              if (st.metrics) f.querySelector('.walk-metrics').textContent = st.metrics.join('\\n');
            }""",
            [data, st, i, n],
        )
        await page.locator("#walk-frame").screenshot(path=str(OUT / "steps" / st["file"]))
        print("wrote", OUT / "steps" / st["file"])


async def priority_figure(page, base: str) -> None:
    graph = json.loads(
        (HERE.parent / "eda-learning/courses/learn_clustering/module01-01-affinity-metrics/examples/priority_graph.json")
        .read_text(encoding="utf-8")
    ) if (HERE.parent / "eda-learning").exists() else None
    if graph is None:
        print("skip priority figure (eda-learning not next to this repo)")
        return
    await page.goto(f"{base}/tools/affinity-metrics/index.html", wait_until="networkidle")
    await page.evaluate(
        """async (g) => {
          const { drawGraph } = await import('/assets/clustering-ui.js');
          const layout = {P:{x:80,y:60},Q:{x:80,y:260},R:{x:240,y:160},X:{x:380,y:80},Y:{x:520,y:240}};
          const wrap = document.createElement('div'); wrap.id = 'fig';
          wrap.style.cssText = 'display:flex;flex-direction:column;gap:18px;padding:16px;background:#fff;width:600px;font:600 24px system-ui';
          for (const [t, hot] of [['Poids d\\u2019arête : 1re fusion X–Y (5)', 'X|Y'],
                                  ['Voisins communs : 1re fusion P–Q (4+4 = 8)', 'P|Q']]) {
            const p = document.createElement('div');
            const h = document.createElement('div'); h.textContent = t; h.style.marginBottom = '8px';
            const c = document.createElement('canvas'); c.style.cssText = 'width:556px;height:340px;display:block;border:1px solid #ccc';
            p.append(h, c); wrap.append(p); document.body.prepend(wrap);
            drawGraph(c, { nodes: g.nodes, edges: g.edges }, { layout, highlightPairs: [hot],
              assignment: { P: '0', Q: '0', R: '0', X: '0', Y: '0' } });
          }
        }""",
        graph,
    )
    await page.wait_for_timeout(300)
    await page.locator("#fig").screenshot(path=str(OUT / "priority-graph.png"))
    print("wrote", OUT / "priority-graph.png")


async def lab_screenshot(page, lab_base: str) -> None:
    url = f"{lab_base}/fr/tools/affinity-metrics/index.html"
    await page.goto(url, wait_until="networkidle")
    await page.add_style_tag(content="html,body{scroll-behavior:auto !important}")

    async def click(n):
        xy = await page.evaluate(
            """async (n) => {
              const { fitGraphLayout } = await import('../../assets/canvas-hires.js');
              const M = await import('./affinity-lab-model.js');
              const c = document.querySelector('canvas'); const r = c.getBoundingClientRect();
              const { layout } = fitGraphLayout(M.LAYOUTS.starter, c.clientWidth, c.clientHeight);
              return [r.left + layout[n].x, r.top + layout[n].y];
            }""",
            n,
        )
        await page.mouse.click(*xy)

    await page.select_option("#lab-chal-sel", "ac-climbs")
    await page.click("#lab-chal-start")
    for a, b in [("A", "B"), ("D", "E")]:
        await click(a); await click(b)
        await page.click("button:text-is('Ajouter à mon classement')")
    await click("B"); await click("D"); await page.fill(".aff-input", "2")
    await page.click("button:text-is('Vérifier mon score')")
    await click("A"); await click("C"); await page.fill(".aff-input", "5")
    await page.click("button:text-is('Vérifier mon score')")
    await page.locator(".tool-layout").screenshot(path=str(OUT / "lab-starter.png"))
    print("wrote", OUT / "lab-starter.png")


async def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--course-base", default="http://127.0.0.1:8080", help="served eda-learning/platform")
    ap.add_argument("--lab-base", default=None, help="served docs/ of this repo (for the lab screenshot)")
    args = ap.parse_args()
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        page = await b.new_page(viewport={"width": 1100, "height": 900})
        await walkthrough(page, args.course_base)
        hi = await b.new_page(viewport={"width": 1400, "height": 1000}, device_scale_factor=2)
        await priority_figure(hi, args.course_base)
        if args.lab_base:
            lab = await b.new_page(viewport={"width": 1280, "height": 3000}, device_scale_factor=2)
            await lab_screenshot(lab, args.lab_base)
        await b.close()


if __name__ == "__main__":
    asyncio.run(main())
