#!/usr/bin/env python3
"""Checks that a translated article is a faithful copy of its English original where it must be.

A translation file sits next to the English one:  content/articles/feedstock.md  ->  feedstock.hi.md

What this proves (deterministic, no AI involved):
  * the English original exists and is itself published
  * the translation was made from the CURRENT English version (same `updated` date)
  * topic, sources, confidence and lede_refs are unchanged
  * every reference keeps its n, title, url, host and quote EXACTLY (quotes stay in the source's own words)
  * every number in a sentence is unchanged (figures like 50:1 or 12 to 24 cannot drift)
  * every sentence still ends with its source marker, and each paragraph cites the same sources in the same order
  * no links, HTML or Devanagari digits were added
  * nothing was left untranslated (each paragraph and finding contains Devanagari)

What it cannot prove: that the Hindi is good Hindi and means the same thing. That is the human review.

A translation that is going live (draft: false) must pass, or the deploy stops.
A draft only prints warnings, so you can work on it. Use --strict to treat draft problems as errors.

Usage:  python tools/check_translation.py [--root .] [--strict]      (needs: pip install pyyaml)
"""
import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

TRANSLATION_RE = re.compile(r"^(?P<stem>.+)\.(?P<lang>[a-z]{2,3})\.md$")
MARKER_RE = re.compile(r"\[(\d+)\]\(#s(\d+)\)")
NUMBER_RE = re.compile(r"\d+(?:[:.,–-]\d+)*")
DEVANAGARI_RE = re.compile(r"[ऀ-ॿ]")
DEVANAGARI_DIGIT_RE = re.compile(r"[०-९]")
SENTENCE_END_RE = re.compile(r"।|[?!]|\.(?=\s|$)")  # danda, ? !, or a full stop before space/end
EXACT_REF_FIELDS = ("n", "title", "url", "host", "quote")
SAME_FIELDS = ("topic", "sources", "confidence", "lede_refs")


