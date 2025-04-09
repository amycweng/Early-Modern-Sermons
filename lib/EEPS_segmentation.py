import re,json
import sys 
sys.path.append('../')
from lib.standardization import * 
from lib.EEPS_segmenter import *
from lib.EEPS_sermons import *
from lib.citations import *  
from EEPS_helper import * 

import pandas as pd 
from tqdm import tqdm
import numpy as np

# primary key is (sent_idx, text_idx)
columns = ['sent_idx', 'text_idx', 'is_note', 'encoding']
def encode(tcpID): 
    Text = Segments(tcpID)
    margins = []
    sents = {}
    info = {}

    for sent_idx, tuple in enumerate(Text.segments):
        section_idx, start_page, paragraph, s, p, l = tuple 
        info[sent_idx] = (section_idx, start_page, paragraph)

        sentence, pos, standardized = [], [] ,[]
        s, p, l = s.split(" "), p.split(" "),l.split(" ")
        for t, token in enumerate(s): 
            # if token != ".": 
            sentence.append(s[t])
            pos.append(p[t])
            standardized.append(l[t])

        encoded = []
        start_note, in_note = False, False 
        note_tag = 0 
        t = -1  
        for token in sentence: 
            # if token == ".": continue 
            
            t += 1 
             
            if re.search(r"STARTNOTE\d+", token):
                # add a placeholder to retain the note's position in the text
                encoded.append(('<NOTE>',"NOTE",'<NOTE>',0))
                in_note, start_note = True, True
            elif re.search(r"ENDNOTE\d+",token):
                in_note = False
            else:
                if start_note:
                    note_tag, start_note = 1, False
                elif in_note: 
                    note_tag = 2
                else: 
                    note_tag = 0
                if token == "STARTITALICS": 
                    encoded.append(('<i>',"<i>",'<i>',note_tag)) 
                elif token == "ENDITALICS": 
                    encoded.append(('</i>',"</i>",'</i>',note_tag))
                elif token == "NONLATINALPHABET": 
                    encoded.append((token, "foreign", token, note_tag))
                
                else: 
                    encoded.append((token, pos[t], standardized[t], note_tag))

        text_parts = []
        curr = []
        in_note = False 
        for encoding in encoded: 
            if encoding[-1] == 1: 
                text_parts.append((in_note, curr))
                curr = []
                in_note = True 
            elif in_note and encoding[-1] == 0: 
                text_parts.append((in_note,curr))
                curr = []
                in_note = False
            curr.append(encoding[:3])
        text_parts.append((in_note,curr))
        
        for is_note, part in text_parts: 
            if sent_idx not in sents: sents[sent_idx] = [] 
            if not is_note: # text 
                sents[sent_idx].extend(part)
            else: 
                margins.append((sent_idx, part))
    return margins, sents, info

def process_prefix(tcpIDs,era,prefix): 
    margins = {}
    texts = {}
    info = {}
    progress = tqdm(tcpIDs)
    for tcpID in progress:
        # if tcpID != "A18708": continue 
        progress.set_description(era + " " + tcpID) 
        m, s, i = encode(tcpID)
        margins[tcpID] = m 
        texts[tcpID] = s
        info[tcpID] = i 

    PROCESS_SERMONS(era,prefix,texts,margins,info)
    # PROCESS_CITATIONS(era,prefix)

import os 
if __name__ == "__main__": 
    already_adorned = os.listdir('../assets/adorned')
    already_adorned = {k.split(".txt")[0]:None for k in already_adorned}

    with open('../assets/corpora.json','r') as file: 
        corpora = json.load(file)
    for era in corpora:
        for prefix,tcpIDs in corpora[era].items(): 
            if era in ["pre-Elizabeth","Elizabeth","JamesI",  "CharlesI", "CivilWar","Interregnum","CharlesII"]: continue
            if era == "JamesII":
                if prefix  in ["B","A0","A1","A2"]: continue  

            tcpIDs = sorted(tcpIDs)
            tcpIDs = [tcpID for tcpID in tcpIDs if tcpID in already_adorned]
            if len(tcpIDs) == 0: continue
            process_prefix(tcpIDs,era, prefix)

            segment_lengths = []
            text = pd.read_csv(f"/Users/amycweng/DH/SERMONS_APP/db/data/{era}/{prefix}_body.csv", header=None)
            for idx, item in enumerate(text[6]): 
                items = item.split(" ")
                length = len(items)
                segment_lengths.append(length)
            print(np.mean(segment_lengths), min(segment_lengths), max(segment_lengths))