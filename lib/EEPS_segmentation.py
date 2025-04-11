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
        # if tcpID != "A03342": continue 
        progress.set_description(era + " " + tcpID) 
        m, s, i = encode(tcpID)
        margins[tcpID] = m 
        texts[tcpID] = s
        info[tcpID] = i 

    PROCESS_SERMONS(era,prefix,texts,margins,info)

import os 
if __name__ == "__main__": 
    already_adorned = os.listdir('../assets/adorned')
    already_adorned = {k.split(".txt")[0]:None for k in already_adorned}

    with open('../assets/corpora.json','r') as file: 
        corpora = json.load(file)
    
    target_era = input("Enter era or All: ")
    target_prefix = input("Enter prefix or All: ")
    target_tcpID = input("Enter tcpID or All: ")
    for era in corpora:
        if target_era != "All":
            if era != target_era: 
                continue 
        for prefix,tcpIDs in corpora[era].items(): 
            if target_prefix != "All":
                if prefix != target_prefix: 
                    continue 
                
            if target_tcpID != "All":
                tcpIDs = [target_tcpID]


    # redo = {('Elizabeth', 'A1'): 34, ('JamesI', 'A1'): 30, ('JamesI', 'A0'): 28, ('CharlesI', 'A1'): 27, ('Elizabeth', 'A0'): 24, ('CharlesI', 'A0'): 20, ('CharlesII', 'A6'): 20, ('CharlesII', 'A5'): 19, ('WilliamAndMary', 'A4'): 18, ('WilliamAndMary', 'A6'): 17, ('CharlesII', 'A2'): 16, ('WilliamAndMary', 'A5'): 15, ('CharlesII', 'A3'): 15, ('WilliamAndMary', 'A3'): 14, ('CharlesII', 'A4'): 13, ('WilliamAndMary', 'A2'): 10, ('pre-Elizabeth', 'A0'): 8, ('Interregnum', 'A8'): 8, ('Interregnum', 'A7'): 7, ('Interregnum', 'A9'): 6, ('Interregnum', 'A3'): 6, ('JamesI', 'A2'): 6, ('JamesI', 'B'): 6, ('CivilWar', 'A8'): 5, ('pre-Elizabeth', 'A1'): 5, ('CivilWar', 'A9'): 5, ('CivilWar', 'A7'): 4, ('CharlesII', 'B'): 4, ('JamesII', 'A4'): 3, ('Elizabeth', 'A6'): 3, ('CharlesI', 'A6'): 3, ('CharlesII', 'A7'): 3, ('JamesII', 'A3'): 3, ('Interregnum', 'A2'): 3, ('CivilWar', 'A5'): 3, ('CharlesII', 'A9'): 3, ('Interregnum', 'B'): 2, ('CharlesI', 'A7'): 2, ('JamesII', 'A6'): 2, ('WilliamAndMary', 'A7'): 2, ('Interregnum', 'A6'): 2, ('Elizabeth', 'A7'): 2, ('Elizabeth', 'A2'): 2, ('JamesI', 'A6'): 2, ('Elizabeth', 'B'): 2, ('JamesI', 'A7'): 2, ('WilliamAndMary', 'B'): 2, ('Interregnum', 'A4'): 2, ('Interregnum', 'A5'): 2, ('CharlesII', 'A8'): 2, ('CharlesI', 'A3'): 2, ('CharlesI', 'B'): 2, ('CivilWar', 'A6'): 1, ('JamesII', 'B'): 1, ('pre-Elizabeth', 'B'): 1, ('CivilWar', 'B'): 1, ('WilliamAndMary', 'A9'): 1, ('CharlesI', 'A8'): 1, ('CharlesI', 'A5'): 1, ('JamesII', 'A2'): 1}
    # redo = sorted(list(redo.keys()))
    # for pair in redo:
    #         era, prefix = pair 
            # tcpIDs = sorted(corpora[era][prefix])
            
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