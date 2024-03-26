import re
from collections import defaultdict

class Sentences(): 
    def __init__(self,tcpID): 
        self.tcpID = tcpID
        self.sentences = []
        self.notes_spans = defaultdict(list)# sentence idx to list of note indices
        self.segment()

    def segment(self): 
        with open(f"../assets/adorned/{self.tcpID}.txt","r") as file: 
            adorned = file.readlines()
        sentences = []
        curr_sermon, curr_page, curr_paragraph = 0, None, 0
        curr_sentence = []
        curr_pos = []
        curr_lemma = []
        curr_in_note = False  

        # tcpID, sermon, start_page, sent_idx, sentence, sentence_pos, sentence_lemmas   
        for idx, item in enumerate(adorned): 
            
            parts = item.strip("\n").split("\t")
            if len(item) == 0: continue

            token, pos, lemma, EOS = parts[0], parts[2], parts[4], parts[5]
            if "^" in token: lemma = token

            def update(t,p,l): 
                curr_sentence.append(t)
                if not re.search("STARTITALICS|NONLATINALPHABET|ENDITALICS|STARTNOTE\d+|ENDNOTE\d+",t):
                    if re.search("^[vV]er$",t): # sometimes ver gets turned into for
                        curr_lemma.append(t)
                    else: 
                        curr_lemma.append(l)
                    curr_pos.append(p)
                else:
                    curr_lemma.append(t)
                    curr_pos.append(t)
            
            if re.search(r"SERMON\d+",token):
                # start of a new sermon in the text 
                curr_sermon += 1 
                curr_page = None # fill in later by subtracting from the next known page 
            elif re.search(r"PAGE\d+|PAGEIMAGE\d+",token): 
                curr_page = token 
            elif re.search(r"PARAGRAPH\d+",token):
                curr_paragraph += 1 
                if len(curr_sentence) > 0: 
                    sentences.append((curr_sermon, curr_page, curr_paragraph, 
                                        " ".join(curr_sentence),
                                        " ".join(curr_pos),
                                        " ".join(curr_lemma)))
                    curr_sentence = []
                    curr_pos = []
                    curr_lemma = []
            else: 
                
                
                if re.search(r"STARTNOTE\d+",token): 
                    # beginning of a note
                    curr_in_note = True 
                elif re.search(r"ENDNOTE\d+",token): 
                    # end of a note 
                    curr_in_note = False

                if idx < len(adorned) -1: 
                    next = adorned[idx+1].split("\t")
                    next_token, next_pos, next_lemma = next[0], next[2], next[4]
                else: 
                    next_token, next_pos, next_lemma = "","",""
                    
                # case of Israell2 Sam. 16.22 in A04389
                if re.search(r"[\w\,\.]+\d+$",token) and not re.search("STARTITALICS|NONLATINALPHABET|ENDITALICS|STARTNOTE\d+|ENDNOTE\d+",token): 
                    num = re.findall(r"\d+$",token)[0]
                    token = token.split(num)[0]
                    update(token,pos,token)
                    update(num,"crd",num)
                    continue
                elif re.search(r"[A-Z]",token[1:]) and re.search(r"[a-z]",token[1:]): 
                    # capital in the middle of a word, .e.,g fireMat 3.10 in A04389
                    words = [token[0]]
                    for char in token[1:]:
                        if char.isupper():
                            words.append(' ')
                        words.append(char)
                    words = ''.join(words)
                    words = words.split(" ")
                    for word in words: 
                        update(word, "", lemma)
                else: 
                    update(token,pos,lemma)

                if EOS == "1":
                    if pos == "crd" and len(curr_sentence) == 1 and len(sentences) > 0: 
                        serm,page,para,c,d,e = sentences[-1]
                        if curr_paragraph == para: 
                            sentences[-1] = (serm,page,para,
                                            c+ " " + " ".join(curr_sentence),
                                            d + " " + " ".join(curr_pos),
                                            e + " " + " ".join(curr_lemma))
                            curr_sentence = []
                            curr_pos = []
                            curr_lemma = [] 
                            continue
                    
                    if pos != token: 
                        if next_pos == "crd" or len(curr_sentence) == 1 or len(token.strip("."))==1: 
                            continue

                    if re.search(r"ENDNOTE\d+",next_token): 
                        # case of a sentence boundary occuring within a note  
                        # do not end sentence 
                        update(next_token, next_pos, next_lemma)
                        curr_in_note = False
                        adorned[idx+1] = ""
                    
                    elif not curr_in_note: 
                        if re.search(r"STARTNOTE\d+|NONLATINALPHABET",next_token):
                            # if the first token of the next predicted sentence is the beginning of a note or a section of non-Latin text.  
                            continue
                        elif re.search(r"np1", pos) and re.search("fw", next_pos): 
                            # current EOS token is a proper noun and the next word is foreign 
                            # (in the case of Latin quotations right after a person's name) 
                            continue
                        elif re.search(r"etc",lemma): 
                            # case of "By faith Noah warned of God moved with fear, STARTITALICS &c. ENDITALICS H*b. 11. 7."
                            continue 
                        else: 
                            if re.search(r"ENDITALICS",next_token): 
                                # case of a sentence boundary occuring within an italicized section 
                                # "STARTITALICS <sentence> . ENDITALICS <next sentence>"
                                update(next_token, next_pos, next_lemma)
                                adorned[idx+1] = ""
                            
                            if (re.search(r"^[a-z0-9\^\.]",curr_sentence[0]))and len(sentences) > 0: 
                                serm,page,para,c,d,e = sentences[-1]
                                if curr_paragraph == para: 
                                    sentences[-1] = (serm,page,para,
                                                    c+ " " + " ".join(curr_sentence),
                                                    d + " " + " ".join(curr_pos),
                                                    e + " " + " ".join(curr_lemma))
                                else: 
                                    sentences.append((curr_sermon, curr_page, curr_paragraph, 
                                                    " ".join(curr_sentence),
                                                    " ".join(curr_pos),
                                                    " ".join(curr_lemma)))
                            
                            elif len(sentences) > 0:                    
                                serm,page,para,c,d,e = sentences[-1]
                                end_with_crd, end_with_it, end_with_single = False, False, False
                                if len(d.split(" ")) >= 2: 
                                    if re.search(r"crd|\^[\.]*",d.split(" ")[-1]) or re.search(r"crd|\^[\.]*",d.split(" ")[-2]):
                                        end_with_crd = True
                                    if len(c.split(" ")[-2].strip(".")) == 1: 
                                        end_with_single = True
                                if len(c.split(" ")) > 1: 
                                    if re.search(r"ENDITALICS",c.split(" ")[-1]): 
                                        end_with_it = True
                                if curr_paragraph == para and (end_with_crd or end_with_it or end_with_single):
                                    sentences[-1] = (serm,page,para,
                                                    c+ " " + " ".join(curr_sentence),
                                                    d + " " + " ".join(curr_pos),
                                                    e + " " + " ".join(curr_lemma))
                                else: 
                                    sentences.append((curr_sermon, curr_page, curr_paragraph, 
                                                    " ".join(curr_sentence),
                                                    " ".join(curr_pos),
                                                    " ".join(curr_lemma)))
                            else: 
                                sentences.append((curr_sermon, curr_page, curr_paragraph, 
                                                " ".join(curr_sentence),
                                                " ".join(curr_pos),
                                                " ".join(curr_lemma)))
                            curr_sentence = []
                            curr_pos = []
                            curr_lemma = [] 
        self.sentences = sentences

