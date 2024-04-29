import sys,csv,json
sys.path.append('../')
import pandas as pd 
from lib.standardization import * 

ERA = "pre-Elizabethan"
FOLDER = '/Users/amycweng/DH/SERMONS_APP/db/data'

if __name__ == "__main__": 
    with open('../assets/corpora.json','r') as file: 
        corpora = json.load(file)

    era = "pre-Elizabethan"
    prefixes = []
    for prefix,ids in corpora[era].items(): 
        if len(ids) > 0: prefixes.append(prefix)
    
    formatted_citations = []
    for prefix in prefixes: 
        done = {}
        body = pd.read_csv(f"{FOLDER}/{ERA}/{prefix}_body.csv",
                                names = ["tcpID","sidx","section","loc","loc_type","pid","tokens","lemmatized"])
        for idx, token_str in enumerate(body["tokens"]): 
            tcpID = body["tcpID"][idx]
            if tcpID not in done:
                if len(done) > 0: print('Processed',tcpID) 
                done[tcpID] = 0
            sidx = body["sidx"][idx]
            cited, outliers, replaced = extract_citations(token_str)
            for cidx, c_list in cited.items(): 
                rep = replaced[cidx]
                formatted_citations.append({
                    'tcpID': tcpID,
                    'sidx': sidx,
                    'nidx': 'In-Text', 
                    'cidx': cidx, 
                    'citation': "; ".join(c_list),
                    'outlier': [None if cidx not in outliers else outliers[cidx]][0],
                    'replaced': replaced[cidx]
                })
        print('Processed',tcpID) 
        print(f'Processed {ERA} {prefix} texts')
        
        done = {}
        marginalia = pd.read_csv(f"{FOLDER}/{ERA}/{prefix}_margin.csv"
                        , names = ["tcpID","sidx","nidx","tokens","lemmatized"])
        for idx, token_str in enumerate(marginalia["tokens"]): 
            tcpID = marginalia["tcpID"][idx]
            if tcpID not in done:
                if len(done) > 0: print('Processed',tcpID) 
                done[tcpID] = 0 
            sidx = marginalia["sidx"][idx]
            nidx = marginalia["nidx"][idx]
            cited, outliers, replaced = extract_citations(token_str)
            for cidx, c_list in cited.items(): 
                formatted_citations.append({
                    'tcpID': tcpID,
                    'sidx': sidx,
                    'nidx': f'Note {nidx}', 
                    'cidx': cidx, 
                    'citation': "; ".join(c_list),
                    'outlier': [None if cidx not in outliers else outliers[cidx]][0],
                    'replaced': replaced[cidx]
                })
        print('Processed',tcpID) 
        print(f'Processed {ERA} {prefix} marginalia')
    
    with open(f"{FOLDER}/{ERA}/citations.csv","w+") as outfile: 
        writer = csv.DictWriter(outfile, fieldnames=formatted_citations[0].keys())
        writer.writerows(formatted_citations)
    