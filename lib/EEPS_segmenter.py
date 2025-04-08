import re
from collections import defaultdict
from EEPS_helper import * 

class Segments(): 
    def __init__(self,tcpID): 
        self.tcpID = tcpID
        self.segments = []
        self.curr_section = None  
        self.curr_page = None 
        self.curr_paragraph = 0 # paragraph is a global index (continuous over sections/DIVs)
        self.curr_segment = []
        self.curr_pos = [] # part of speech 
        self.curr_standard = [] # standardized terms 
        self.curr_in_note = False  
        self.curr_length = 0 # the length of the current segment excluding note spans & italic markers 
        self.curr_last_token = None 
        self.prior_length = 0 # the length of the prior segment excluding note spans & italic markers 
        self.prior_last_token = None # last non-note token in the prior segment

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

    def add_segment(self):
        if self.curr_length > 0:  
            self.segments.append((self.curr_section, self.curr_page, self.curr_paragraph, 
                                    " ".join(self.curr_segment),
                                    " ".join(self.curr_pos),
                                    " ".join(self.curr_standard)))
            self.prior_length = self.curr_length 
            self.prior_last_token = self.curr_last_token 
            self.reset()

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
    
    def segment(self): 
        with open(f"../assets/adorned/{self.tcpID}.txt","r") as file: 
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
                self.curr_section = token
                # get accurate page number 
                self.curr_page = find_curr_page(idx,adorned)
            
            ############ 
            # NEW PAGE 
            ############            
            elif re.search(r"^PAGE[\d+\w+]",token):      
                curr_page_type,curr_page,currisRoman = get_page_number(token)
                self.curr_page = f"{curr_page_type}{curr_page}{currisRoman}"
            

            else:
                ############ 
                # NEW PARAGRAPH OR MARGINALIUM OR 
                # ADD TOKEN TO SEGMENT 
                ############
        
                if re.search(r"STARTNOTE",token):
                    self.curr_in_note = True 
                    self.update(token,pos,standard)
                elif re.search(r"ENDNOTE",token): 
                    self.curr_in_note = False 
                    self.update(token,pos,standard)
                elif not re.search(r"PARAGRAPH\d+",token):  
                    self.update(token,pos,standard)
                    if token not in ['STARTITALICS', 'NONLATINALPHABET', 'ENDITALICS'] and not self.curr_in_note:
                        if not re.match(r"\:|\;|\?|\\|\/|\!|\,|\.",token): 
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
                if self.curr_length == 1: # ensures that "FINIS." is its own segment 
                    if idx == (len(adorned)-1): 
                        self.combine_with_prior_segment()
                    continue 

                ############ 
                # FIND NEXT TOKEN 
                ############        
                next_token, next_pos,next_standard = "","",""
                next_token_non_punc, next_pos_non_punc = "",""
                nextidx = idx+1 
                if nextidx == len(adorned): break # at the end of document 
                next = adorned[nextidx].split("\t")
                next_token, next_pos,next_standard = next[0], next[2], next[3]
                while next_pos_non_punc == next_token_non_punc: 
                    if nextidx == len(adorned): break 
                    next_non_punc = adorned[nextidx].split("\t")
                    next_token_non_punc, next_pos_non_punc = next_non_punc[0], next_non_punc[2]
                    nextidx += 1 

                ############ 
                # SEGMENT BOUNDARY IS WITHIN MARGINALIUM  
                ############
                if re.search(r"ENDNOTE\d+",next_token): 
                    self.update(next_token, next_pos, next_standard)
                    adorned[idx+1] = ""
                    self.curr_in_note = False 
                    if nextidx < len(adorned):  
                        next_non_punc = adorned[nextidx].split("\t")
                        next_token_non_punc, next_pos_non_punc = next_non_punc[0], next_non_punc[2]
                        nextidx += 1 
                
                ############ 
                # SEGMENT BOUNDARY IS WITHIN ITALICIZED SPAN   
                ############
                if re.search(r"ENDITALICS",next_token): 
                    # "STARTITALICS <segment> . ENDITALICS <next segment>"
                    self.update(next_token, next_pos, next_standard)
                    adorned[idx+1] = ""
                    if nextidx < len(adorned):  
                        next_non_punc = adorned[nextidx].split("\t")
                        next_token_non_punc, next_pos_non_punc = next_non_punc[0], next_non_punc[2]
                        nextidx += 1 
                
                ############ 
                # DO NOT ALLOW NUMBERS TO BEGIN SENTENCES   
                # avoid starting the current segment with a number or parenthetical 
                # the boundary of the prior segment is not a colon, semicolon, or question mark 
                ############
                isNumeral = False 
                if re.search(r"^[0-9\^\(\)]",next_token): 
                    isNumeral = True 
                else: 
                    num = convert_numeral(next_token)
                    if isinstance(num,int): 
                        isNumeral = True 
                if isNumeral or "crd" in next_pos:
                    self.update(next_token, next_pos, next_standard)
                    adorned[idx+1] = ""
                    if nextidx < len(adorned):  
                        next_non_punc = adorned[nextidx].split("\t")
                        next_token_non_punc, next_pos_non_punc = next_non_punc[0], next_non_punc[2]
                        nextidx += 1 
                
                ############ 
                # ADD SEGMENT OR COMBINE WITH PRIOR SEGMENT 
                # Average length of a Bible verse is 23 words with white space tokenization  
                # Common lengths in order from top to low: [17, 18, 16, 15, 19, 14, 20, 21, 13, 22]
                ############          
                
                if (re.match(r"\:|\;|\?|\\|\/|\!|\.",token) or EOS == "1"):
                    if len(self.segments) > 0: # there is a prior segment 
                        prior_segment = self.segments[-1][3].split(" ")
                        last_token = prior_segment[-1]
                                
                        if self.curr_length <= 10:
                            # current segment is shorter than 10 words
                            if self.prior_length <= 15: 
                                if self.curr_length <= 5: 
                                    # current segment is shorter than five words 
                                    self.combine_with_prior_segment()
                                    continue 
                                # prior segment is shorter than 20 words 
                                if re.search(r'^[a-z\d]',self.curr_segment[0]):
                                    # current segment begins with a lower case word or number 
                                    self.combine_with_prior_segment()
                                    continue
                                elif (not re.search(r"\.|ENDITALICS|ENDNOTE",last_token)): 
                                    # prior segment ends with a non-period punctuation mark 
                                    self.combine_with_prior_segment()
                                    continue
                                elif re.match(r'[a-z\d]',self.prior_last_token[0]):
                                    # the last actual word of the prior segment is in lower case or contains a number
                                    self.combine_with_prior_segment()
                                    continue
                                    
                    self.add_segment()   
                elif self.curr_length >= 23 and re.search(r"\&|and|but|so|or|then|if|than",next_token.lower()):
                    # ensure that segments are not overly long 
                    self.add_segment()
                elif self.curr_length >= 50 and next_token_non_punc[0].isupper():
                        self.add_segment 