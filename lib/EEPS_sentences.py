import re
from collections import defaultdict
from EEPS_helper import * 

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
        
        curr_section, curr_page, curr_paragraph = None, None, 0 # paragraph is a global index (continuous over sections/DIVs)
        curr_sentence = []
        curr_pos = [] # part of speech 
        curr_standard = [] # standardized terms 
        curr_in_note = False  
        non_note_tokens = 0 
        last_non_note_token = None 

        # tcpID, section, start_page, sent_idx, sentence, sentence_pos, sentence_standard
        for idx, item in enumerate(adorned):             
            parts = item.strip("\n").split("\t")
            if len(item) == 0: continue

            token, pos, standard, _, EOS = parts[0], parts[2], parts[3], parts[4], parts[5]
            if re.search(r"STARTNOTE",token):
                    curr_in_note = True   


            def update(t,p,s): # token, pos, standard 
                curr_sentence.append(t)
                if not re.search("STARTITALICS|NONLATINALPHABET|ENDITALICS|STARTNOTE\d+|ENDNOTE\d+",t):
                    curr_standard.append(s)
                    curr_pos.append(p)
                else:
                    curr_standard.append(t)
                    curr_pos.append(t)
            
            def add_segment():
                sentences.append((curr_section, curr_page, curr_paragraph, 
                                        " ".join(curr_sentence),
                                        " ".join(curr_pos),
                                        " ".join(curr_standard)))
                # reset variables 
                curr_sentence = []
                curr_pos = []
                curr_standard = []
                non_note_tokens=0
                last_non_note_token=None

            if re.search(r"DIV\d+\^",token): 
                # start of a new section in the text (DIV1-7)
                if len(curr_sentence) > 0: 
                    # conclude the prior segment 
                    add_segment()
                
                curr_section = token
                
                # get accurate page number 
                curr_page = find_curr_page(idx,adorned)
            
            elif re.search(r"\bPAGE[\d+\w+]",token): # at a new page 
                curr_page_type,curr_page,currisRoman = get_page_number(token)
                curr_page = f"{curr_page_type}{curr_page}{currisRoman}"
                

            elif re.search(r"PARAGRAPH\d+",token):# at a new paragraph 
                # combine_with_prior = False 
                # if len(curr_sentence) > 0: 
                #     if (re.search(r"STARTNOTE",curr_sentence[0]) and re.search(r"ENDNOTE",curr_sentence[-1])) or non_note_tokens <= 6:
                #         if len(sentences) > 0: 
                #             combine_with_prior = True 
                # if combine_with_prior: 
                #     section,page,para,c,d,e = sentences[-1]
                #     sentences[-1] = (section,page,para,
                #                     c+ " " + " ".join(curr_sentence),
                #                     d + " " + " ".join(curr_pos),
                #                     e + " " + " ".join(curr_standard))
                # else:         
                add_segment()
                curr_paragraph += 1 
            else: 
                
                # update spans 
                if re.search(r"STARTNOTE",token):
                    curr_in_note = True 
                elif re.search(r"ENDNOTE",token): 
                    curr_in_note = False 
                else: 
                    non_note_tokens += 1 
                    last_non_note_token = token 
                    
                update(token,pos,standard)

                ################
                # SEGMENTATION    


                # find next and previous tokens         
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
                    # case of a sentence boundary occuring within an italicized span  
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
                def add_segment(): 
                    sentences.append((curr_section, curr_page, curr_paragraph, 
                                    " ".join(curr_sentence),
                                    " ".join(curr_pos),
                                    " ".join(curr_standard)))
                    curr_sentence = []
                    curr_pos = []
                    curr_standard = [] 
                    non_note_tokens = 0


                 # either add to prior segment or as its own segment            
                combine_with_prior = False 

                if (re.search(r"\:|\;|\.|\?|\\|\/",token) or EOS == "1") and not curr_in_note: 
                    if len(sentences) > 0 and non_note_tokens <= 10: 
                        # IF current segment is short 
                        # AND prior segment is shorter than 30 words
                        # AND ( (prior segment ends with : or ;)  
                        #    OR (prior segment ends with a lower case word or comma) )
                        # THEN append current to prior 
                        # ELSE allow current to grow larger 
                        if True: 
                            break
                        else: 
                            continue
                    add_segment()  

                
                # if re.search(r"STARTNOTE",curr_sentence[0]) and re.search(r"ENDNOTE",curr_sentence[-1]):
                #     combine_with_prior = True
                    
                # if re.search(r"\,|\.",token) and not curr_in_note: 
                #     if curr_in_note: continue 
                #     if len(sentences) > 0 and non_note_tokens <= 6: continue
                    
                #     if re.search(r"^[a-z0-9\^\*]",next_token_non_punc) or "crd" in next_pos_non_punc:
                #         continue  
                #     if re.search(r"np1", pos) and re.search("fw", next_pos_non_punc) and not curr_in_note: 
                #         # current EOS token is a proper noun and the next word is foreign 
                #         # (in the case of Latin quotations right after a person's name) 
                #         continue 
                    
                #     if nextidx < len(adorned):  
                #         next_non_punc = adorned[nextidx].split("\t")
                #         next_token_non_punc, next_pos_non_punc = next_non_punc[0], next_non_punc[2]
                #         nextidx += 1 
                        
                #         if re.search(r"^[0-9\^\*]",next_token_non_punc) or "crd" in next_pos_non_punc:
                #             continue  
                    
                #     if re.search(r"\(|\)",next_token):
                #         # next token is the beginning or end of a parenthetical 
                #         continue
                   
                #     if len(sentences) > 0 and not re.search(r"\:|\;|\?|\\|\/",prev_token): 
                #         if re.search(r"STARTITALICS",curr_sentence[0]) and re.search(r"^[a-z]",curr_sentence[1]):
                #             # STARTITALICS <lower case word> 
                #             combine_with_prior = True
                #         if re.search("ENDNOTE",prev_token_non_punc):
                #             # Note in the middle of a segment 
                #             if len(sentences[-1]) > 1:
                #                 word_before_note = ""
                #                 if prev_token_idx is not None: 
                #                     word_idx = prev_token_idx -1 
                                    
                #                     if word_idx >= 0: 
                #                         word_before_note = c.split(" ")[word_idx]
                                        
                #                         if word_before_note == ",": 
                #                             word_idx -= 1 
                #                             if word_idx >= 0: 
                #                                 word_before_note = c.split(" ")[word_idx]
                                
                #                         if not re.search(r"\:|\;|\?|\\|\/",word_before_note): 
                #                             # lowercase <NOTE> lowercase 
                #                             combine_with_prior = True 
                                
                #         if re.search(r"^[0-9\^]|STARTITALICS",prev_token_non_punc):
                            
                #             # avoid ending the prior segment with a number (ignoring ending puncutation) or the beginning of italics 
                #             # if there is another number in the first three words of this segment
                #             # the boundary of the prior sentence is not a colon, semicolon, or question mark  
                #             num = 0  
                            
                #             if len(prev_token) > 0:         
                #                 for i, w in enumerate(curr_sentence):
                #                     if ("crd" in curr_pos[i] or re.search(r"^[0-9\^\*]",w)):
                #                         combine_with_prior = True 
                #                         break
                #                     if not re.search(r"STARTITALICS|ENDITALICS",w) and curr_pos[i] != w: 
                #                         num += 1 
                #                     if num == 3: break 
                #         if re.search(r"^[0-9\^\(\)]",curr_sentence[0]) or "crd" in curr_pos[0]:
                #             # avoid starting the current sentence with a number 
                #             # the boundary of the prior sentence is not a colon, semicolon, or question mark  
                #             if len(prev_token) > 0:         
                #                 combine_with_prior = True 
                    
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
