import re,json
import sys 
sys.path.append('../')
from lib.standardization import * 
from lib.sentences import *
import pandas as pd 

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

        sermon_idx, start_page, paragraph, s, p, l = tuple 
        info[sent_idx] = (sermon_idx, start_page, paragraph)

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
        in_italics, in_note = False, False 
        start_italics, start_note = False, False

        t = -1  
        for token in sentence: 
            if token == ".": continue 
            
            t += 1 
            
            if token == "STARTITALICS": 
                in_italics, start_italics = True, True  
            elif token == "ENDITALICS": 
                in_italics = False 
            elif re.search(r"STARTNOTE\d+", token):
                # add a placeholder to retain the note's position in the text 
                encoded.append((f'<NOTE>',"NOTE",f'<NOTE>',0,0))
                in_note, start_note = True, True 
            elif re.search(r"ENDNOTE\d+",token): 
                in_note = False
            else:
                if start_italics:
                    it_tag, start_italics = 1, False
                elif in_italics: 
                    it_tag = 2
                else: 
                    it_tag = 0
                
                if start_note:
                    note_tag, start_note = 1, False
                elif in_note: 
                    note_tag = 2
                else: 
                    note_tag = 0
                
                if token == "NONLATINALPHABET": 
                    encoded.append((token, "foreign", token, it_tag, note_tag))
                
                encoded.append((token, pos[t], standardized[t], it_tag, note_tag))

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
    progress = tcpIDs[0][:3] 
    for tcpID in tcpIDs: 
        m, s, i = encode(tcpID)
        margins[tcpID] = m 
        texts[tcpID] = s
        info[tcpID] = i 
        if tcpID[:3] != progress: 
            progress = tcpID[:3]
            print(progress)
    print('finished all')

    with open(f"../assets/processed/{era}/json/{prefix}_marginalia.json","w+") as file: 
        json.dump(margins, file)
        print("wrote marginalia")

    with open(f"../assets/processed/{era}/json/{prefix}_texts.json","w+") as file: 
        json.dump(texts, file)
        print("wrote texts")

    with open(f"../assets/processed/{era}/json/{prefix}_info.json","w+") as file: 
        json.dump(info, file)
        print("wrote sentence info")


if __name__ == "__main__": 
    with open('../assets/corpora.json','r') as file: 
        corpora = json.load(file)
    # era = "pre-Elizabethan"
    era = input('Enter subcorpus name: ')
    for prefix,tcpIDs in corpora[era].items():
        tcpIDs = sorted(tcpIDs)
        if len(tcpIDs) == 0: continue
        process_prefix(tcpIDs,era, prefix)