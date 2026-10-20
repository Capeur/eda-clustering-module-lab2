# Lab 02 — Affinity metrics · Clustering for EDA

A standalone, **bilingual (English / French)** GitHub Pages site for **Lab 02 (affinity metrics)** of the
[Clustering for EDA course](https://github.com/yongfu-li/eda-learning) — a review build of the
upgraded lab, not yet merged into the course repository.

- English: `https://capeur.github.io/eda-clustering-module-lab2/`
- Français : `https://capeur.github.io/eda-clustering-module-lab2/fr/`

Each language has the narrated video with subtitles, every slide as an image, PDF/PowerPoint
downloads, the **interactive browser lab**, the Track A material, a quiz and the full transcript.
A switch in every header (page and lab) jumps to the other language at the same place.

## Layout

| Path | What |
|------|------|
| `build_site.py` | builds `docs/` (English) and `docs/fr/` (French) |
| `make_fr_media.py` | builds the French slides, narration and video with the course's own tools |
| `site_src/` | page template, CSS, quiz script (shared by both languages) |
| `i18n/strings.py` | all page text, English and French |
| `i18n/fr/module01-01-affinity-metrics/` | French narration (`transcript.md`), French images, French deck |
| `i18n/fr/EXAMPLES.md`, `i18n/fr/quiz.json` | French Track A guide and quiz |
| `i18n/fr/lab_strings.py` | French text for the browser lab (exact replacements; the build fails if the lab changed) |
| `i18n/fr/walkthrough-steps.json` + `tools/capture_fr_images.py` | French walkthrough frames (re-capture only if the walkthrough changes) |
| `docs/` | the built site served by GitHub Pages (main branch, `/docs`) |

English content comes from your `eda-learning` clone (Lab 02 patch applied); nothing in it is modified.

## Rebuild

```bash
# English narration + video, in eda-learning (needs internet)
cd ~/path/to/eda-learning
bash .cursor/skills/module-slides/scripts/narrate_clips.sh \
  courses/learn_clustering/module01-01-affinity-metrics

# French slides + narration + video, here (needs internet, LibreOffice, ffmpeg)
cd ~/path/to/eda-clustering-module-lab2
pip install markdown pyyaml edge-tts
python3 make_fr_media.py --repo ../eda-learning

# both sites
python3 build_site.py --repo ../eda-learning
git add -A && git commit -m "Rebuild site" && git push
```

Preview: `python3 -m http.server 8000 --directory docs` → `http://127.0.0.1:8000/` and `/fr/`.

**Terminology (French):** *netlist*, *net*, *cluster*/*clustering* and *quiz* stay in English, as in
French EDA courses; *broche* (pin), *poids d'arête* (edge weight), *voisins communs* (shared
neighbors), *départage* (tie-break), *fusion gloutonne* (greedy merge). Code, commands and program
output stay in English.

## Credits

Course content, browser lab framework and media pipeline: the
[EDA Algorithms Platform](https://github.com/yongfu-li/eda-learning) (CC BY 4.0).
Lab 02 upgrade and French translation built for the course assignment.
