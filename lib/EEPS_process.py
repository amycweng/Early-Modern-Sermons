import re,json
import sys 
sys.path.append('../')
from lib.standardization import * 
from lib.EEPS_sentences import *
from lib.sermons import *
from lib.citations import *  

import pandas as pd 
from tqdm import tqdm 
sermons_metadata = pd.read_csv("../assets/sermons.csv")
sermons = sorted(sermons_metadata["id"])

def get_ids(group): 
    return sorted([tcpID for tcpID in sermons if group in tcpID])

# primary key is (sent_idx, text_idx)
columns = ['sent_idx', 'text_idx', 'is_note', 'encoding']
def encode(tcpID): 
    encoded = []
    Text = Sentences(tcpID)

    for sent_idx, tuple in enumerate(Text.sentences):
        section_idx, start_page, paragraph, s, p, l = tuple 
        sentence, pos, regular, lemma = [], [] ,[], []
        s, p, l = s.split(" "), p.split(" "),l.split(" ")
        for t, token in enumerate(s): 
            sentence.append(s[t])
            pos.append(p[t])
            if " REGLEMSPLIT " in l[t]:
                reg, lem = l[t].split(" REGLEMSPLIT ")
            else: 
                reg,lem = token, token
            regular.append(reg)
            lemma.append(lem)

        start_note, in_note = False, False 
        start_it, in_it = False, False
        note_tag,it_tag = 0,0 
        t = -1  
        for token in sentence: 
            
            t += 1 
             
            if re.search(r"STARTNOTE\d+", token):
                in_note, start_note = True, True
            elif re.search(r"ENDNOTE\d+",token):
                in_note = False
            elif token == "STARTITALICS":
                in_it, start_it = True, True
            elif token == "ENDITALICS":
                in_it = False
            else:
                if start_note: # 1 is B, 2 is I, 0 is O
                    note_tag, start_note = 1, False
                elif in_note: 
                    note_tag = 2
                else: 
                    note_tag = 0
                
                if start_it: 
                    it_tag, start_it = 1, False
                elif in_it: 
                    it_tag = 2
                else: 
                    it_tag = 0  
                
                if token == "NONLATINALPHABET":
                    regular[t] = token
                    lemma[t] = token
                    pos[t] = "fw-nonla"
                entry = (token, pos[t], regular[t], lemma[t], 
                        note_tag, it_tag,
                        sent_idx,int(section_idx),paragraph,
                        Text.section_names[section_idx]
                        )
                if len(entry) != 10: print(entry)
                encoded.append(entry)
    encoded = pd.DataFrame(encoded,columns=['token','pos','regular','lemma',
                                            'note_tag','it_tag',
                                            'sent_idx','section_idx','paragraph_idx',
                                            'section_name'])
    encoded.to_csv(f"/Users/amycweng/DH/EEPS/encodings/{tcpID}_encoded.csv",index=False) 

def process_prefix(tcpIDs,era): 
    tcpIDs = tqdm(tcpIDs)
    for tcpID in tcpIDs:
        tcpIDs.set_description(era + " " + tcpID)
        encode(tcpID) 

import os 
if __name__ == "__main__": 
    already_adorned = os.listdir('../assets/adorned')
    already_adorned = {k.split(".txt")[0]:None for k in already_adorned}

    with open('../assets/corpora.json','r') as file: 
        corpora = json.load(file)
    
    for era in corpora:  
        for prefix,tcpIDs in corpora[era].items(): 
            tcpIDs = sorted(tcpIDs)
            tcpIDs = [tcpID for tcpID in tcpIDs if tcpID in already_adorned]
            if len(tcpIDs) == 0: continue
            process_prefix(tcpIDs,era)