def split_file(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        raise ValueError("front matter not found")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def blocks(body: str):
    out = []
    for raw in re.split(r"\n\s*\n", body.strip()):
        raw = raw.strip()
        if not raw:
            continue
        h = re.match(r"^(#{1,6})\s+(.*)$", raw, re.S)
        out.append(("h" + str(len(h.group(1))), h.group(2)) if h else ("p", raw))
    return out


def marker_runs(text: str):
    """Source numbers in order, with immediate repeats collapsed: [4] [3] [3] -> 4, 3."""
    run = []
    for n, _ in MARKER_RE.findall(text):
        if not run or run[-1] != n:
            run.append(n)
    return run


def numbers(text: str):
    return Counter(NUMBER_RE.findall(MARKER_RE.sub("", text)))


def check_pair(en_path: Path, tr_path: Path, lang: str):
    problems = []
    add = problems.append
    en_fm, en_body = split_file(en_path)
    tr_fm, tr_body = split_file(tr_path)

    # 1. The English original must be published, and the translation must track its current version.
    if en_fm.get("draft") is not False or en_fm.get("status") != "approved":
        add("the English original is not published yet (needs draft: false and status: approved)")
    if tr_fm.get("lang") != lang:
        add(f"front matter lang is {tr_fm.get('lang')!r}, expected {lang!r}")
    if str(tr_fm.get("updated")) != str(en_fm.get("updated")):
        add(f"English was updated {en_fm.get('updated')} but this translation says {tr_fm.get('updated')}: "
            f"re-translate from the current English, then set updated to {en_fm.get('updated')}")
    for k in SAME_FIELDS:
        if tr_fm.get(k) != en_fm.get(k):
            add(f"{k} differs from English ({tr_fm.get(k)!r} vs {en_fm.get(k)!r}); it must be identical")

    # 2. References: sources and quotes are copied, only `finding` is translated.
    en_refs, tr_refs = en_fm.get("references") or [], tr_fm.get("references") or []
    if len(en_refs) != len(tr_refs):
        add(f"{len(tr_refs)} references but English has {len(en_refs)}")
    for i, (a, b) in enumerate(zip(en_refs, tr_refs), start=1):
        for k in EXACT_REF_FIELDS:
            if a.get(k) != b.get(k):
                add(f"reference {i}: {k} must be identical to English (quotes stay in the source's own words)")
        finding = str(b.get("finding", ""))
        if not DEVANAGARI_RE.search(finding):
            add(f"reference {i}: finding is empty or not translated")
        if numbers(str(a.get("finding", ""))) != numbers(finding):
            add(f"reference {i}: numbers in finding differ from English "
                f"({sorted(numbers(str(a.get('finding', ''))).elements())} vs {sorted(numbers(finding).elements())})")
    for k in ("summary", "lede"):
        v = str(tr_fm.get(k, ""))
        if not DEVANAGARI_RE.search(v):
            add(f"{k} is empty or not translated")
        elif numbers(str(en_fm.get(k, ""))) != numbers(v):
            add(f"numbers in {k} differ from English")

    # 3. Body, block by block.
    en_blocks, tr_blocks = blocks(en_body), blocks(tr_body)
    if [t for t, _ in en_blocks] != [t for t, _ in tr_blocks]:
        add(f"structure differs: English has {len(en_blocks)} blocks "
            f"({' '.join(t for t, _ in en_blocks)}), this has {len(tr_blocks)} ({' '.join(t for t, _ in tr_blocks)})")
    max_n = len(en_refs)
    for idx, ((kind, en_text), (_, tr_text)) in enumerate(zip(en_blocks, tr_blocks), start=1):
        where = f"block {idx}"
        if numbers(en_text) != numbers(tr_text):
            add(f"{where}: numbers differ from English "
                f"({sorted(numbers(en_text).elements())} vs {sorted(numbers(tr_text).elements())})")
        if DEVANAGARI_DIGIT_RE.search(tr_text):
            add(f"{where}: use 0-9, not Devanagari digits, so figures match the sources")
        if re.search(r"<[A-Za-z/!]", tr_text):
            add(f"{where}: HTML is not allowed")
        stripped = MARKER_RE.sub("", tr_text)
        if "](" in stripped or re.search(r"https?://", stripped):
            add(f"{where}: links are not allowed except the [n](#sn) source markers")
        if not DEVANAGARI_RE.search(tr_text):
            add(f"{where}: no Devanagari text; it looks untranslated")
        if kind != "p":
            continue
        bad = [m for m in MARKER_RE.findall(tr_text) if m[0] != m[1]]
        if bad:
            add(f"{where}: marker text and target must match, like [2](#s2)")
        if marker_runs(en_text) != marker_runs(tr_text):
            add(f"{where}: cites sources {marker_runs(tr_text)} but English cites {marker_runs(en_text)}")
        if any(int(n) < 1 or int(n) > max_n for n, _ in MARKER_RE.findall(tr_text)):
            add(f"{where}: cites a source number that does not exist")
        if not re.search(r"\[\d+\]\(#s\d+\)\s*$", tr_text):
            add(f"{where}: the paragraph must end with a source marker")
        masked = MARKER_RE.sub("\u0000", tr_text)  # each marker becomes one placeholder character
        for m in SENTENCE_END_RE.finditer(masked):
            if not re.match(r"\s*\u0000", masked[m.end():]):
                add(f"{where}: a sentence ends without a source marker near "
                    f"\"{masked[max(0, m.start() - 25):m.end()].strip()}\"")
                break
    return problems, tr_fm.get("draft") is False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="repository root (default: current folder)")
    ap.add_argument("--strict", action="store_true", help="treat problems in drafts as errors too")
    args = ap.parse_args()

    articles = Path(args.root) / "content" / "articles"
    gh = os.environ.get("GITHUB_ACTIONS") == "true"
    failed = checked = 0
    for tr_path in sorted(articles.glob("*.md")):
        m = TRANSLATION_RE.match(tr_path.name)
        if not m or tr_path.name.startswith("_"):
            continue
        checked += 1
        en_path = articles / f"{m.group('stem')}.md"
        rel = tr_path.relative_to(args.root).as_posix()
        if not en_path.exists():
            problems, live = [f"there is no English original {en_path.name}"], True
        else:
            try:
                problems, live = check_pair(en_path, tr_path, m.group("lang"))
            except Exception as exc:  # a broken file must not pass silently
                problems, live = [f"could not be read: {exc}"], True
        blocking = bool(problems) and (live or args.strict)
        label = "LIVE" if live else "draft"
        if not problems:
            print(f"ok    {rel} ({label})")
            continue
        for p in problems:
            if gh:
                print(f"::{'error' if blocking else 'warning'} file={rel}::{p}")
            else:
                print(f"{'FAIL' if blocking else 'warn'}  {rel} ({label}): {p}")
        failed += blocking
    if checked == 0:
        print("no translated articles found")
    print(f"{checked} translated article(s) checked, {failed} blocking")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
