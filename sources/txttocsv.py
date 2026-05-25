import csv
import re

input_file = "Digbib_Odyssee.txt"
output_file = "Digbib_Odyssee.csv"

rows = []
book_number = 0
line_number = 0

with open(input_file, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        
        if not line:
            continue
        
        # "n. Gesang"
        match = re.fullmatch(r"(\d+)\.\s*Gesang", line)
        if match:
            book_number = int(match.group(1))
            continue
        
        # reine Zahlenzeilen
        if re.fullmatch(r"\d+", line):
            continue
        
        line_number += 1
        rows.append([line_number, book_number, line])

with open(output_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["line_number", "book_number", "original_text"])
    writer.writerows(rows)

print(f"{line_number} Zeilen in {output_file} geschrieben.")
