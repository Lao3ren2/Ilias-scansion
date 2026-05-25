#Vibecoded by claude
"""
parse_ilias.py
Parses textgrid_Ilias_qhzn_0.xml (TEI/XML) into a CSV with columns:
  line_number, book_number, original_text

Line numbers run continuously across all books (never reset).
Books are identified from <div subtype="work:no" n="…/N. Gesang"> elements.
Text lines come from:
  - <l> elements (most lines)
  - <p rend="zenoPLm4n8"> elements (the opening line of each book, present in
    23 of 24 books; book 8 uses a plain <l> instead)

Usage:
    python parse_ilias.py [input_xml] [output_csv]

Defaults:
    input  = textgrid_Ilias_qhzn_0.xml  (same directory as script)
    output = ilias.csv
"""

import csv
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

DEFAULT_INPUT  = Path(__file__).parent / "Textgrid_Odyssee.xml"
DEFAULT_OUTPUT = Path(__file__).parent / "Textgrid_Odyssee.csv"

TEI_NS = "http://www.tei-c.org/ns/1.0"


def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def book_number_from_n(n_attr: str) -> int | None:
    match = re.search(r"(\d+)\.\s*Gesang", n_attr)
    return int(match.group(1)) if match else None


def is_verse_p(elem) -> bool:
    """<p rend="zenoPLm4n8"> is used as the opening verse line in most books."""
    return strip_ns(elem.tag) == "p" and "zenoPLm4n8" in elem.get("rend", "")


def walk_book(div, book_no: int, results: list) -> None:
    """
    Recursively walk a book div in document order, collecting verse lines.
    A verse line is either:
      - any <l> element, OR
      - a <p rend="zenoPLm4n8"> element (the incipit line of most books)
    We skip <p> elements that are inside <div subtype="work:no"> nested children
    that are themselves another book (shouldn't happen in the Ilias, but guard anyway).
    """
    for child in div:
        local = strip_ns(child.tag)

        # Don't recurse into nested book divs (shouldn't exist, but be safe)
        if local == "div" and child.get("subtype") == "work:no":
            continue

        if local == "l" or is_verse_p(child):
            text = "".join(child.itertext()).strip()
            if text:
                results.append((book_no, text))
        else:
            # Recurse into any other container element
            walk_book(child, book_no, results)


def parse(input_path: Path, output_path: Path) -> None:
    print(f"Reading : {input_path}")

    tree = ET.parse(str(input_path))
    root = tree.getroot()

    rows: list[tuple[int, int, str]] = []
    line_number = 0

    for div in root.iter(f"{{{TEI_NS}}}div"):
        if div.get("subtype") != "work:no":
            continue
        book_no = book_number_from_n(div.get("n", ""))
        if book_no is None:
            continue

        book_lines: list[tuple[int, str]] = []
        walk_book(div, book_no, book_lines)

        for _, text in book_lines:
            line_number += 1
            rows.append((line_number, book_no, text))

    print(f"Writing : {output_path}  ({line_number:,} lines across "
          f"{len({r[1] for r in rows})} books)")

    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["line_number", "book_number", "original_text"])
        writer.writerows(rows)

    print("Done.")


if __name__ == "__main__":
    inp = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    parse(inp, out)
