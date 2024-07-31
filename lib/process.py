import re,json
import sys 
sys.path.append('../')
from lib.standardization import * 
from lib.sentences import *
import pandas as pd 
from tqdm import tqdm 
sermons_metadata = pd.read_csv("../assets/sermons.csv")
sermons = sorted(sermons_metadata["id"])

def get_ids(group): 
    return sorted([tcpID for tcpID in sermons if group in tcpID])

# primary key is (sent_idx, text_idx)
columns = ['sent_idx', 'text_idx', 'is_note', 'encoding']
def encode(tcpID): 
    Text = Sentences(tcpID)
    margins = []
    sents = {}
    info = {}

    for sent_idx, tuple in enumerate(Text.sentences):

        section_idx, start_page, paragraph, s, p, l = tuple 
        info[sent_idx] = (section_idx, start_page, paragraph)

        sentence, pos, standardized = [], [] ,[]
        s, p, l = s.split(" "), p.split(" "),l.split(" ")
        for t, token in enumerate(s): 
            if token != ".": 
                sentence.append(s[t])
                pos.append(p[t])
                standardized.append(l[t])
            elif t-1 >= 0: 
                sentence[-1] = sentence[-1] + "."
                pos[-1] = pos[-1] + "." # indicates that the period at end of the word is a sentence boundary and its own token
                standardized[-1] = standardized[-1] + "."

        encoded = []
        start_note, in_note = False, False 
        note_tag = 0 
        t = -1  
        for token in sentence: 
            if token == ".": continue 
            
            t += 1 
             
            if re.search(r"STARTNOTE\d+", token):
                # add a placeholder to retain the note's position in the text 
                encoded.append(('<NOTE>',"NOTE",'<NOTE>',0))
                in_note, start_note = True, True 
            elif re.search(r"ENDNOTE\d+",token): 
                in_note = False
            elif token == "STARTITALICS": 
                encoded.append(('<i>',"<i>",'<i>',note_tag)) 
            elif token == "ENDITALICS": 
                encoded.append(('</i>',"</i>",'</i>',note_tag))
            else:
                if start_note:
                    note_tag, start_note = 1, False
                elif in_note: 
                    note_tag = 2
                else: 
                    note_tag = 0
                
                if token == "NONLATINALPHABET": 
                    encoded.append((token, "foreign", token, note_tag))
                
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
        progress.set_description(era + " " + tcpID) 
        m, s, i = encode(tcpID)
        margins[tcpID] = m 
        texts[tcpID] = s
        info[tcpID] = i 

    with open(f"../assets/processed/{era}/json/{prefix}_marginalia.json","w+") as file: 
        json.dump(margins, file)
        print("wrote marginalia")

    with open(f"../assets/processed/{era}/json/{prefix}_texts.json","w+") as file: 
        json.dump(texts, file)
        print("wrote texts")

    with open(f"../assets/processed/{era}/json/{prefix}_info.json","w+") as file: 
        json.dump(info, file)
        print("wrote sentence info")

import os 
if __name__ == "__main__": 
    already_adorned = os.listdir('../assets/adorned')
    already_adorned = {k.split(".txt")[0]:None for k in already_adorned}

    with open('../assets/corpora.json','r') as file: 
        corpora = json.load(file)
    
    # era = input('Enter subcorpus name: ')
    for era in corpora: 
        for prefix,tcpIDs in corpora[era].items():
            tcpIDs = sorted(tcpIDs)
            tcpIDs = [tcpID for tcpID in tcpIDs if tcpID in already_adorned]
            if len(tcpIDs) == 0: continue
            process_prefix(tcpIDs,era, prefix)