# English Practice

A private reading-and-writing page for becoming more eloquent in English. It runs
as a Claude artifact on claude.ai, so Claude reviews my writing on my own plan,
with no API key.

## Why this exists

I am a researcher and a non-native English speaker. My English is past the
intermediate level, where apps like Duolingo stop helping. My goal is to speak and
write about ideas with the precision and ease of a good native speaker: to argue
in a discussion, explain a complex thought, and choose the exact word.

This project is built on four observations:

- **My bottleneck is expression, not ideas.** I have many thoughts, often not
  well sorted. What holds me back is finding precise, native wording and correct
  grammar for long, complex sentences.
- **Wording matters more than grammar.** Readers misunderstand me more often
  because of an unnatural word or collocation than because of a grammar mistake.
  So the review fixes meaning first, then wording, then grammar, then structure.
- **Skill comes from exposure and free practice, not drills.** Rhetorical and
  argumentative techniques appear naturally once you have read and analysed
  enough good examples, the way proof techniques do in mathematics. So the tool
  never assigns a topic or a technique. I read real authors, write whatever I
  want, and review it afterwards.
- **Laziness, distraction and friction kill most learning.** The page opens
  straight to a passage, with no setup and no questions. The writing box sits
  next to the text, and the review comes back in under a minute. The library
  never runs out, so I never have to search for material.

I chose real authors over AI-written essays on purpose: imitating fluent but
generic model prose would teach the wrong style.

## How a session works

Each session:

1. **Read** a passage. Hand-picked first, then drawn automatically from the shelf.
2. **Write** whatever I want: a reaction, an argument, a summary. Or skip it.
3. **Review.** Claude returns:
   - my whole text, corrected in my own voice, with every change highlighted;
   - at most 6 notes, in priority order: meaning → wording → grammar → structure;
   - expressions from the passage worth learning, each marked "modern" or "dated";
   - anything else worth pointing out, or nothing.

## Everyday English: Revise

Eloquence and daily English fail in different ways, so they get different tabs.
**Revise** is for the English of my own life:

- **How do I say…?** A short question, in Chinese or English, gets 2–3 natural
  ways to say it, each with its register. Hard English words in the question
  itself are offered too.
- **Paste** a message, an email, or a whole chat. Claude guesses the setting and
  register (I can change them), corrects only my own lines, and corrects them
  for that setting, so a casual chat stays casual. Expressions worth keeping
  come from the whole paste, including other people's lines. Text that is not
  mine at all gets a language study instead.

## Recall

Any phrase can be **kept** with one tap: in a review, an Explain answer, or a
"How do I say" answer. Nothing is added automatically. **Recall** shows one kept
phrase at a time as a cue (its example with a blank, or my original question),
then the answer. It uses 5 Leitner boxes (1, 2, 4, 8, 16 days) and at most 10 new
phrases a day, so the deck never piles up.

I can select any phrase in a passage and press **Explain**. Every session is
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
| `tools/build.py` | Assembles `dist/english-practice.html` and `dist/shelf/`. |

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

> Run `python3 tools/build.py`, then publish `dist/english-practice.html` as an artifact
> with capabilities `{"sample": {}, "db": {}, "user": {}, "downloads": true}`, and
> publish every file in `dist/shelf/` alongside it as `shelf/<name>.json`.
> To update the existing page, pass its URL.

The current page: https://claude.ai/artifact/CKuK9hYg1BGqm1d5K74Hrh

My history is stored inside that artifact, not in this repo. A new artifact
starts empty, so I use **History → Save backup (JSON)** regularly. **Load backup**
restores it into any copy of the page.

## Sources and licence

Passages are public-domain texts from Project Gutenberg and
[Standard Ebooks](https://standardebooks.org).
