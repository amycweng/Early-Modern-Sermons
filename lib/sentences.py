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
        skip = [] # "SECTION3:homily" became "SECTION3 : homily"
        curr_section, curr_page, curr_paragraph = 0, None, 0
        curr_sentence = []
        curr_pos = []
        curr_standard = [] # choose lemmas over standard spelling
        curr_in_note = False  

        # tcpID, section, start_page, sent_idx, sentence, sentence_pos, sentence_lemmas   
        for idx, item in enumerate(adorned): 
            
            parts = item.strip("\n").split("\t")
            if len(item) == 0: continue
            if idx in skip: continue
            if item == "_" and (idx-1) in skip: 
                skip.append(idx+1)

            token, pos, standard, EOS = parts[0], parts[2], parts[3], parts[5]
            if re.search(r"^I",standard) and re.search(r"^J",parts[4]): # compare standard with lemma 
                # turn Iesus to Jesus 
                standard = "J" + standard[1:] 
            def update(t,p,l): 
                curr_sentence.append(t)
                if not re.search("STARTITALICS|NONLATINALPHABET|ENDITALICS|STARTNOTE\d+|ENDNOTE\d+",t):
                    if re.search("^[vV]er$",t): # sometimes ver gets turned into for
                        curr_standard.append(t)
                    else: 
                        curr_standard.append(l)
                    curr_pos.append(p)
                else:
                    curr_standard.append(t)
                    curr_pos.append(t)
            
            if re.search(r"SECTION\d+",token):
                # start of a new section in the text 
                if len(curr_sentence) > 0: 
                    sentences.append((curr_section, curr_page, curr_paragraph, 
                                        " ".join(curr_sentence),
                                        " ".join(curr_pos),
                                        " ".join(curr_standard)))
                    curr_sentence = []
                    curr_pos = []
                    curr_standard = []

                curr_section = token.split(":")[0].split("SECTION")[-1]
                skip = [idx+1, idx+2]

                prev_known_page = None 
                page_type = None 
                idx_to_find_page = idx
                while prev_known_page is None: 
                    if idx_to_find_page >= 0: 
                        temp = adorned[idx_to_find_page]
                        temp = temp.strip("\n").split("\t")
                        if len(temp) == 0: continue
                        if re.search(r"PAGE\d+|PAGEIMAGE\d+",temp[0]):
                            temp = re.findall(r'([A-Z]+)(\d+)',temp[0])[0]
                            page_type = temp[0]
                            prev_known_page = int(temp[1])
                        idx_to_find_page -= 1 
                    else: 
                        break
                next_page = None 
                idx_to_find_page = idx
                while next_page is None: 
                    if idx_to_find_page < len(adorned): 
                        temp = adorned[idx_to_find_page]
                        temp = temp.strip("\n").split("\t")
                        if len(temp) == 0: continue
                        if re.search(r"PAGE\d+|PAGEIMAGE\d+",temp[0]):
                            temp = re.findall(r'([A-Z]+)(\d+)',temp[0])[0]
                            page_type = temp[0]
                            next_page = int(temp[1])
                        idx_to_find_page += 1 
                    else: 
                        break
                
                if prev_known_page == next_page: 
                    curr_page = f"{page_type}{next_page}"
                elif prev_known_page is None and next_page is not None: 
                    curr_page = f"{page_type}{next_page-1}"
                elif next_page is not None and (prev_known_page + 1) != next_page: 
                    # when the extracted sections are not consecutive
                    curr_page = f"{page_type}{next_page-1}"
                else: 
                    curr_page = f"{page_type}{prev_known_page}"
            elif re.search(r"PAGE\d+|PAGEIMAGE\d+",token): 
                pagenum = re.findall(r'([A-Z]+\d+)(.*?)',token)[0]
                curr_page = pagenum[0] 
                if len(pagenum[1]) > 0: 
                    # case of PAGEIMAGE23The
                    update(pagenum[1],None,pagenum[1])
                
            elif re.search(r"PARAGRAPH\d+",token):
                # start of a new paragraph 
                curr_paragraph += 1 
            else: 
                if re.search(r"STARTNOTE\d+",token):
                    curr_in_note = True 
                elif re.search(r"ENDNOTE",token): 
                    curr_in_note = False 

                next_token, next_pos,next_standard = "","",""
                next_token_non_punc, next_pos_non_punc = "",""
                nextidx = idx+1 
                if nextidx == len(adorned): break 
                next = adorned[nextidx].split("\t")
                next_token, next_pos,next_standard = next[0], next[2], next[3]
                while next_pos_non_punc == next_token_non_punc: 
                    if nextidx == len(adorned): break 
                    next_non_punc = adorned[nextidx].split("\t")
                    next_token_non_punc, next_pos_non_punc = next_non_punc[0], next_non_punc[2]
                    nextidx += 1 
                if len(sentences) > 0: 
                    section,page,para,c,d,e = sentences[-1]
                    prev_token, prev_pos = c.split(" ")[-1],d.split(" ")[-1]
                    if prev_token == prev_pos: 
                        prev_token_non_punc = c.split(" ")[-2]
                    else: 
                        prev_token_non_punc = prev_token 
                else: 
                    page, para = "",""
                    prev_token, prev_pos = "",""
                    prev_token_non_punc = ""

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
                        update(word, "", standard)
                else: 
                    update(token,pos,standard)
                                   
                
                if len(curr_sentence) <= 5 and len(sentences) > 0: # no segments less than 5 tokens 
                    continue  
                if "crd" in next_pos_non_punc or re.search(r"[0-9]",next_token_non_punc):   
                    # do not end segment 
                    continue
                if re.search(r"STARTNOTE\d+|NONLATINALPHABET",next_token_non_punc):
                    # if the first token of the next predicted sentence is the 
                    # beginning of a note or a section of non-Latin text.
                    continue
                if re.search(r"\(|\)",next_token):
                    continue
                if re.search(r"np1", pos) and re.search("fw", next_pos_non_punc): 
                    # current EOS token is a proper noun and the next word is foreign 
                    # (in the case of Latin quotations right after a person's name) 
                    continue
                # segment
                
                if EOS == "1" or (token == pos and not re.search(r"\*|\^|\(|\)",token)):
                    if re.search(r"\,|\.",pos): 
                        if re.search(r"^[a-z0-9\^\*]",next_token_non_punc) or re.search("NOTE|ITALICS|\&",next_token_non_punc):
                            continue 

                    # either add to prior segment or as its own segment 
                    
                    if re.search(r"ENDITALICS",next_token_non_punc): 
                        # case of a sentence boundary occuring within an italicized section 
                        # "STARTITALICS <sentence> . ENDITALICS <next sentence>"
                        update(next_token, next_pos, next_standard)
                        adorned[idx+1] = ""
                    if re.search(r"ENDNOTE\d+",next_token_non_punc): 
                        # case of a sentence boundary occuring within a note 
                        update(next_token, next_pos, next_standard)
                        adorned[idx+1] = ""
                        curr_in_note = False 
                    if curr_in_note: continue
                    
                    combine_with_prior = False 
                    
                    if len(sentences) > 0: 
                        if re.search(r"STARTITALICS",curr_sentence[0]) and re.search(r"^[a-z]",next_token_non_punc):
                            # STARTITALICS <lower case word> 
                            combine_with_prior = True
                        if re.search("STARTNOTE",prev_token_non_punc) and re.search("ENDNOTE",prev_token_non_punc):
                            # avoid having a marginal note as a single segment 
                            combine_with_prior = True 
                        if re.search(r"[0-9\^]",prev_token_non_punc):
                            # avoid ending the prior segment with a number (ignoring ending puncutation)
                            # if there is another number in the first three words of this segment
                            # the boundary of the prior sentence is not a colon, semicolon, or question mark  
                            
                            num = 0  
                            if not re.search(r"\:|\;|\?",prev_token) and len(prev_token) > 0:         
                                for i, w in enumerate(curr_sentence):
                                    if ("crd" in curr_pos[i] or re.search(r"^[0-9\^\*]",w)):
                                        combine_with_prior = True 
                                        break
                                    if not re.search(r"STARTITALICS|ENDITALICS",w) and curr_pos[i] != w: 
                                        num += 1 
                                    if num == 3: break 
                        if re.search(r"[0-9\^]",curr_sentence[0]) or "crd" in curr_pos[0]:
                            # avoid starting the current sentence with a number 
                            # the boundary of the prior sentence is not a colon, semicolon, or question mark  
                            if not re.search(r"\:|\;|\?",prev_token) and len(prev_token) > 0:         
                                combine_with_prior = True 
                    
                    if combine_with_prior: 
                        if str(curr_paragraph) not in str(para).split("-"): 
                            para = f"{para}-{curr_paragraph}"
                        sentences[-1] = (section,page,para,
                                        c+ " " + " ".join(curr_sentence),
                                        d + " " + " ".join(curr_pos),
                                        e + " " + " ".join(curr_standard))
                        curr_sentence = []
                        curr_pos = []
                        curr_standard = [] 
                        continue 
                     
                    # add as an individual segment 
                    sentences.append((curr_section, curr_page, curr_paragraph, 
                                    " ".join(curr_sentence),
                                    " ".join(curr_pos),
                                    " ".join(curr_standard)))
                    curr_sentence = []
                    curr_pos = []
                    curr_standard = [] 
        self.sentences = sentences

