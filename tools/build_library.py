#!/usr/bin/env python3
"""Build data/library.json: the 20 hand-picked passages shown first.

Texts come from Project Gutenberg via its GitHub mirror (github.com/GITenberg).
Each spec names an anchor phrase; the script takes the paragraph containing it,
plus `before`/`after` neighbouring paragraphs. To add a passage, add a spec line
(book file must be in BOOKS) and rerun:  python3 tools/build_library.py
"""
import json, os, re, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache/gutenberg"
BOOKS = {  # file name -> GITenberg repo/path
    "5827.txt": "The-Problems-of-Philosophy_5827/master/5827.txt",
    "34901.txt": "On-Liberty_34901/master/34901.txt",
    "9662.txt": "An-Enquiry-Concerning-Human-Understanding_9662/master/9662.txt",
    "26659.txt": "The-Will-to-Believe-and-Other-Essays-in-Popular-Philosophy_26659/master/26659.txt",
    "205.txt": "Walden-and-On-The-Duty-Of-Civil-Disobedience_205/master/205.txt",
    "690.txt": "Proposed-Roads-to-Freedom_690/master/690.txt",
    "16643.txt": "Essays-by-Ralph-Waldo-Emerson_16643/master/16643.txt",
    "25447.txt": "Mysticism-and-Logic-and-Other-Essays_25447/master/25447-0.txt",
}

def paras(fn):
    path = CACHE / fn
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen("https://raw.githubusercontent.com/GITenberg/" + BOOKS[fn], timeout=60) as r:
            path.write_bytes(r.read())
    raw = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    ps = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", raw)]
    return [p for p in ps if p]

specs = [
 # id, file, author, work, year, section, anchor, before, after
 ("russell-value","5827.txt","Bertrand Russell","The Problems of Philosophy",1912,"Ch. XV, The Value of Philosophy","The man who has no tincture",0,1),
 ("russell-certain","5827.txt","Bertrand Russell","The Problems of Philosophy",1912,"Ch. I, Appearance and Reality","Is there any knowledge in the world which is so certain",0,1),
 ("russell-worship","25447.txt","Bertrand Russell","Mysticism and Logic",1918,"A Free Man's Worship","Brief and powerless is Man",-1,0),
 ("russell-math","25447.txt","Bertrand Russell","Mysticism and Logic",1918,"The Study of Mathematics","Mathematics, rightly viewed",0,0),
# ("russell-cause","25447.txt","Bertrand Russell","Mysticism and Logic",1918,"On the Notion of Cause","The law of causality, I believe",0,0),
 ("russell-roads","690.txt","Bertrand Russell","Proposed Roads to Freedom",1918,"Ch. VIII, The World as It Could Be Made","The world that we must seek",-1,0),
 ("mill-silencing","34901.txt","John Stuart Mill","On Liberty",1859,"Ch. II, Of the Liberty of Thought and Discussion","peculiar evil of silencing",0,0),
 ("mill-own-side","34901.txt","John Stuart Mill","On Liberty",1859,"Ch. II, Of the Liberty of Thought and Discussion","He who knows only his own side",0,0),
 ("mill-harm","34901.txt","John Stuart Mill","On Liberty",1859,"Ch. I, Introductory","sole end for which mankind are warranted",0,0),
 ("mill-tree","34901.txt","John Stuart Mill","On Liberty",1859,"Ch. III, Of Individuality","Human nature is not a machine",0,0),
 ("hume-two-kinds","9662.txt","David Hume","An Enquiry Concerning Human Understanding",1748,"Sect. IV, Sceptical Doubts","All the objects of human reason or enquiry",0,1),
 ("hume-be-a-man","9662.txt","David Hume","An Enquiry Concerning Human Understanding",1748,"Sect. I, Of the Different Species of Philosophy","Be a philosopher; but",-1,0),
 ("hume-evidence","9662.txt","David Hume","An Enquiry Concerning Human Understanding",1748,"Sect. X, Of Miracles","proportions his belief to the evidence",0,0),
 ("hume-commit","9662.txt","David Hume","An Enquiry Concerning Human Understanding",1748,"Sect. XII, Of the Academical or Sceptical Philosophy","Commit it then to the flames",-1,0),
 ("james-passional","26659.txt","William James","The Will to Believe",1896,"The Will to Believe","Our passional nature not only lawfully may",0,0),
 ("james-two-ways","26659.txt","William James","The Will to Believe",1896,"The Will to Believe","There are two ways of looking at our duty",0,1),
 ("emerson-trust","16643.txt","Ralph Waldo Emerson","Essays",1841,"Self-Reliance","To believe your own thought",0,0),
 ("emerson-consistency","16643.txt","Ralph Waldo Emerson","Essays",1841,"Self-Reliance","A foolish consistency",-1,0),
 ("thoreau-woods","205.txt","Henry David Thoreau","Walden",1854,"Where I Lived, and What I Lived For","I went to the woods because",0,0),
 ("thoreau-desperation","205.txt","Henry David Thoreau","Walden",1854,"Economy","quiet desperation",0,1),
 ("thoreau-civil","205.txt","Henry David Thoreau","Civil Disobedience",1849,"Opening","I heartily accept the motto",0,0),
]

out = []
for sid, fn, au, wk, yr, sec, anc, b, a in specs:
    ps = paras(fn)
    idx = [i for i, p in enumerate(ps) if anc.lower() in p.lower()]
    if not idx:
        print("MISSING", sid); continue
    i = idx[0]
    text = "\n\n".join(re.sub(r"^\d+\.\s+", "", c) for c in ps[max(0, i + b):i + a + 1])
    text = re.sub(r"\[\d+\]|\{\d+\}\s?", "", text.replace("--", "\u2014"))
    text = re.sub(r" {2,}", " ", text)
    out.append(dict(id=sid, author=au, work=wk, year=yr, section=sec, text=text, words=len(text.split())))
    print(f"{sid:22s} {len(text.split()):4d} words")
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data/library.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(len(out), "passages → data/library.json")
