import re,json
from re import finditer
import sys 
sys.path.append('../')
from lib.standardization import * 
from lib.sentences import *
from lib.dictionaries.pos import fix_pos
import pandas as pd 

sermons_metadata = pd.read_csv("../assets/sermons.csv")
sermons = sorted(sermons_metadata["id"])

def get_ids(group): 
    return [tcpID for tcpID in sermons if group in tcpID]

def encode(tcpID): 
    Text = Sentences(tcpID)
    all_encodings = {}
    all_citations = {}
    all_sentences = {}
    for sent_idx, tuple in enumerate(Text.sentences):
        if sent_idx != 48: continue
        # print(sent_idx)
        all_encodings[sent_idx] = []
        sermon_idx, start_page, paragraph, s, p, l = tuple 
        all_sentences[sent_idx] = (sermon_idx, start_page, paragraph)

        sentence, pos, lemmatized = [], [] ,[]
        s, p, l = s.split(" "), p.split(" "),l.split(" ")
        for t, token in enumerate(s): 
            if token != ".": 
                sentence.append(s[t])
                pos.append(p[t])
                lemmatized.append(l[t])
            elif t-1 >= 0: 
                sentence[-1] = sentence[-1] + "."
                pos[-1] = pos[-1] + "<EOS>" # indicates that the period at end of the word is a sentence boundary and its own token
                lemmatized[-1] = lemmatized[-1] + "."

        encoded = []
        in_italics, in_note = False, False 
        start_italics, start_note = False, False
        ver_citation = False

         # encode with citation information 
        sent_str = re.sub(r"STARTITALICS|ENDITALICS|STARTNOTE\d+|ENDNOTE\d+",""," ".join(sentence))
        sent_str = re.sub(r"\s+"," ",sent_str)
        citations, outliers, replaced_str, replaced = extract_citations(sent_str) # from original
        
        t = -1  
        for token in sentence: 
            if token == ".": continue 
            
            t += 1 
            
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
                
                if re.search(r"^[Vv]er[.se]*$|^[Vv][.]*$",token) and t + 1 < len(sentence):
                    if pos[t+1] == "crd": 
                        encoded.append((token, pos[t], lemmatized[t], it_tag, note_tag, 'B-REF-VERSE'))
                        ver_citation = True
                        continue  
                    elif t+2 < len(sentence) and sentence[t+1] == "ENDITALICS":
                        if pos[t+2] == "crd": 
                            encoded.append((token, pos[t], lemmatized[t], it_tag, note_tag, 'B-REF-VERSE'))
                            ver_citation = True
                            continue 
                    encoded.append((token, pos[t], lemmatized[t], it_tag, note_tag, 'O-REF'))
                elif ver_citation and (pos[t] == "crd" or pos[t] == token):
                    encoded.append((token, pos[t], lemmatized[t], it_tag, note_tag, 'I-REF-VERSE'))
                else:
                    ver_citation = False
                    if token in fix_pos: 
                        pos[t] = fix_pos[token]
                    encoded.append((token, pos[t], lemmatized[t], it_tag, note_tag, 'O-REF'))

        if len(citations) > 0:  
            sent = replaced_str.split(" ")
            following = {}
            books = {}
            # print(sent_str)
            # print(sent_idx,citations,outliers)
            def get_book(r,c=None): 
                elt = replaced[r].split(" ")
                if re.search(r"\d|\^",elt[0]): 
                    book = elt[1]
                    numbered_book = True 
                else: 
                    book = elt[0]
                    if c is not None: 
                        if re.search(r"\d|\^",c[0]): 
                            numbered_book = True
                        else: 
                            numbered_book = False
                    else: 
                        numbered_book = False
                return book, numbered_book
            
            for i, word in enumerate(sent):
                if re.search(r"\<REF\d+\>",word): 
                    ref_idx = int(re.findall(r'\d+',word)[0])
                    if i+1 < len(sent): 
                        next_elt = sent[i+1]
                        if re.search(r"\<REF\d+\>",next_elt): 
                            next_elt = replaced[ref_idx+1].split(" ")[0]
                        following[ref_idx] = next_elt
                        citation = citations[ref_idx][0]
                        books[ref_idx] = get_book(ref_idx,citation)
                    else: 
                        books[ref_idx] = get_book(ref_idx)
                        following[ref_idx] = None
            
            print(books,following,sent_str)
            print(len(sent_str.split(" ")))
            print(len(encoded))
            start = 0
            index_encodings = {}
            for e, encoding in enumerate(encoded): 
                end = start + len(encoding[0].strip(" ")) -1 
                index_encodings[(start,end)] = list(encoding)
                start = 1 + end + 1 # add one for space 
            citation_spans = []
            for b, book in books.items():
                book = book[0]
                for phrase in finditer(rf"({book})(.*?)({following[b]})", sent_str):
                    span = list(phrase.span())
                    print(span,[phrase.group()])
                    phrase =  phrase.group().split(" ")
                    citation_spans.append(span)
            
            b = 0
            in_citation = False 
            prev_span = None 
            for e_span, encoding in index_encodings.items(): 
                if e_span[0] == citation_spans[b][0]: 
                    # start of a citation 
                    index_encodings[e_span][-1] = "B-REF"
                    in_citation = True
                    if books[b][1] == True: 
                        # is a numbered book
                        index_encodings[prev_span][-1] = "B-REF"
                        index_encodings[e_span][-1] = "I-REF" 
                    else: 
                        index_encodings[e_span][-1] = "B-REF"
                elif e_span[1] == citation_spans[b][1]:
                    # end of a citation
                    # check if it is the beginning of another 
                    print(encoding)
                    b += 1 
                    if e_span[0] ==  citation_spans[b][0]: 
                        # start of a citation 
                        index_encodings[e_span][-1] = "B-REF"
                        in_citation = True
                        if books[b][1] == True: 
                            # is a numbered book
                            index_encodings[prev_span][-1] = "B-REF"
                            index_encodings[e_span][-1] = "I-REF" 
                        else: 
                            index_encodings[e_span][-1] = "B-REF"
                    else: 
                        in_citation = False
                elif in_citation: 
                    index_encodings[e_span][-1] = "I-REF"
                prev_span = e_span 
            print(index_encodings)
            # print(sent_idx,following,citations,replaced,sent_str)
        #     new_encoding = []
        #     in_citation = False 
        #     book, numbered_book = books[r_idx]
        #     if r_idx+1 < len(replaced): 
        #         next_book, next_numbered = books[r_idx+1]
        #     else: 
        #         next_book, next_numbered = "", False

        #     for idx, item in enumerate(encoded):
        #         if len(item) == 0: continue
        #         token,b,c,d,e = item[:-1]
        #         word = re.sub(r"\.", "",token)
        #         print(word,book,r_idx)
        #         if book == None: 
        #             if token == " ": token = c
        #             new_encoding.append(item)

        #         if word == book and idx + 1 < len(encoded):  
        #             print(word,book,r_idx)
        #             next_t, next_p, next_l, d, e = encoded[idx+1][:-1]
        #             if re.search(r'^[0-9\*\^\.]+$',convert_numeral(next_t)) or re.search(r"\b[cC]\b|\b[lL]\b|\b[vV]\b|\b[vV]erse\b|\b[vV]ers\b|\b[vV]er\b|\b[cC]ap\b|\b[Cc]hap\b|\b[cC]hapter\b",next_t): 
        #                 print(word,book,r_idx)
        #                 if idx + 2 < len(encoded): 
        #                     # case of 1 Cor. 1 Cor. 6.9 6.9 
        #                     t2 = encoded[idx+2][:-1][0]
        #                     clean_t2 = clean_word(t2)
        #                     if clean_t2 in abbrev_to_book: 
        #                         clean_t2 = abbrev_to_book[clean_t2]
        #                         element = ""
        #                         if next_t == "^":
        #                             element = f"unknown{clean_t2}"
        #                         elif f"{next_t} {clean_t2}" in numBook: 
        #                             element = f"{next_t} {clean_t2}"
                                
        #                         if element in numBook: 
        #                             new_encoding.append(item)
        #                             continue
                        
        #                 print("here",numbered_book)
        #                 if len(new_encoding) > 0: 
        #                     prev_t, prev_p, prev_l, d, e, f = new_encoding[-1]

        #                     if numbered_book: 
        #                         if prev_t == "of" and len(new_encoding) > 1: 
        #                             first_t, first_p, first_l, dd, ee,ff = new_encoding[-2]
        #                             new_encoding[-2] = (first_t, first_p, first_l, dd,ee,"B-REF")
        #                             new_encoding[-1] = (prev_t, prev_p, prev_l, d, e, "I-REF")
        #                         else: 
        #                             new_encoding[-1] = (prev_t, prev_p, prev_l, d, e, "B-REF")
        #                         tag = "I-REF"
                            
        #                     elif re.search(r'^[0-9\*\^]+$', convert_numeral(prev_t)): 
        #                         if len(new_encoding) > 1:
        #                             first_t, first_p, first_l, dd, ee,ff = new_encoding[-2]
        #                             if re.search(r"^[Vv]er[.se]*$|^[Vv][.]*$",first_t):
        #                                 if len(citations[r_idx]) == 1:
        #                                     c = citations[r_idx][0].split(" ") 
        #                                     nums = c[-1].split(".")
        #                                     versenum = re.sub(r"[^0-9\^\*]+","",prev_t)
        #                                     if len(c[0]) == 1 and len(nums) == 1:
        #                                         citations[r_idx] = [f"{c[0]} {c[1]} {nums[0]}.{versenum}"]
        #                                     else: 
        #                                         citations[r_idx] = [f"{c[0]} {nums[0]}.{versenum}"]
        #                                     tag = "I-REF"
        #                                 else: 
        #                                     tag = "B-REF"
        #                             elif convert_numeral(prev_t) in citations[r_idx][0].split(" "): 
        #                                 tag = "I-REF"
        #                             else: 
        #                                 tag = "B-REF"
                                    
        #                         elif convert_numeral(prev_t) in citations[r_idx][0]: 
        #                             new_encoding[-1] = (prev_t, prev_p, prev_l, d, e, "B-REF")
        #                             tag = "I-REF"
        #                         else: 
        #                             tag = "B-REF"
        #                     else: 
        #                         tag = "B-REF"
                            
        #                     if f in ["B-REF","I-REF"] and not numbered_book:
        #                         print("there",tag,word)
        #                         r_idx += 1
        #                 else: 
        #                     tag = "B-REF"
        #                 print("there",tag,word)
        #                 new_encoding.append((token,b,c,d,e,tag))
        #                 in_citation = True
        #                 print(new_encoding)
                    
        #             elif idx+2 < len(encoded): 
        #                 print("here?")
        #                 next_next_t = encoded[idx+1][0]
        #                 if next_t == "of" and re.search(r"\bSol\b|\bSolomon\b",next_next_t):
        #                     new_encoding.append((token,b,c,d,e,"B-REF"))
        #                     in_citation = True
        #                 else: 
        #                     new_encoding.append((token,b,c,d,e,"O-REF"))
        #             else: 
        #                 print("here")
        #                 new_encoding.append((token,b,c,d,e,"O-REF"))
                
        #         elif in_citation and word != following[r_idx]: 
        #             # print("here",word,following[r_idx],next_book,r_idx)
        #             if token == " ": 
        #                 token = c
        #             if len(word) > 0 and word == next_book and idx + 1 < len(encoded):
        #                 r_idx += 1 
        #                 next_t, next_p, next_l, d, e = encoded[idx+1][:-1]
        #                 if next_p == next_l or re.search(r'^[0-9\*\^\.]+$',convert_numeral(next_t)): 
        #                     if next_numbered: 
        #                         prev_t, prev_p, prev_l, d, e, f = new_encoding[-1]
        #                         new_encoding[-1] = (prev_t, prev_p, prev_l, d, e, "B-REF")
        #                         tag = "I-REF"
        #                     else: 
        #                         tag = "B-REF"
        #                     new_encoding.append((token,b,c,d,e,tag))
        #                     in_citation = True 
        #                     r_idx += 1 
        #                 else: 
        #                     new_encoding.append((token,b,c,d,e,"I-REF"))
                        
        #                 book, numbered_book = next_book, next_numbered
        #                 if r_idx+1 < len(replaced): 
        #                     next_book, next_numbered = books[r_idx+1]
        #                 else: 
        #                     next_book, next_numbered = "", False
        #                     in_citation = False
        #             else: 
        #                 new_encoding.append((token,b,c,d,e,"I-REF"))
        #         else: 
        #             if token == " ": token = c
        #             new_encoding.append(item)
        #             if in_citation: 
        #                 in_citation = False
        #                 r_idx += 1 
        #                 if r_idx < len(replaced): 
        #                     book, numbered_book = books[r_idx]
        #                     if r_idx+1 < len(replaced): 
        #                         next_book, next_numbered = books[r_idx+1]
        #                     else: 
        #                         next_book, next_numbered = "", False
        #                 else: 
        #                     book, numbered_book = None,False
        #                     next_book, next_numbered = None, False
            
        #     for e_id, encoding in enumerate(new_encoding):
        #         a,b,c,d,e,f = encoding 
        #         all_encodings[sent_idx].append((e_id, a,b,c,d,e,f))
        # else: 
        #     for e_id, encoding in enumerate(encoded):
        #         a,b,c,d,e,f = encoding 
        #         all_encodings[sent_idx].append((e_id, a,b,c,d,e,f))
        
    #     if len(citations) > 0 or len(outliers) > 0:
    #         all_citations[sent_idx] = (citations, outliers)

    # output = (all_encodings, all_citations, all_sentences)
    # with open(f"../assets/encoded/{tcpID}.json","w+") as file: 
    #     json.dump(output, file)

if __name__ == "__main__": 
    sermon_group = input("Enter the beginning characters of a tcpID category: ")
    tcpIDs = get_ids(sermon_group)
    for tcpID in tcpIDs: 
        print(tcpID)
        encode(tcpID)

# print(extract_citations("5 psalms 115"))