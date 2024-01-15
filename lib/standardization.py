'''Text cleaning and conversions'''
import re 
from lib.abbreviations import * 

def clean_word(word): 
    word = word.lower().strip(".")
    word = re.sub("v","u",word) # replace all v's with u's 
    word = re.sub(r"^i","j",word) # replace initial i's to j's 
    word = re.sub(r"(?<=\w)y(?=\w)","i",word) # replace y's that occur within words into i's
    word = re.sub(r"[^\x00-\x7F]+","*",word) # replace all non-ASCII characters with asterisks 
    return word 

# convert a roman numeral to its integer format 
# The longest book in the Bible is Psalms with 150 chapters, 
# and the longest chapter (Psalms 119) has 176 verses
roman_to_int = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
def convert_numeral(numeral):
    if not re.search(r'^(c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$', numeral): 
        return "invalid"
    num = 0
    for idx, n in enumerate(numeral):
        if idx > 0 and roman_to_int[n] > roman_to_int[numeral[idx - 1]]:
            # case where we are one less than a multiple of ten or five (e.g., IX or IV)
            num += roman_to_int[n] - 2 * roman_to_int[numeral[idx - 1]]
        else:
            num += roman_to_int[n] 
    return num