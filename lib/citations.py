import re
import sys 
sys.path.append('../')
from lib.standardization import * 
from lib.sentences import *

Text = Sentences('A41135')
for idx, tuple in enumerate(Text.sentences): 
    sermon_idx, start_page, sent_str, pos, lemmatized = tuple 
    sentence, pos, lemmatized = sent_str.split(" "), pos.split(" "), lemmatized.split(" ")

    encoded = []
    in_italics, in_note = False, False 
    start_italics, start_note = -1, -1
    for t, token in enumerate(sentence): 
        if token == "STARTITALICS": 
            in_italics = True 
            start_italics += 1 
        elif token == "ENDITALICS": 
            in_italics = False 
        elif re.search(r"STARTNOTE\d+", token): 
            in_note = True 
            start_note += 1 
        elif re.search(r"ENDNOTE\d+",token): 
            in_note = False
        else:
            if in_italics and in_note: 
                it_tag, note_tag = start_italics, start_note
            elif in_italics: 
                it_tag, note_tag = start_italics, -1 
            elif in_note: 
                it_tag, note_tag = -1, start_note
            else: 
                it_tag, note_tag = -1, -1
            if token == "NONLATINALPHABET": 
                encoded.append((token, "foreign", lemmatized[t], it_tag, note_tag))
            else: 
                encoded.append((token, pos[t], lemmatized[t], it_tag, note_tag))

    sent_str = re.sub(r"STARTITALICS|ENDITALICS|STARTNOTE\d+|ENDNOTE\d+","",sent_str)
    citations, outliers, sent_str, replaced = extract_citations(sent_str) # from original
    if len(citations) > 0: 
        if len(replaced) < 2: continue 
        sent = sent_str.split(" ")
        following = {}
        for i, word in enumerate(sent):
            if re.search(r"\(REF\d+\)",word): 
                ref_idx = int(re.findall(r'\d+',word)[0])
                if i+1 < len(sent): 
                    following[ref_idx] = sent[i+1]
                else: 
                    following[ref_idx] = None
        r_idx = 0
        book = replaced[r_idx].split(" ")[0]
        new_encoding = []
        in_citation = False
        if r_idx < len(replaced): 
            next_book = replaced[r_idx+1].split(" ")[0]
        else: 
            next_book = ""

        for idx, item in enumerate(encoded):
            token,b,c,d,e = item
            word = re.sub(r"\.", " ",token)
            word = re.sub(r"\s+"," ",word)
            word = re.sub(r"([^\w\*])$","",word)
            word = re.sub("v","u",word) # replace all v's with u's 
            word = re.sub(r"^i","j",word) # replace initial i's to j's 
            word = re.sub(r"(?<=\w)y(?=\w)","i",word) # replace y's that occur within words into i's
            if word == book and idx + 1 < len(encoded):  
                next_t, next_p, next_l, d, e = encoded[idx+1]
                if next_p == next_l or next_p == "crd": 
                    new_encoding.append((token,b,c,d,e,r_idx))
                    in_citation = True 
                else: 
                    new_encoding.append((token,b,c,d,e,-1))
            elif in_citation and word != following[r_idx]: 
                if token == " ": 
                    token = c

                if word == next_book:
                    r_idx += 1 
                    print(next_book)
                    new_encoding.append((token,b,c,d,e,r_idx))
                    book = next_book
                    if r_idx+1 < len(replaced): 
                        next_book = replaced[r_idx+1].split(" ")[0]
                    else: 
                        next_book = ""
                else: 
                    new_encoding.append((token,b,c,d,e,r_idx))
            else: 
                if token == " ": token = c
                new_encoding.append((token,b,c,d,e,-1))
                if in_citation: 
                    in_citation = False
                    r_idx += 1 
                    if r_idx < len(replaced): 
                        book = replaced[r_idx].split(" ")[0]
                        if r_idx+1 < len(replaced): 
                            next_book = replaced[r_idx+1].split(" ")[0]
                        else: 
                            next_book = ""
        
        for tuple in new_encoding: 
            print(tuple)
        print(book, citations)

        break

