#!/usr/bin/env python3
"""Assemble dist/english-practice.html from src/template.html + data/library.json,
and copy the shelf to dist/shelf/. Publish dist/ as described in README.md."""
import json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
lib = json.loads((ROOT / "data/library.json").read_text())
page = (ROOT / "src/template.html").read_text()
assert "__LIBRARY__" in page, "template is missing the __LIBRARY__ placeholder"
page = page.replace("__LIBRARY__", json.dumps(lib, ensure_ascii=False).replace("</", "<\\/"))

dist = ROOT / "dist"
if dist.exists():
    shutil.rmtree(dist)
(dist / "shelf").mkdir(parents=True)
(dist / "english-practice.html").write_text(page)
for f in sorted((ROOT / "data/shelf").glob("*.json")):
    shutil.copy(f, dist / "shelf" / f.name)
n = len(list((dist / "shelf").glob("*.json")))
print(f"dist/english-practice.html ({len(page)//1024} KB) + {n} shelf files")
