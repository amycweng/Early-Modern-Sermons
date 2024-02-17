import re,json
import sys 
sys.path.append('../')
from lib.standardization import * 
from lib.sentences import *
from lib.dictionaries.pos import fix_pos

tcpID = 'A41135'
Text = Sentences(tcpID)
all_encodings = []
all_citations = {}
for sent_idx, tuple in enumerate(Text.sentences):
    sermon_idx, start_page, sent_str, pos, lemmatized = tuple 
    sentence, pos, lemmatized = sent_str.split(" "), pos.split(" "), lemmatized.split(" ")

    encoded = []
    in_italics, in_note = False, False 
    start_italics, start_note = False, False
    ver_citation = False

     # encode with citation information 
    sent_str = re.sub(r"STARTITALICS|ENDITALICS|STARTNOTE\d+|ENDNOTE\d+","",sent_str)
    citations, outliers, sent_str, replaced = extract_citations(sent_str) # from original
    if len(citations) > 0 or len(outliers) > 0:
        all_citations[sent_idx] = (citations, outliers)
    for t, token in enumerate(sentence): 
        if token == "STARTITALICS": 
            in_italics, start_italics = True, True  
        elif token == "ENDITALICS": 
            in_italics = False 
        elif re.search(r"STARTNOTE\d+", token): 
            in_note, start_note = True, True 
        elif re.search(r"ENDNOTE\d+",token): 
            in_note = False
        else:
            if start_italics:
                it_tag, start_italics = "B-IT", False
            elif in_italics: 
                it_tag = "I-IT"
            else: 
                it_tag = "O-IT"
            if start_note:
                note_tag, start_note = "B-NOTE", False
            elif in_note: 
                note_tag = "I-NOTE"
            else: 
                note_tag = "O-NOTE"
            
            if token == "NONLATINALPHABET": 
                encoded.append((token, "foreign", lemmatized[t], it_tag, note_tag, 'O-REF'))
            elif re.search(r"^[Vv]er[.se]{0,}$",token) and t + 1 < len(sentence): 
                if pos[t+1] == "crd": 
                    encoded.append((token, pos[t], lemmatized[t], it_tag, note_tag, 'B-REF'))
                    ver_citation = True 
                else: 
                    encoded.append((token, pos[t], lemmatized[t], it_tag, note_tag, 'O-REF'))
            elif ver_citation and pos[t] == "crd":
                encoded.append((token, pos[t], lemmatized[t], it_tag, note_tag, 'I-REF'))
                ver_citation = False
            else:
                if token in fix_pos: 
                    pos[t] = fix_pos[token]
                encoded.append((token, pos[t], lemmatized[t], it_tag, note_tag, 'O-REF'))
    
    if len(citations) > 0:  
        sent = sent_str.split(" ")
        following = {}
        for i, word in enumerate(sent):
            if re.search(r"\<REF\d+\>",word): 
                ref_idx = int(re.findall(r'\d+',word)[0])
                if i+1 < len(sent): 
                    following[ref_idx] = sent[i+1]
                else: 
                    following[ref_idx] = None
        r_idx = 0

        def get_book(rep):
            rep = rep.split(" ")
            numbered_book = False 
            if re.search("1|2|3", rep[0]):
                book = rep[1]
                numbered_book = True
            else: 
                book = rep[0]
            return book, numbered_book 
        
        book, numbered_book = get_book(replaced[r_idx])
        new_encoding = []
        in_citation = False 
        if r_idx+1 < len(replaced): 
            next_book, next_numbered = get_book(replaced[r_idx+1])
        else: 
            next_book, next_numbered = "", False

        for idx, item in enumerate(encoded):
            if len(item) == 0: continue
            token,b,c,d,e = item[:-1]
            word = re.sub(r"\.", "",token)

            if word == book and idx + 1 < len(encoded):  
                next_t, next_p, next_l, d, e = encoded[idx+1][:-1]
                if next_p == next_l or next_p == "crd": 
                    if numbered_book: 
                        prev_t, prev_p, prev_l, d, e, f = new_encoding[-1]
                        new_encoding[-1] = (prev_t, prev_p, prev_l, d, e, "B-REF")
                        tag = "I-REF"
                    else: 
                        tag = "B-REF"
                    new_encoding.append((token,b,c,d,e,tag))
                    in_citation = True 
                else: 
                    new_encoding.append((token,b,c,d,e,"I-REF"))
            
            elif in_citation and word != following[r_idx]: 
                if token == " ": 
                    token = c
                    
                if len(word) > 0 and word == next_book and idx + 1 < len(encoded):
                    r_idx += 1 
                    next_t, next_p, next_l, d, e = encoded[idx+1][:-1]
                    if next_p == next_l or next_p == "crd": 
                        if next_numbered: 
                            prev_t, prev_p, prev_l, d, e, f = new_encoding[-1]
                            new_encoding[-1] = (prev_t, prev_p, prev_l, d, e, "B-REF")
                            tag = "I-REF"
                        else: 
                            tag = "B-REF"
                        new_encoding.append((token,b,c,d,e,tag))
                        in_citation = True 
                    else: 
                        new_encoding.append((token,b,c,d,e,"I-REF"))
                    
                    book, numbered_book = next_book, next_numbered
                    if r_idx+1 < len(replaced): 
                        next_book, next_numbered = get_book(replaced[r_idx+1])
                    else: 
                        next_book, next_numbered = "", False
                else: 
                    new_encoding.append((token,b,c,d,e,"I-REF"))
            else: 
                if token == " ": token = c
                new_encoding.append(item)
                if in_citation: 
                    in_citation = False
                    r_idx += 1 
                    if r_idx < len(replaced): 
                        book, numbered_book = get_book(replaced[r_idx])
                        if r_idx+1 < len(replaced): 
                            next_book, next_numbered = get_book(replaced[r_idx+1])
                        else: 
                            next_book, next_numbered = "", False
        
        for e_id, encoding in enumerate(new_encoding):
            a,b,c,d,e,f = encoding 
            all_encodings.append((sent_idx, e_id, a,b,c,d,e,f))
    else: 
        for e_id, encoding in enumerate(encoded):
            a,b,c,d,e,f = encoding 
            all_encodings.append((sent_idx, e_id, a,b,c,d,e,f))

output = (all_encodings, all_citations)
with open(f"../assets/encoded/{tcpID}.json","w+") as file: 
    json.dump(output, file)


