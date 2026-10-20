# Lab 02 — Affinity metrics · Clustering for EDA

A standalone GitHub Pages site for **Lab 02 (affinity metrics)** of the
[Clustering for EDA course](https://github.com/yongfu-li/eda-learning) — a review build of the
upgraded lab, not yet merged into the course repository.

The page has the narrated video with subtitles, every slide as an image, PDF/PowerPoint
downloads, the **interactive browser lab**, the Track A implementation material and files,
a quiz, and the full transcript.

Live site: `https://<your-username>.github.io/eda-clustering-module-lab2/`

## How it works

The course repository stays the source of truth. `build_site.py` reads from your local
`eda-learning` clone (with the Lab 02 patch applied) and writes the static site into `docs/`:

| From `eda-learning` | To `docs/` |
|---------------------|------------|
| `courses/learn_clustering/module01-01-affinity-metrics/slides.pdf` | `slides/01.png … 17.png` (gallery) + `slides.pdf` |
| `…/slides.pptx`, `quiz.json`, `transcript.md`, `examples/*` | copied as downloads |
| `…/video.mp4` + `audio/slide_timings.json` | `video.mp4` + `subs.vtt` / `subs.srt` (timed from the narration) |
| `…/EXAMPLES.md` | rendered into the Implement section |
| `platform/tools/affinity-metrics/` + the shared lab assets it imports | `tools/affinity-metrics/` + `assets/` |

`site_src/` holds the page template, its CSS and the quiz script.

## Rebuild after changing the lab

```bash
# 1. in eda-learning: regenerate narration + video (needs internet)
cd ~/path/to/eda-learning
bash .cursor/skills/module-slides/scripts/narrate_clips.sh \
  courses/learn_clustering/module01-01-affinity-metrics

# 2. here: rebuild docs/ and publish
cd ~/path/to/eda-clustering-module-lab2
pip install markdown pyyaml            # once; needs pdftoppm (sudo apt install poppler-utils)
python3 build_site.py --repo ~/path/to/eda-learning
git add -A && git commit -m "Rebuild site" && git push
```

Preview locally: `python3 -m http.server 8000 --directory docs`, then open `http://127.0.0.1:8000/`.

## Credits

Course content, browser lab framework and media pipeline: the
[EDA Algorithms Platform](https://github.com/yongfu-li/eda-learning) (CC BY 4.0).
Lab 02 upgrade (pin-count affinity, priority graph, interactive challenges, self-check,
new slides) built for the course assignment.
