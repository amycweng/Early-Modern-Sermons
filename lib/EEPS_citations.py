import sys,csv,json,re
sys.path.append('../')
import pandas as pd 
from EEPS_citationID import * 
from tqdm import tqdm 
import warnings 
warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)

from EEPS_helper import folder

FOLDER = f'{folder}/SERMONS_APP/db/data'
OUTPUT_FOLDER = f'{folder}/CITATIONS'

def PROCESS_CITATIONS(ERA,prefix): 
    formatted_citations = []
    
    body = pd.read_csv(f"{FOLDER}/{ERA}/{prefix}_body.csv",
                            names = ["tcpID","sidx","section","loc","loc_type","pid","tokens","standardized","pos"])
    # progress = enumerate(body["tokens"])
    print(ERA,prefix)
    for idx, token_str in tqdm(enumerate(body["tokens"])): 
        tcpID = body["tcpID"][idx]
        # if tcpID != "B07186": continue
        sidx = body["sidx"][idx]
        token_str = re.sub(r"\<i\>|\<\/i\>"," ",token_str)
        token_str = re.sub(r"\s+"," ",token_str)
        
        # if "ii cor iiii" not in token_str: continue 

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
    # progress = enumerate(marginalia["tokens"])
    for idx, token_str in progress: 
        tcpID = marginalia["tcpID"][idx]
        # if tcpID != "B07186": continue
        progress.set_description(tcpID+" marginalia") 
        # if "ii cor iiii" not in token_str: continue 
        sidx = marginalia["sidx"][idx]
        nidx = marginalia["nidx"][idx]
        token_str = re.sub(r"\<i\>|\<\/i\>"," ",token_str)
        token_str = re.sub(r"\s+"," ",token_str)
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
        with open(f"{OUTPUT_FOLDER}/{ERA}_{prefix}_citations.csv","w+") as outfile: 
            writer = csv.DictWriter(outfile, fieldnames=formatted_citations[0].keys())
            writer.writerows(formatted_citations)


if __name__ == "__main__":
    # print(extract_citations("Num. 13.30. & 14.9."))
    with open('../assets/corpora.json','r') as file: 
        corpora = json.load(file)
    target_era = input("Enter era or All: ")
    target_prefix = input("Enter prefix or All: ")

    # target_era = "JamesI"
    # target_prefix = "B"

    for era in corpora:
        if target_era != "All":
            if era != target_era: 
                continue 
        for prefix,tcpIDs in corpora[era].items(): 
            # if era in ['CharlesI'] and prefix in ['B','A0']:continue
            if len(tcpIDs) == 0: continue
            if target_prefix != "All":
                if prefix != target_prefix: 
                    continue 
                
 
            PROCESS_CITATIONS(era,prefix)

    # print(extract_citations("3 John 23.12"))
    # print(extract_citations("3 John 23.24,25,26"))
    # print(extract_citations("3 John 23. 24, 25,26"))
    # print(extract_citations("3 John 23.24-25"))
    # print(extract_citations("3 John 23.2•-25"))
    # print(extract_citations("3 John 23.22-•4"))
    # print(extract_citations("3 John 22-•4"))
    # print(extract_citations("3 John 12.12,13,15,4.4"))
    # print(extract_citations("3 John 12.12,13-15,4.4"))

    # print(extract_citations("3 John 12.12,•-15,4.•"))
    # •
    # print(extract_citations("• John 12.12,•-15,4.•"))
    # print(extract_citations('Gene. 7.8.'))
    # print(extract_citations('1 Cor. cap. 8. 9. & 10.'))
    # print(extract_citations("Rom viii • ii cor iiii and v psa xliiii e"))
    # print(extract_citations("Esay 51.12, & 7, 8."))
    