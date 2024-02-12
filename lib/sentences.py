import re
from collections import defaultdict

class Sentences(): 
    def __init__(self,tcpID): 
        self.tcpID = tcpID
        self.sentences = []
        self.notes_spans = defaultdict(list)# sentence idx to list of note indices
        self.segment()
        self.fix_illegible_and_get_notes()


    def segment(self): 
        with open(f"../assets/adorned/{self.tcpID}.txt","r") as file: 
            adorned = file.readlines()
        sentences = []
        curr_sermon, curr_page = 0, None
        curr_sentence = []
        curr_pos = []
        curr_lemma = []
        curr_in_note = False  

        # tcpID, sermon, start_page, sent_idx, sentence, sentence_pos, sentence_lemmas   
        for idx, item in enumerate(adorned): 
            parts = item.strip("\n").split("\t")
            if len(item) == 0: continue

            token, pos, lemma, EOS = parts[0], parts[2], parts[4], parts[5]
            

            def update(t,p,l): 
                curr_sentence.append(t)
                if not re.search("STARTITALICS|NONLATINALPHABET|ENDITALICS|STARTNOTE\d+|ENDNOTE\d+",t):
                    curr_lemma.append(l)
                    curr_pos.append(p)
                else:
                    curr_lemma.append(t)
                    curr_pos.append(t)
            
            if re.search(r"SERMON\d+",token):
                # start of a new sermon in the text 
                curr_sermon += 1 
                curr_page = None # fill in later by subtracting from the next known page 
            elif re.search(r"PAGE\d+",token): 
                curr_page = int(re.findall('\d+',token)[0]) 
            
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
                    

                update(token,pos,lemma)

                if EOS == "1":
                    if pos != token: 
                        if next_pos == "crd" or len(curr_sentence) == 1: 
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
                        elif re.search(r"crd", pos) and re.search("fw", next_pos): 
                            # current token is a number and the next word is foreign (in the case of Latin quotations right after a verse)
                            continue
                        else: 
                            if re.search(r"ENDITALICS",next_token): 
                                # case of a sentence boundary occuring within an italicized section 
                                # "STARTITALICS <sentence> . ENDITALICS <next sentence>"
                                update(next_token, next_pos, next_lemma)
                                adorned[idx+1] = ""
                            
                            if (re.search(r"^[a-z0-9]",curr_sentence[0]))and len(sentences) > 0: 
                                a,b,c,d,e = sentences[-1]
                                sentences[-1] = (a,b,
                                                c+ " " + " ".join(curr_sentence),
                                                d + " " + " ".join(curr_pos),
                                                e + " " + " ".join(curr_lemma))
                            elif len(sentences) > 0:                    
                                a,b,c,d,e = sentences[-1]
                                if "crd" in e.split(" ")[-1] or "crd" in e.split(' ')[-2]:
                                    sentences[-1] = (a,b,
                                                    c+ " " + " ".join(curr_sentence),
                                                    d + " " + " ".join(curr_pos),
                                                    e + " " + " ".join(curr_lemma))
                                else: 
                                    sentences.append((curr_sermon, curr_page,
                                                    " ".join(curr_sentence),
                                                    " ".join(curr_pos),
                                                    " ".join(curr_lemma)))
                            else: 
                                sentences.append((curr_sermon, curr_page,  
                                                " ".join(curr_sentence),
                                                " ".join(curr_pos),
                                                " ".join(curr_lemma)))
                            curr_sentence = []
                            curr_pos = []
                            curr_lemma = [] 
            # if len(sentences)>25:
            #     break
        self.sentences = sentences

    def fix_illegible_and_get_notes(self): 
        with open(f"../assets/plain/{self.tcpID}.txt","r") as file: 
            plain = file.readlines()[0].split(" ")
        illegible = []
        for word in plain: 
            illegible.extend(re.findall(r"^(\*[\w\*]+)",word))
        illegible_dict = {word:None for word in illegible}
        for s_idx, tuple in enumerate(self.sentences): 
            sentence, pos, lemma = tuple[2:]
            sentence, pos, lemma = sentence.split(" "), pos.split(" "), lemma.split(" ")
            note_start = None
            for idx, word in enumerate(sentence): 
                if re.search(r"STARTNOTE\d+",word):
                    note_start = idx
                elif re.search(r'ENDNOTE\d+',word):
                    self.notes_spans[s_idx].append((note_start,idx))
                elif idx+1 < len(sentence): 
                    if word == "*": 
                        combined = word + sentence[idx+1]
                        if combined in illegible_dict: 
                            sentence[idx] = ""
                            sentence[idx+1] = combined
                            lemma[idx+1] = combined
                            pos[idx] = ""
                            lemma[idx] = ""
            sentence = [_ for _ in sentence if len(_) > 0]
            lemma = [_ for _ in lemma if len(_) > 0]
            pos = [_ for _ in pos if len(_) > 0]
            self.sentences[s_idx] = (tuple[0], tuple[1], " ".join(sentence), " ".join(pos), " ".join(lemma))

                



