import re 


tcpID = 'A00003'
with open(f"../assets/adorned/{tcpID}.txt","r") as file: 
    adorned = file.readlines()
sentences = []
curr_sermon, curr_sent, curr_page = 0, 0, 0 
curr_sentence = []
curr_pos = []
curr_in_note = False 
curr_fw = False 

# tcpID, sermon, start_page, sentence, sent_idx, sentence_pos, sentence_lemmas   
for idx, item in enumerate(adorned): 
    parts = item.strip("\n").split("\t")
    if len(item) == 0: continue

    token, pos, lemma, EOS = parts[0], parts[2], parts[4], parts[5]
    
    if re.search(r"SERMON\d+",token):
        # start of a new sermon in the text 
        curr_sermon += 1 
    elif re.search(r"PAGE\d+",token): 
        curr_page += 1 
    
    else: 
        curr_sentence.append(token)
        curr_pos.append(pos)

        if re.search(r"STARTNOTE\d+",token): 
            # beginning of a note
            curr_in_note = True 
        elif re.search(r"ENDNOTE\d+",token): 
            # end of a note 
            curr_in_note = False
        

        if EOS == "1" and idx < len(adorned)-1:
            next = adorned[idx+1].split("\t")
            next_token, next_pos, next_lemma = next[0], next[2], next[4]

            if pos != token: 
                if next_pos == "crd" or len(curr_sentence) == 1: 
                    continue

            if re.search(r"ENDNOTE\d+",next_token): 
                # case of a sentence boundary occuring within a note  
                # do not end sentence 
                curr_sentence.append(next_token)
                curr_pos.append(next_pos)
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
                        curr_sentence.append(next_token)
                        curr_pos.append(next_pos)
                        adorned[idx+1] = ""
                    
                    if (re.search(r"^[a-z0-9]",curr_sentence[0]))and len(sentences) > 0: 
                        a,b,c,d,e = sentences[-1]
                        sentences[-1] = (a,b,c, d+ " " + " ".join(curr_sentence),e + " " + " ".join(curr_pos))
                    elif re.search(r"STARTITALICS",curr_sentence[0]) and len(sentences) > 0:                    
                        a,b,c,d,e = sentences[-1]
                        if "crd" in e:
                            sentences[-1] = (a,b,c, d+ " " + " ".join(curr_sentence),e + " " + " ".join(curr_pos))
                        else: 
                            sentences.append((curr_sermon, curr_page, curr_sent, " ".join(curr_sentence)," ".join(curr_pos)))
                    else: 
                        sentences.append((curr_sermon, curr_page, curr_sent, " ".join(curr_sentence)," ".join(curr_pos)))
                    curr_sentence = []
                    curr_pos = []
                    curr_sent += 1 

        elif EOS == "1": # reached the end of the last sentence 
            sentences.append((curr_sermon, curr_page, curr_sent, " ".join(curr_sentence)," ".join(curr_pos)))
            

for a,b,c,d,e in sentences: 
    print(d,"\n")
