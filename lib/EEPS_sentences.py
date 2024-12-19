import re
from collections import defaultdict

class Sentences(): 
    def __init__(self,tcpID): 
        self.tcpID = tcpID
        self.sentences = []
        self.section_names = {}
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
        curr_standard = [] 
        curr_in_note = False  
        non_note_tokens = 0 

        # tcpID, section, start_page, sent_idx, sentence, sentence_pos, sentence_standard
        for idx, item in enumerate(adorned): 
            
            parts = item.strip("\n").split("\t")
            if len(item) == 0: continue
            if idx in skip: # can only be in skip if we have already encountered the idx
                if parts[0] == ":": continue
                if curr_section not in self.section_names: 
                    self.section_names[curr_section] = parts[0]
                else: 
                    self.section_names[curr_section] = "_".join([self.section_names[curr_section],parts[0]]) 
                continue
            if item == "_" and (idx-1) in skip: 
                skip.append(idx+1)
                # SECTION3 : homily

            token, pos, standard, lemma, EOS = parts[0], parts[2], parts[3], parts[4], parts[5]
            standard = " REGLEMSPLIT ".join([standard,lemma]) # regularized_spelling--lemmatized_spelling
            if re.search(r"STARTNOTE",token):
                    curr_in_note = True   

            def update(t,p,s): 
                curr_sentence.append(t)
                if not re.search("STARTITALICS|NONLATINALPHABET|ENDITALICS|STARTNOTE\d+|ENDNOTE\d+",t):
                    curr_standard.append(s)
                    curr_pos.append(p)
                else:
                    curr_standard.append(t)
                    curr_pos.append(t)
            
            if re.search(r"SECTION\d+",token):
                # start of a new section in the text 
                if len(curr_sentence) > 0: 
                    # add prior segment 
                    sentences.append((curr_section, curr_page, curr_paragraph, 
                                        " ".join(curr_sentence),
                                        " ".join(curr_pos),
                                        " ".join(curr_standard)))
                    curr_sentence = []
                    curr_pos = []
                    curr_standard = []
                    non_note_tokens=0

                curr_section = token.split(":")[0].split("SECTION")[-1]
                skip = [idx+1, idx+2]
                # get accurate page number 
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
                
                # compare previously known page and next page to deduct current page number 
                if prev_known_page == next_page: 
                    curr_page = f"{page_type}{next_page}"
                elif prev_known_page is None and next_page is not None: 
                    curr_page = f"{page_type}{next_page-1}"
                elif next_page is not None and (prev_known_page + 1) != next_page: 
                    # when the extracted sections are not consecutive
                    curr_page = f"{page_type}{next_page-1}"
                else: 
                    curr_page = f"{page_type}{prev_known_page}"
            
            elif re.search(r"PAGE\d+|PAGEIMAGE\d+",token): # at a new page 
                pagenum = re.findall(r'([A-Z]+\d+)(.*?)',token)[0]
                curr_page = pagenum[0] 
                if len(pagenum[1]) > 0: 
                    # case of PAGEIMAGE23The
                    update(pagenum[1],None,pagenum[1])
                
            elif re.search(r"PARAGRAPH\d+",token):# at a new paragraph 
                combine_with_prior = False 
                if len(curr_sentence) > 0: 
                    if (re.search(r"STARTNOTE",curr_sentence[0]) and re.search(r"ENDNOTE",curr_sentence[-1])) or non_note_tokens <= 5:
                        if len(sentences) > 0: 
                            combine_with_prior = True 
                if combine_with_prior: 
                    section,page,para,c,d,e = sentences[-1]
                    sentences[-1] = (section,page,para,
                                    c+ " " + " ".join(curr_sentence),
                                    d + " " + " ".join(curr_pos),
                                    e + " " + " ".join(curr_standard))
                else:         
                    sentences.append((curr_section, curr_page, curr_paragraph, 
                                    " ".join(curr_sentence),
                                    " ".join(curr_pos),
                                    " ".join(curr_standard)))
                
                curr_sentence = []
                curr_pos = []
                curr_standard = [] 
                non_note_tokens = 0
                curr_paragraph += 1 
            else: 
                
                # update spans 
                if re.search(r"STARTNOTE",token):
                    curr_in_note = True 
                elif re.search(r"ENDNOTE",token): 
                    curr_in_note = False 
                else: non_note_tokens += 1 
                    
                # case of Israell2 Sam. 16.22 in A04389
                if re.search(r"[\w\,\.]+\d+$",token) and not re.search("NOTE",token): 
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
                    # add token 
                    update(token,pos,standard)

                
                ################
                # SEGMENTATION    
                            
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

                page, para = "",""
                prev_token = ""
                prev_token_non_punc = ""
                prev_token_idx = None 
                if len(sentences) > 0: 
                    section,page,para,c,d,e = sentences[-1]
                    prev_token = c.split(" ")[-1]
                    if re.search(r"ITALICS|\,|\.",prev_token) and len(c.split(" ")) >= 2: 
                        prev_token_non_punc = c.split(" ")[-2]
                        prev_token_idx= len(c.split(" "))-2
                    else: 
                        prev_token_non_punc = prev_token 
                        prev_token_idx =len(c.split(" "))-1   


                if re.search(r"ENDNOTE\d+",next_token): 
                    # case of a sentence boundary occuring within a note 
                    update(next_token, next_pos, next_standard)
                    adorned[idx+1] = ""
                    curr_in_note = False 
                    if nextidx < len(adorned):  
                        next_non_punc = adorned[nextidx].split("\t")
                        next_token_non_punc, next_pos_non_punc = next_non_punc[0], next_non_punc[2]
                        nextidx += 1 
                
                if re.search(r"ENDITALICS",next_token): 
                    # case of a sentence boundary occuring within an italicized section 
                    # "STARTITALICS <sentence> . ENDITALICS <next sentence>"
                    update(next_token, next_pos, next_standard)
                    adorned[idx+1] = ""
                    if nextidx < len(adorned):  
                        next_non_punc = adorned[nextidx].split("\t")
                        next_token_non_punc, next_pos_non_punc = next_non_punc[0], next_non_punc[2]
                        nextidx += 1 
                
                if curr_in_note: continue                

                # if "were all three this day" in " ".join(curr_sentence): 
                #     print(token, next_token_non_punc, curr_sentence)
                
                if re.search(r"\:|\;|\?|\\|\/",token) and not curr_in_note:
                    if len(sentences) > 0 and non_note_tokens <= 5: continue
                    if curr_in_note: continue  
                    # add as individual segment 
                    sentences.append((curr_section, curr_page, curr_paragraph, 
                                    " ".join(curr_sentence),
                                    " ".join(curr_pos),
                                    " ".join(curr_standard)))
                    curr_sentence = []
                    curr_pos = []
                    curr_standard = [] 
                    non_note_tokens = 0
                    continue   
                
                 # either add to prior segment or as its own segment            
                combine_with_prior = False 
                if re.search(r"STARTNOTE",curr_sentence[0]) and re.search(r"ENDNOTE",curr_sentence[-1]):
                    combine_with_prior = True
                if re.search(r"\,|\.",token) and not curr_in_note: 
                    if curr_in_note: continue 
                    if len(sentences) > 0 and non_note_tokens <= 5: continue
                    
                    if re.search(r"^[a-z0-9\^\*]",next_token_non_punc) or "crd" in next_pos_non_punc:
                        continue  
                    # if re.search(r"np1", pos) and re.search("fw", next_pos_non_punc) and not curr_in_note: 
                    #     # current EOS token is a proper noun and the next word is foreign 
                    #     # (in the case of Latin quotations right after a person's name) 
                    #     continue 
                    
                    if nextidx < len(adorned):  
                        next_non_punc = adorned[nextidx].split("\t")
                        next_token_non_punc, next_pos_non_punc = next_non_punc[0], next_non_punc[2]
                        nextidx += 1 
                        
                        if re.search(r"^[0-9\^\*]",next_token_non_punc) or "crd" in next_pos_non_punc:
                            continue  
                    
                    if re.search(r"\(|\)",next_token):
                        # next token is the beginning or end of a parenthetical 
                        continue
                   
                    if len(sentences) > 0 and not re.search(r"\:|\;|\?|\\|\/",prev_token): 
                        if re.search(r"STARTITALICS",curr_sentence[0]) and re.search(r"^[a-z]",curr_sentence[1]):
                            # STARTITALICS <lower case word> 
                            combine_with_prior = True
                        if re.search("ENDNOTE",prev_token_non_punc):
                            # Note in the middle of a segment 
                            if len(sentences[-1]) > 1:
                                word_before_note = ""
                                if prev_token_idx is not None: 
                                    word_idx = prev_token_idx -1 
                                    
                                    if word_idx >= 0: 
                                        word_before_note = c.split(" ")[word_idx]
                                        
                                        if word_before_note == ",": 
                                            word_idx -= 1 
                                            if word_idx >= 0: 
                                                word_before_note = c.split(" ")[word_idx]
                                
                                        if not re.search(r"\:|\;|\?|\\|\/",word_before_note): 
                                            # lowercase <NOTE> lowercase 
                                            combine_with_prior = True 
                                
                        if re.search(r"^[0-9\^]|STARTITALICS",prev_token_non_punc):
                            
                            # avoid ending the prior segment with a number (ignoring ending puncutation) or the beginning of italics 
                            # if there is another number in the first three words of this segment
                            # the boundary of the prior sentence is not a colon, semicolon, or question mark  
                            num = 0  
                            
                            if len(prev_token) > 0:         
                                for i, w in enumerate(curr_sentence):
                                    if ("crd" in curr_pos[i] or re.search(r"^[0-9\^\*]",w)):
                                        combine_with_prior = True 
                                        break
                                    if not re.search(r"STARTITALICS|ENDITALICS",w) and curr_pos[i] != w: 
                                        num += 1 
                                    if num == 3: break 
                        if re.search(r"^[0-9\^\(\)]",curr_sentence[0]) or "crd" in curr_pos[0]:
                            # avoid starting the current sentence with a number 
                            # the boundary of the prior sentence is not a colon, semicolon, or question mark  
                            if len(prev_token) > 0:         
                                combine_with_prior = True 
                    
                    if combine_with_prior:
                        
                        sentences[-1] = (section,page,para,
                                        c+ " " + " ".join(curr_sentence),
                                        d + " " + " ".join(curr_pos),
                                        e + " " + " ".join(curr_standard))
                        curr_sentence = []
                        curr_pos = []
                        curr_standard = [] 
                        non_note_tokens = 0
                        continue 
                    
                    # add as an individual segment 
                    sentences.append((curr_section, curr_page, curr_paragraph, 
                                    " ".join(curr_sentence),
                                    " ".join(curr_pos),
                                    " ".join(curr_standard)))
                    curr_sentence = []
                    curr_pos = []
                    curr_standard = [] 
                    non_note_tokens = 0
        self.sentences = sentences

