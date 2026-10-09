# Commonplace Book

A private reading-and-writing page for improving English eloquence. It runs as a
Claude artifact on claude.ai, so Claude reviews your writing on your own plan,
with no API key.

Each session:

1. **Read** a passage. Hand-picked first, then drawn automatically from the shelf.
2. **Write** whatever you want: a reaction, an argument, a summary. Or skip it.
3. **Review.** Claude returns:
   - your whole text, corrected in your own voice, with every change highlighted;
   - at most 6 notes, in priority order: meaning → wording → grammar → structure;
   - expressions from the passage worth learning, each marked "modern" or "dated";
   - anything else worth pointing out, or nothing.

You can select any phrase in a passage and press **Explain**. Every session is
saved to History, and History can export Markdown or a JSON backup.

## Where things live

| Path | What |
|---|---|
| `src/template.html` | The page: HTML, CSS and JS in one file. The review prompt is in `buildPrompt()`. |
| `data/library.json` | 20 hand-picked passages (Russell, Mill, Hume, W. James, Emerson, Thoreau). |
| `data/shelf/` | About 3,900 passages from 27 public-domain books, one JSON file per book. |
| `sources/shelf_sources.txt` | The books on the shelf (Standard Ebooks repo names). |
| `tools/build_library.py` | Rebuilds `library.json` from Project Gutenberg (GitHub mirror). |
| `tools/build_shelf.py` | Rebuilds `data/shelf/` from Standard Ebooks. |
| `tools/build.py` | Assembles `dist/commonplace.html` and `dist/shelf/`. |

## Rebuild

```sh
python3 tools/build_shelf.py     # only when the book list changed (takes ~2 min)
python3 tools/build_library.py   # only when the hand-picked specs changed
python3 tools/build.py           # always: produces dist/
```

To add books, append Standard Ebooks repo names to `sources/shelf_sources.txt`.
The names are the ones under github.com/standardebooks.

## Publish (or republish) on claude.ai

Artifacts are published from a Claude session that has this repo. Ask Claude:

> Run `python3 tools/build.py`, then publish `dist/commonplace.html` as an artifact
> with capabilities `{"sample": {}, "db": {}, "user": {}, "downloads": true}`, and
> publish every file in `dist/shelf/` alongside it as `shelf/<name>.json`.
> To update the existing page, pass its URL.

The current page: https://claude.ai/artifact/CKuK9hYg1BGqm1d5K74Hrh

Your history is stored inside that artifact, not in this repo. A new artifact
starts empty, so use **History → Save backup (JSON)** regularly. **Load backup**
restores it into any copy of the page.

## Sources and licence

Passages are public-domain texts from Project Gutenberg and
[Standard Ebooks](https://standardebooks.org).
