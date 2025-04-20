import re
from collections import defaultdict
from EEPS_helper import * 

class Segments(): 
    def __init__(self,tcpID): 
        self.tcpID = tcpID
        self.segments = []
        self.curr_section = "None^0" 
        self.curr_page = None 
        self.curr_page_type = None 
        self.curr_paragraph = 0 # paragraph is a global index (continuous over sections/DIVs)
        self.curr_segment = []
        self.curr_pos = [] # part of speech 
        self.curr_standard = [] # standardized terms 
        self.curr_in_note = False  
        self.curr_length = 0 # the length of the current segment excluding note spans & italic markers 
        self.curr_last_token = '' 
        self.prior_length = 0 # the length of the prior segment excluding note spans & italic markers 
        self.prior_last_token = '' # last non-note token in the prior segment

        self.segment()

    def reset(self): 
        self.curr_segment = []
        self.curr_pos = [] 
        self.curr_standard = [] 
        self.curr_in_note = False  
        self.curr_length = 0 
        self.curr_last_token = None 


    def update(self, t,p,s): # token, pos, standard 
        self.curr_segment.append(t)
        if not re.search("STARTITALICS|NONLATINALPHABET|ENDITALICS|STARTNOTE|ENDNOTE",t):
            self.curr_standard.append(s)
            self.curr_pos.append(p)
        else:
            self.curr_standard.append(t)
            self.curr_pos.append(t)
    
    def combine_with_prior_segment(self):
        if self.curr_length > 0: 
            section,page,para,c,d,e = self.segments[-1]
            self.segments[-1] = (section,page,para,
                            c+ " " + " ".join(self.curr_segment),
                            d + " " + " ".join(self.curr_pos),
                            e + " " + " ".join(self.curr_standard))
            self.prior_length += self.curr_length 
            self.prior_last_token = self.curr_last_token 
            self.reset()

    def add_segment(self):
        if len(self.segments) > 0: 
            # merge overly short segments with prior segments of the SAME DIV
            prior_paragraph = self.segments[-1][2]
            if self.curr_length <= 5 and (self.curr_paragraph == prior_paragraph) and self.prior_length <= 60: 
                self.combine_with_prior_segment()
                return  
        if self.curr_length > 0:  
            self.segments.append((self.curr_section, self.curr_page, self.curr_paragraph, 
                                    " ".join(self.curr_segment),
                                    " ".join(self.curr_pos),
                                    " ".join(self.curr_standard)))
            self.prior_length = self.curr_length 
            self.prior_last_token = self.curr_last_token 
            self.reset()

    
    def update_section(self,token):
        section_idx = int(self.curr_section.split("^")[-1]) + 1
        self.curr_section = token + f"^{section_idx}"
        
    def segment(self,text=None): 
        with open(f"{adorned_folder}/{self.tcpID}.txt","r") as file: 
            adorned = file.readlines()

        # tcpID, section, start_page, sent_idx, segment, segment_pos, segment_standard
        for idx, item in enumerate(adorned):             
            parts = item.strip("\n").split("\t")
            if len(item) == 0: continue

            token, pos, standard, _, EOS = parts[0], parts[2], parts[3], parts[4], parts[5] 
            
            ############ 
            # NEW SECTION IN THE TEXT (DIV1-7)
            ############
            if re.search(r"DIV\d+\^",token): 
                if len(self.curr_segment) > 0: 
                    # conclude the prior segment 
                    self.add_segment()
                
                nextidx = idx+1 
                previdx = idx-1
                next_token = ""
                prev_token = ""  
                if nextidx < len(adorned):   
                    next_token = adorned[nextidx].split("\t")
                    next_token = next_token[0]
                if previdx >= 0: 
                    prev_token = adorned[previdx].split("\t")
                    prev_token = prev_token[0]

                if re.search(r"DIV\d+\^",next_token): # not the beginning of an extracted section
                    # reset page because there is a gap 
                    self.curr_page = None
                    continue # skip this section 
                else:
                    self.update_section(token) 
                    if self.curr_page is None:
                        # get accurate page number 
                        self.curr_page = find_curr_page(idx,adorned,self.curr_page,None)
                       
                        if self.curr_page_type is None: 
                            if "IMAGE" in self.curr_page: 
                                self.curr_page_type = "PAGEIMAGE"
                            else: 
                                self.curr_page_type = "PAGE"

                    elif not re.search(r"DIV\d+\^",prev_token): # direct continuation of previous DIV
                        self.update_section(token)
                        continue # do not change page info 

            ############ 
            # MISSING PAGE 
            ############  
            elif "PAGE" in token and "MISSING" in token: 
                self.update(token,token,token)
                self.curr_paragraph += 1  
                if len(self.curr_segment) > 0: 
                    # conclude the prior segment 
                    self.add_segment()
                self.prior_length = float("inf") 
                self.prior_last_token = ''
                continue 
            ############ 
            # NEW PAGE 
            ############            
            elif is_page(token) or is_page_image(token): 
                curr_page = str(self.curr_page)  
                if "IMAGE" in curr_page and "IMAGE" not in token: 
                    continue # only look at pages 
                elif "IMAGE" not in curr_page and "IMAGE" in token: 
                    continue # only look at page images 
                else: 
                    curr_page_type,curr_page,currisRoman = get_page_number(token)
                    self.curr_page = f"{curr_page_type}{curr_page}{currisRoman}"
            
            else:
                ############ 
                # NEW PARAGRAPH OR MARGINALIUM OR 
                # ADD TOKEN TO SEGMENT 
                ############
        
                if re.search(r"STARTNOTE",token):
                    self.curr_in_note = True 
                    self.update(token,token,token)
                elif re.search(r"ENDNOTE",token): 
                    self.curr_in_note = False 
                    self.update(token,token,token)
                elif token in ['STARTITALICS', 'NONLATINALPHABET', 'ENDITALICS'] and not self.curr_in_note:
                    self.update(token,token,token)
                elif not re.search(r"PARAGRAPH\d+",token):  
                    self.update(token,pos,standard)
                    if not self.curr_in_note and not re.match(r"\:|\;|\?|\\|\/|\!|\,|\.",standard):
                        self.curr_last_token = token 
                        self.curr_length += 1 
                else: # NEW PARAGRAPH 
                    ############ 
                    # DO NOT END SEGMENT WITHIN A MARGINALIUM OR ITALICIZED SPAN 
                    # DO NOT ADD SINGLE ITEM SEGMENTS 
                    ############
                    if self.curr_in_note: continue                
                    if self.curr_length == 1: continue 
                    self.add_segment()
                    self.curr_paragraph += 1 
                    continue 

                ############ 
                # DO NOT END SEGMENT WITHIN A MARGINALIUM OR ITALICIZED SPAN 
                # DO NOT ADD SINGLE ITEM SEGMENTS 
                ############
                if self.curr_in_note: continue                
                if self.curr_length == 1: # ensures that the final segment is added in case there is not an EOS marker 
                    if idx == (len(adorned)-1): 
                        self.add_segment()
                    continue

                ############ 
                # FIND NEXT TOKEN 
                ############        
                next_token, next_pos,next_standard = "","",""
                nextidx = idx+1 
                if nextidx < len(adorned): 
                    next = adorned[nextidx].split("\t")
                    next_token, next_pos,next_standard = next[0], next[2], next[3]

                ############ 
                # SEGMENT BOUNDARY IS WITHIN MARGINALIUM  
                ############
                if re.search(r"ENDNOTE\d+",next_token): 
                    self.update(next_token, next_pos, next_standard)
                    adorned[nextidx] = ""
                    self.curr_in_note = False 
                    nextidx += 1 
                    if nextidx < len(adorned): 
                        next = adorned[nextidx].split("\t")
                        next_token, next_pos,next_standard = next[0], next[2], next[3]
                
                ############ 
                # SEGMENT BOUNDARY IS WITHIN ITALICIZED SPAN   
                ############
                if re.search(r"ENDITALICS",next_token): 
                    # "STARTITALICS <segment> . ENDITALICS <next segment>"
                    self.update(next_token, next_pos, next_standard)
                    adorned[nextidx] = ""
                    nextidx += 1 
                    if nextidx < len(adorned): 
                        next = adorned[nextidx].split("\t")
                        next_token, next_pos,next_standard = next[0], next[2], next[3]
                    

                
                ############ 
                # DO NOT ALLOW NUMBERS TO BEGIN SENTENCES   
                # avoid starting the current segment with a number or parenthetical 
                # the boundary of the prior segment is not a colon, semicolon, or question mark 
                ############

                if not re.match(r"\:|\;|\?|\\|\/|\!",token) and (isNumeral(next_token) or "crd" in next_pos):
                    self.update(next_token, next_pos, next_standard)
                    self.curr_last_token = next_token 
                    adorned[nextidx] = ""
                    continue 
                elif re.match(r"\(|\)",next_token):
                    self.update(next_token, next_pos, next_standard)
                    self.curr_last_token = next_token 
                    adorned[nextidx] = ""
                    continue

                
                ############ 
                # ADD SEGMENT OR COMBINE WITH PRIOR SEGMENT 
                # Average length of a Bible verse is 23 words with white space tokenization  
                # Common lengths in order from top to low: [17, 18, 16, 15, 19, 14, 20, 21, 13, 22]
                ############         

                if (re.match(r"\:|\;|\?|\\|\/|\!|\.",standard) or EOS == "1"):
                    if len(self.segments) > 0: # there is a prior segment 
                        prior_segment = self.segments[-1][3].split(" ")
                        prior_section = self.segments[-1][0]
                        last_token = prior_segment[-1]
                        first_token = self.curr_segment[0]

                        # check that the prior segment belongs in the same section 
                        if self.curr_section.split("^")[-1] != prior_section.split("^")[-1]:
                            self.add_segment()
                            continue

                        if isNumeral(self.prior_last_token) and first_token not in conjunctions and first_token not in start_words: 
                            # the last word of the prior segment is a number 
                            self.combine_with_prior_segment()
                            continue
                        
                        # combine short segments 
                        if self.curr_length <= 15 and self.prior_length <= 15:
                            if re.search(r'^[a-z]',first_token):
                                # current segment begins with a lower case word or numeral 
                                self.combine_with_prior_segment()
                                continue
                            if isNumeral(first_token) and re.search(r"\.|\,",token):
                                self.combine_with_prior_segment()  
                            elif (not re.search(r"\.|ENDITALICS|ENDNOTE",last_token)): 
                                # prior segment ends with a non-period punctuation mark 
                                self.combine_with_prior_segment()
                                continue
                            
                    self.add_segment() 
                elif self.curr_length >= 60 and (next_standard in conjunctions or next_standard in start_words): 
                    self.add_segment()   
                elif self.curr_length >= 120 and next_standard.capitalize() in conjunctions: 
                    self.add_segment()
                
                

