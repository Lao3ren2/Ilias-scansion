"""
Build verses_syllabified.csv: one row per verse with normalized and syllabified text
"""

import csv
import re
from pathlib import Path
from syllabify_word import Syllabifier


VERSES = "../sources/Digbib_Odyssee.csv"
MANUAL = "manual_syllabification.csv"
OUT = "digbib_odyssee_syllabified.csv"


def clean_verse_words(text: str) -> list[str]:
    WORD_CLEAN_RE = re.compile(r"[^\w\säöüÄÖÜß']")
    clean = WORD_CLEAN_RE.sub(" ", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean.split() if clean else []


def main() -> None:
    root = Path(__file__).resolve().parent
    
    rows_out: list[dict[str, str]] = []
    S = Syllabifier()
    with (root / VERSES).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            line_number = row.get("line_number", "")
            book_number = row.get("book_number", "")
            orig = row.get("original_text", "")
            words = clean_verse_words(orig)
            verse_norm = " ".join(w.lower() for w in words)
            
            syllabified_words = [S.syllabify_word(w.lower()) for w in words]
            verse_syl = "|".join(syllabified_words)
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
