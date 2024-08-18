import sys,csv,json
sys.path.append('../')
import pandas as pd 
from lib.standardization import * 
from tqdm import tqdm 

FOLDER = '/Users/amycweng/DH/SERMONS_APP/db/data'

def PROCESS_CITATIONS(ERA,prefix): 
    formatted_citations = []
    
    body = pd.read_csv(f"{FOLDER}/{ERA}/{prefix}_body.csv",
                            names = ["tcpID","sidx","section","loc","loc_type","pid","tokens","standardized"])
    progress = tqdm(enumerate(body["tokens"]))
    for idx, token_str in progress: 
        tcpID = body["tcpID"][idx]
        progress.set_description(tcpID)
        sidx = body["sidx"][idx]
        token_str = re.sub(r"NONLATINALPHABET|\<i\>|\<\/i\>"," ",token_str)
        token_str = re.sub(r"\s+"," ",token_str)
        cited, outliers, replaced = extract_citations(token_str)
        for cidx, c_list in cited.items(): 
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
    

    marginalia = pd.read_csv(f"{FOLDER}/{ERA}/{prefix}_margin.csv"
                    , names = ["tcpID","sidx","nidx","tokens","standardized"])
    progress = tqdm(enumerate(marginalia["tokens"]))
    for idx, token_str in progress: 
        tcpID = marginalia["tcpID"][idx]
        progress.set_description(tcpID+" marginalia") 
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
    if len(formatted_citations) > 0: 
        with open(f"{FOLDER}/{ERA}/{prefix}_citations.csv","w+") as outfile: 
            writer = csv.DictWriter(outfile, fieldnames=formatted_citations[0].keys())
            writer.writerows(formatted_citations)
    