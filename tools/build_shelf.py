#!/usr/bin/env python3
"""Build data/shelf/ (index.json + one JSON file per book): reading-sized windows cut from Standard Ebooks texts.

Standard Ebooks (https://standardebooks.org) publishes carefully proofread
public-domain books; each book is a GitHub repo under github.com/standardebooks.
This script reads sources/shelf_sources.txt (one repo name per line), downloads
each book's chapters, and cuts them into passages of roughly 220-600 words that
never cross a chapter boundary.

Usage:  python3 tools/build_shelf.py            (from the project root)
Add a book: append its repo name to sources/shelf_sources.txt and rerun.
"""
import html, json, re, sys, time, urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/standardebooks/{repo}/master/src/epub/{path}"
SKIP = re.compile(r"(imprint|titlepage|halftitle|colophon|uncopyright|endnotes|dedication|epigraph|loi|index|bibliography|appendix|footnotes|glossary)", re.I)
MIN_WORDS, TARGET, MAX_WORDS = 220, 320, 600
PER_BOOK = 160          # cap per book, spread evenly through it, so no single book dominates


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2)


class Paras(HTMLParser):
    """Collect <p> text (italics as _x_, footnote markers dropped) and the first heading."""
    def __init__(self):
        super().__init__()
        self.paras, self.heading = [], ""
        self.buf, self.in_p, self.in_h, self.skip, self.hbuf = [], False, False, 0, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.skip or (tag == "a" and "noteref" in (a.get("epub:type") or "")) or tag in ("sup",):
            self.skip += 1; return
        if tag == "p": self.in_p, self.buf = True, []
        elif tag in ("h2", "h3", "h4") and not self.heading: self.in_h, self.hbuf = True, []
        elif tag in ("i", "em") and self.in_p: self.buf.append("_")
        elif tag == "br" and self.in_p: self.buf.append(" ")

    def handle_endtag(self, tag):
        if self.skip:
            if tag in ("a", "sup"): self.skip -= 1
            return
        if tag == "p" and self.in_p:
            t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            t = re.sub(r"_\s*_", "", t)
            if t: self.paras.append(t)
            self.in_p = False
        elif tag in ("i", "em") and self.in_p: self.buf.append("_")
        elif tag in ("h2", "h3", "h4") and self.in_h:
            self.heading = re.sub(r"\s+", " ", "".join(self.hbuf)).strip(); self.in_h = False

    def handle_data(self, d):
        if self.skip: return
        if self.in_p: self.buf.append(d)
        elif self.in_h: self.hbuf.append(d)


def meta(repo):
    opf = get(RAW.format(repo=repo, path="content.opf"))
    title = re.search(r"<dc:title[^>]*>(.*?)</dc:title>", opf, re.S)
    author = re.search(r'<dc:creator id="author[^"]*"[^>]*>(.*?)</dc:creator>', opf, re.S) or re.search(r"<dc:creator[^>]*>(.*?)</dc:creator>", opf, re.S)
    return html.unescape(title.group(1).strip()) if title else repo, html.unescape(author.group(1).strip()) if author else ""


def chapters(repo):
    toc = get(RAW.format(repo=repo, path="toc.xhtml"))
    seen, out = set(), []
    for href, label in re.findall(r'<a href="(text/[^"#]+)[^>]*>(.*?)</a>', toc, re.S):
        if href in seen or SKIP.search(href): continue
        seen.add(href)
        out.append((href, html.unescape(re.sub(r"<[^>]+>", "", label)).strip()))
    return out


def windows(paras):
    """Greedy, non-overlapping runs of whole paragraphs."""
    out, cur, n = [], [], 0
    for p in paras:
        w = len(p.split())
        if w > MAX_WORDS:                      # one huge paragraph: split it at sentence ends
            if cur and n >= MIN_WORDS: out.append(cur)
            cur, n = [], 0
            piece, pn = [], 0
            for sent in re.split(r"(?<=[.?!])\s+(?=[A-Z“\"‘])", p):
                piece.append(sent); pn += len(sent.split())
                if pn >= TARGET:
                    out.append([" ".join(piece) + (" …" if sent is not p else "")]); piece, pn = [], 0
            if pn >= MIN_WORDS: out.append([" ".join(piece)])
            continue
        if n + w > MAX_WORDS and n >= MIN_WORDS:
            out.append(cur); cur, n = [], 0
        cur.append(p); n += w
        if n >= TARGET and p.rstrip().endswith((".", "?", "!", "”", '"')):
            out.append(cur); cur, n = [], 0
    if cur and n >= MIN_WORDS: out.append(cur)
    return out


def looks_like_prose(text):
    letters = sum(c.isalpha() for c in text)
    return letters / max(1, len(text)) > 0.72 and text.count("|") == 0


def main():
    repos = [l.strip() for l in (ROOT / "sources/shelf_sources.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
    books, items = [], []
    for repo in repos:
        try:
            title, author = meta(repo)
            chs = chapters(repo)
        except Exception as e:
            print(f"skip {repo}: {e}", file=sys.stderr); continue
        bi = len(books); mine = []
        for href, label in chs:
            try:
                x = Paras(); x.feed(get(RAW.format(repo=repo, path=href)))
            except Exception as e:
                print(f"  miss {repo}/{href}: {e}", file=sys.stderr); continue
            section = x.heading if (not label or re.fullmatch(r"[IVXLCDM0-9.]+", label)) and x.heading else label
            if re.fullmatch(r"[IVXLCDM0-9.]+", section or ""): section = "Chapter " + section.rstrip(".")
            for w in windows(x.paras):
                text = "\n\n".join(w)
                if not looks_like_prose(text): continue
                mine.append((section, text))
        if len(mine) > PER_BOOK:
            step = len(mine) / PER_BOOK
            mine = [mine[int(i * step)] for i in range(PER_BOOK)]
        if not mine:
            print(f"    0  {author} — {title} (no usable passages)"); continue
        bi = len(books)
        books.append({"repo": repo, "title": title, "author": author, "n": len(mine)})
        shelf = [{"id": f"{repo}#{i}", "s": sec, "t": t} for i, (sec, t) in enumerate(mine)]
        (ROOT / "data/shelf").mkdir(parents=True, exist_ok=True)
        (ROOT / f"data/shelf/{bi}.json").write_text(json.dumps(shelf, ensure_ascii=False, separators=(",", ":")))
        items += shelf
        print(f"{len(mine):5d}  {author} — {title}")
    index = {"books": books, "source": "Standard Ebooks, public domain", "built": time.strftime("%Y-%m-%d")}
    (ROOT / "data/shelf/index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1))
    print(f"{len(items)} passages from {len(books)} books → data/shelf/")


if __name__ == "__main__":
    main()
