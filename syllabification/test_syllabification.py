import csv
import pyphen
import re
from syllabify_word import Syllabifier

TEST_WORDS = "../testing/odyssee_sample_words.txt"


S = Syllabifier()

with open(TEST_WORDS,"r",encoding="utf-8") as f:
    wrong = 0
    has_bad_syllable = 0
    total = 0
    wrong_syllable_count = 0
    for line in f:
        line = line.strip()
        total+=1
        word = line.replace("|","")
        syllabified = S.syllabify_word(word)
        if line!=syllabified:
            print(line,syllabified)
            wrong +=1
            if any([S.is_bad_syllable(s) for s in syllabified.split("|")]):
                has_bad_syllable +=1
            if len(line.split("|")) != len(syllabified.split("|")):
                wrong_syllable_count +=1
    print(f"{wrong} wrong syllabifications, of them {has_bad_syllable} have ill-formed syllables")
    print(f"Wrong syllable counts: {wrong_syllable_count}")
    print(f"Total words: {total}")
