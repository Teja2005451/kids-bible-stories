#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge newly authored kids content into 01-genesis.json.

WHY THIS EXISTS
---------------
Genesis has 1,533 verses. The app needs two authored Telugu fields per
verse that no Bible file supplies:

    kidsTeluguSummary   - simple story explanation for a child
    drawingPrompt       - a drawing challenge

Chapters 1-3 are authored. Chapters 4-50 are not, so the app correctly
shows its "stories not ready yet" empty state for them.

HOW TO ADD A CHAPTER
--------------------
1. Open genesis-template-all-1533.json. It holds every Genesis verse with
   the real rawTeluguText already filled in and the two authored fields
   empty.
2. Fill in kidsTeluguSummary and drawingPrompt for the verses you want.
3. Save that file and run:

       python3 merge-kids-content.py

Only records where BOTH authored fields are non-empty are published to
01-genesis.json. Everything else is left out, so a half-finished chapter
never reaches a child as a blank card.

SCRIPTURE INTEGRITY
-------------------
rawTeluguText is copied verbatim from the template and is never edited,
generated or translated by this script.
"""

import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "genesis-template-all-1533.json")
OUTPUT = os.path.join(HERE, "01-genesis.json")

REQUIRED = ("chapterIndex", "verseIndex", "rawTeluguText",
            "kidsTeluguSummary", "drawingPrompt")


def main():
    if not os.path.exists(TEMPLATE):
        sys.exit("Template not found: %s" % TEMPLATE)

    with open(TEMPLATE, encoding="utf-8") as fh:
        records = json.load(fh)

    if not isinstance(records, list):
        sys.exit("Template root must be a JSON array.")

    published = []
    skipped_incomplete = 0
    skipped_invalid = 0

    for idx, rec in enumerate(records):
        if not isinstance(rec, dict) or any(k not in rec for k in REQUIRED):
            skipped_invalid += 1
            print("  ! record %d is missing required keys; skipped." % idx)
            continue

        chapter = int(rec["chapterIndex"])
        verse = int(rec["verseIndex"])

        if not (1 <= chapter <= 50) or verse < 1:
            skipped_invalid += 1
            print("  ! record %d has an out-of-range index; skipped." % idx)
            continue

        summary = (rec["kidsTeluguSummary"] or "").strip()
        prompt = (rec["drawingPrompt"] or "").strip()

        # Publish only fully authored verses.
        if not summary or not prompt:
            skipped_incomplete += 1
            continue

        published.append({
            "chapterIndex": chapter,
            "verseIndex": verse,
            "rawTeluguText": rec["rawTeluguText"],
            "kidsTeluguSummary": summary,
            "drawingPrompt": prompt,
        })

    published.sort(key=lambda r: (r["chapterIndex"], r["verseIndex"]))

    with open(OUTPUT, "w", encoding="utf-8") as fh:
        json.dump(published, fh, ensure_ascii=False, indent=2)

    per_chapter = Counter(r["chapterIndex"] for r in published)

    print("\nWrote %s" % OUTPUT)
    print("  published verses : %d" % len(published))
    print("  not yet authored : %d" % skipped_incomplete)
    print("  invalid records  : %d" % skipped_invalid)
    print("  chapters ready   : %s"
          % ", ".join(str(c) for c in sorted(per_chapter)))


if __name__ == "__main__":
    main()
