import re
import pyphen
import csv

MANUAL ="manual_syllabification.csv"



class Syllabifier:
    def __init__(self):
        #load manual syllabifications
        self.manual = dict()
        with open(MANUAL,"r",encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.manual[row["word"]] = row["manually_syllabified_word"]
        print(f"loaded {len(self.manual)} manual syllabifications")

        self.pyphen_dict = pyphen.Pyphen(lang='de')
        
    def syllabify_word(self, word):
        if word in self.manual:
            return self.manual[word]
        return self.pyphen_dict.inserted(word,hyphen="|")

    def is_bad_syllable(self,syl):
        #no Vowels
        pattern1 = re.compile(r'^[^aeiouäöüAEIOUÄÖÜëËïÏyY]+$')
        if pattern1.match(syl):
            return True

        #Vowel-Character-Vowel
        pattern2 = re.compile(r'.*[aeiouäöüAEIOUÄÖÜëËïÏ].+[aeiouäöüAEIOUÄÖÜëËïÏ].*')
        if pattern2.match(syl):
            return True

        return False
    

    
