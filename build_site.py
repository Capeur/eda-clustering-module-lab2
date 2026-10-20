#!/usr/bin/env python3
"""Build the Lab 02 (affinity metrics) GitHub Pages site into docs/.

Source of truth stays in the course repo (eda-learning):
    courses/learn_clustering/module01-01-affinity-metrics/   slides, video, quiz, examples
    platform/tools/affinity-metrics/                          interactive browser lab

Usage (from this repo's root):
    python3 build_site.py --repo ~/path/to/eda-learning

Needs: python3, pdftoppm (poppler-utils), and `pip install markdown pyyaml`.
Run narrate_clips.sh in the course repo first so video.mp4 and audio/slide_timings.json exist.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "site_src"
MODULE_REL = Path("courses/learn_clustering/module01-01-affinity-metrics")
TOOL_REL = Path("platform/tools/affinity-metrics")
ASSET_REL = Path("platform/assets")
COURSE_URL = "https://github.com/yongfu-li/eda-learning"
VOICE = "en-US-JennyNeural"

# Track A files offered for download, with a one-line description.
EXAMPLE_FILES = [
    ("examples/tiny_graph.json", "Starter graph (golden 1)"),
    ("examples/priority_graph.json", "Priority graph: the first merge flips (golden 2)"),
    ("examples/tiny_netlist.json", "Tiny netlist with wide nets (golden 3)"),
    ("examples/affinity_check.py", "Golden self-check; --impl checks your code"),
]


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- slides

def slide_titles(module: Path) -> list[str]:
    import yaml

    data = yaml.safe_load((module / "outline.yaml").read_text(encoding="utf-8"))
    return [str(s.get("title", f"Slide {i + 1}")) for i, s in enumerate(data.get("slides", []))]


def render_slides(module: Path, out: Path) -> int:
    pdf = module / "slides.pdf"
    if not pdf.is_file():
        die(f"missing {pdf} (build it with pptx_to_pdf.sh)")
    if not shutil.which("pdftoppm"):
        die("pdftoppm not found: sudo apt install poppler-utils")
    dest = out / "slides"
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pdftoppm", "-png", "-r", "110", str(pdf), str(dest / "s")], check=True)
    pngs = sorted(dest.glob("s-*.png"), key=lambda p: int(re.findall(r"\d+", p.stem)[-1]))
    for i, p in enumerate(pngs, 1):
        p.rename(dest / f"{i:02d}.png")
    return len(pngs)


# ---------------------------------------------------------------- subtitles

def _fmt_ts(t: float, sep: str) -> str:
    h, rem = divmod(max(0.0, t), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}{sep}{int(round((s % 1) * 1000)) % 1000:03d}"


def _chunks(sentence: str, limit: int = 84) -> list[str]:
    """Split one sentence into caption-sized pieces (about two short lines)."""
    words, out, cur = sentence.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > limit:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        out.append(cur)
    return out


def build_cues(repo: Path, module: Path) -> list[tuple[float, float, str]]:
    """Timed captions: each spoken section's audio length is shared over its
    caption chunks in proportion to their length (same timings as the video)."""
    scripts = repo / ".cursor/skills/module-slides/scripts"
    sys.path.insert(0, str(scripts))
    from synthesize_audio import _outline_slide_counts  # noqa: E402
    from transcript_parse import load_transcript_sections  # noqa: E402
    from transcript_to_speech import clean_narration_prose  # noqa: E402

    timings = json.loads((module / "audio/slide_timings.json").read_text(encoding="utf-8"))
    sections = [s for s in load_transcript_sections(module / "transcript.md") if clean_narration_prose(s.body)]
    counts = _outline_slide_counts(module, len(sections))
    durations = [float(t["duration"]) for t in timings]

    cues, t, k = [], 0.0, 0
    for section, n in zip(sections, counts):
        span = sum(durations[k : k + n])
        k += n
        speech = clean_narration_prose(section.body)
        sentences = [x for x in re.split(r"(?<=[.!?])\s+", speech) if x.strip()]
        pieces = [c for s in sentences for c in _chunks(s)]
        total = sum(len(p) for p in pieces) or 1
        start = t
        for p in pieces:
            d = span * len(p) / total
            cues.append((start, start + d, p))
            start += d
        t += span
    return cues


def write_subtitles(cues, out: Path) -> None:
    vtt = ["WEBVTT", ""]
    srt = []
    for i, (a, b, text) in enumerate(cues, 1):
        vtt += [f"{_fmt_ts(a, '.')} --> {_fmt_ts(b, '.')}", text, ""]
        srt += [str(i), f"{_fmt_ts(a, ',')} --> {_fmt_ts(b, ',')}", text, ""]
    (out / "subs.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (out / "subs.srt").write_text("\n".join(srt), encoding="utf-8")


# ---------------------------------------------------------------- browser lab

def copy_lab(repo: Path, out: Path) -> None:
    tool, assets = repo / TOOL_REL, repo / ASSET_REL
    dest_tool = out / "tools/affinity-metrics"
    dest_assets = out / "assets"
    dest_tool.mkdir(parents=True, exist_ok=True)
    dest_assets.mkdir(parents=True, exist_ok=True)
    for f in tool.iterdir():
        if f.is_file():
            shutil.copy2(f, dest_tool / f.name)

    # Shared course assets the lab imports (follow the import graph).
    needed = {"site.css", "tools-shared.css", "clustering-lab.css"}
    todo = []
    for f in tool.glob("*.js"):
        todo += re.findall(r'from\s+"\.\./\.\./assets/([^"]+)"', f.read_text(encoding="utf-8"))
    while todo:
        name = todo.pop()
        if name in needed:
            continue
        needed.add(name)
        todo += re.findall(r'from\s+"\./([^"]+)"', (assets / name).read_text(encoding="utf-8"))
    for name in sorted(needed):
        shutil.copy2(assets / name, dest_assets / name)

    # Standalone header: no platform nav / search (those pages are not deployed here).
    page = (dest_tool / "index.html").read_text(encoding="utf-8")
    page = re.sub(r'\s*<script src="\.\./\.\./assets/site\.js"></script>', "", page)
    page = re.sub(
        r'<header class="site-header">.*?</header>',
        '<header class="site-header">\n    <div class="site-header-inner">\n'
        '      <p class="brand"><a href="../../index.html">Clustering for EDA · Lab 02</a></p>\n'
        '      <nav class="site-nav" aria-label="Site">\n'
        '        <a href="../../index.html">Lab 02 home</a>\n'
        '        <a href="../../index.html#slides">Slides &amp; video</a>\n'
        '      </nav>\n    </div>\n  </header>',
        page,
        flags=re.S,
    )
    page = re.sub(
        r'<footer class="site-footer">.*?</footer>',
        '<footer class="site-footer">Lab 02 · Affinity metrics — part of the '
        f'<a href="{COURSE_URL}">EDA Algorithms Platform</a> clustering course (CC BY 4.0).</footer>',
        page,
        flags=re.S,
    )
    (dest_tool / "index.html").write_text(page, encoding="utf-8")


# ---------------------------------------------------------------- page

def render_markdown(path: Path) -> str:
    import markdown

    return markdown.markdown(path.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])


def transcript_html(module: Path) -> str:
    text = (module / "transcript.md").read_text(encoding="utf-8")
    parts = []
    for title, body in re.findall(r"^## Slide \d+ — (.+?)\n(.*?)(?=^## Slide |\Z)", text, flags=re.S | re.M):
        body = re.sub(r"```.*?```", "", body, flags=re.S)
        body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
        body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
        paras = [p.strip() for p in body.split("\n\n") if p.strip()]
        parts.append(f"<h3>{esc(title)}</h3>" + "".join(f"<p>{esc(p)}</p>" for p in paras))
    return "\n".join(parts)


def build_page(module: Path, out: Path, n_slides: int, has_video: bool, has_subs: bool, runtime: str) -> None:
    titles = slide_titles(module)
    quiz = json.loads((module / "quiz.json").read_text(encoding="utf-8"))

    if has_video:
        track = '<track kind="subtitles" src="subs.vtt" srclang="en" label="English" default>' if has_subs else ""
        video = (
            f'<video controls preload="metadata" poster="slides/01.png">'
            f'<source src="video.mp4" type="video/mp4">{track}'
            "Your browser does not support the video tag.</video>"
        )
        downloads = '<a class="btn" href="video.mp4" download>Download video (MP4)</a>' + (
            '<a class="btn" href="subs.srt" download>Subtitles (SRT)</a>' if has_subs else ""
        )
        meta = (
            f"<p class=\"meta\"><strong>{runtime}</strong> · {n_slides} slides · "
            f"English narration{' and subtitles' if has_subs else ''}</p>"
        )
    else:
        video = '<div class="missing">The narrated video has not been built yet. Run <code>narrate_clips.sh</code> in the course repo, then rebuild this site.</div>'
        downloads, meta = "", f'<p class="meta">{n_slides} slides</p>'

    slides = "\n".join(
        f'<figure><a href="slides/{i:02d}.png"><img src="slides/{i:02d}.png" loading="lazy" '
        f'alt="Slide {i}: {esc(titles[i - 1] if i <= len(titles) else "")}"></a>'
        f"<figcaption><b>{i:02d}</b>{esc(titles[i - 1] if i <= len(titles) else '')}</figcaption></figure>"
        for i in range(1, n_slides + 1)
    )
    files = "\n".join(
        f'<a href="{f}" download><code>{Path(f).name}</code><small>{esc(d)}</small></a>' for f, d in EXAMPLE_FILES
    )

    page = (SRC / "index.html.tmpl").read_text(encoding="utf-8")
    for key, val in {
        "VIDEO": video,
        "DOWNLOADS": downloads,
        "META": meta,
        "SLIDES": slides,
        "N_SLIDES": str(n_slides),
        "N_QUIZ": str(len(quiz["items"])),
        "QUIZ_JSON": json.dumps(quiz, ensure_ascii=False).replace("</", "<\\/"),
        "EXAMPLES_HTML": render_markdown(module / "EXAMPLES.md"),
        "EXAMPLE_FILES": files,
        "TRANSCRIPT": transcript_html(module),
        "COURSE_URL": COURSE_URL,
    }.items():
        page = page.replace("{{" + key + "}}", val)
    (out / "index.html").write_text(page, encoding="utf-8")


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, type=Path, help="path to your eda-learning clone")
    ap.add_argument("--out", default=HERE / "docs", type=Path, help="output folder (default: docs/)")
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    module = repo / MODULE_REL
    if not (module / "transcript.md").is_file() or not (repo / TOOL_REL / "index.html").is_file():
        die(f"{repo} does not look like eda-learning with the Lab 02 patch applied")

    out = args.out.resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / ".nojekyll").write_text("", encoding="utf-8")

    # Static files straight from the module.
    for name in ["slides.pdf", "slides.pptx", "quiz.json", "transcript.md"]:
        shutil.copy2(module / name, out / name)
    (out / "examples").mkdir()
    for f, _ in EXAMPLE_FILES:
        shutil.copy2(module / f, out / f)
    (out / "img").mkdir()
    for name in ["lab-starter.png", "priority-graph.png", "real-shell.png"]:
        shutil.copy2(module / "assets" / name, out / "img" / name)
    shutil.copy2(SRC / "page.css", out / "page.css")
    shutil.copy2(SRC / "quiz.js", out / "quiz.js")

    n_slides = render_slides(module, out)

    video = module / "video.mp4"
    timings = module / "audio/slide_timings.json"
    has_video = video.is_file()
    has_subs, runtime = False, ""
    if has_video:
        newest_source = max((module / f).stat().st_mtime for f in ["transcript.md", "slides.pptx"])
        if video.stat().st_mtime < newest_source:
            print("WARNING: video.mp4 is older than transcript.md/slides.pptx — rerun narrate_clips.sh", file=sys.stderr)
        shutil.copy2(video, out / "video.mp4")
        if timings.is_file():
            durs = json.loads(timings.read_text(encoding="utf-8"))
            if len(durs) != n_slides:
                print(f"WARNING: {len(durs)} timings for {n_slides} slides — subtitles may drift", file=sys.stderr)
            cues = build_cues(repo, module)
            write_subtitles(cues, out)
            has_subs = True
            total = sum(float(d["duration"]) for d in durs)
            runtime = f"{int(total // 60)}:{int(total % 60):02d}"
    else:
        print("NOTE: no video.mp4 yet — the page shows a placeholder. Run narrate_clips.sh, then rebuild.")

    copy_lab(repo, out)
    build_page(module, out, n_slides, has_video, has_subs, runtime)

    size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file()) / 1e6
    print(f"Built {out} — {n_slides} slides, video: {'yes' if has_video else 'no'}, "
          f"subtitles: {'yes' if has_subs else 'no'}, {size:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
