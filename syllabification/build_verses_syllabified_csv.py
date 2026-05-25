"""
Build verses_syllabified.csv: one row per verse with normalized text and
compact per-syllable | segmentation using manual overrides, then pyphen
generated on-the-fly.
"""

import csv
import re
from collections import Counter
from pathlib import Path
import pyphen


WORD_CLEAN_RE = re.compile(r"[^\w\säöüÄÖÜß']")

VERSES = "../sources/Digbib_Odyssee.csv"
MANUAL = "manual_syllabification.csv"
OUT = "digbib_odyssee_syllabified.csv"


def clean_verse_words(text: str) -> list[str]:
    clean = WORD_CLEAN_RE.sub(" ", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean.split() if clean else []


def load_manual(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            w = (row.get("word") or "").strip().lower()
            sy = (row.get("manually_syllabified_word") or "").strip()
            if w:
                out[w] = sy
    return out


def syllabify_token(
    token: str,
    wl: str,
    manual: dict[str, str],
    pyphen_dict: pyphen.Pyphen,
) -> str:
    if wl in manual:
        return manual[wl]
    # Use pyphen to generate syllabification on-the-fly
    syl = pyphen_dict.inserted(wl,hyphen="|")
    return syl


def main() -> None:
    root = Path(__file__).resolve().parent
    manual = load_manual(root / MANUAL)
    pyphen_dict = pyphen.Pyphen(lang='de')

    rows_out: list[dict[str, str]] = []
    with (root / VERSES).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            line_number = row.get("line_number", "")
            book_number = row.get("book_number", "")
            orig = row.get("original_text", "") or ""
            tokens = clean_verse_words(orig)
            verse_norm = " ".join(t.lower() for t in tokens)
            syl_parts = [
                syllabify_token(t, t.lower(), manual, pyphen_dict)
                for t in tokens
            ]
            verse_syl = "|".join(syl_parts)
            rows_out.append(
                {
                    "line_number": line_number,
                    "book_number": book_number,
                    "original_text": orig,
                    "verse_normalized": verse_norm,
                    "verse_syllabified": verse_syl,
                }
            )

    fieldnames = [
        "line_number",
        "book_number",
        "original_text",
        "verse_normalized",
        "verse_syllabified",
    ]
    with (root / OUT).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(rows_out)

    print(f"wrote {len(rows_out)} rows to {OUT}")


if __name__ == "__main__":
    main()
