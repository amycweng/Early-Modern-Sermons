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
# OUTPUT_FOLDER = f'/Users/amycweng/Desktop/CITATIONS'


def PROCESS_CITATIONS(ERA,prefix): 
    formatted_citations = []
    
    body = pd.read_csv(f"{FOLDER}/{ERA}/{prefix}_body.csv",
                            names = ["tcpID","sidx","section","loc","loc_type","pid","tokens","standardized","pos"])
    progress = tqdm(enumerate(body["tokens"]))
    print(ERA,prefix)
    for idx, token_str in progress: 
        tcpID = body["tcpID"].iloc[idx]

        # if tcpID != "B27584": continue

        sidx = body["sidx"].iloc[idx]
        progress.set_description(tcpID)
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
    
    if f"{prefix}_margin.csv" in os.listdir(f"{FOLDER}/{ERA}"): 
         
        marginalia = pd.read_csv(f"{FOLDER}/{ERA}/{prefix}_margin.csv"
                        , names = ["tcpID","sidx","nidx","tokens","standardized","pos"])
        progress = tqdm(enumerate(marginalia["tokens"]))
        for idx, token_str in progress: 
            tcpID = marginalia["tcpID"].iloc[idx]
            # if tcpID != "B27584": continue
            progress.set_description(tcpID)
            # if tcpID != "B07186": continue
            # if "ii cor iiii" not in token_str: continue 
            sidx = marginalia["sidx"].iloc[idx]
            nidx = marginalia["nidx"].iloc[idx]
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
        print(f'Processed {ERA} {prefix} marginalia')
    if len(formatted_citations) > 0: 
        with open(f"{OUTPUT_FOLDER}/{ERA}_{prefix}_citations.csv","w+") as outfile: 
            writer = csv.DictWriter(outfile, fieldnames=formatted_citations[0].keys())
            writer.writerows(formatted_citations)


if __name__ == "__main__":
    # print(extract_citations("Acts 27.20. & 44."))
   
    with open('../assets/corpora.json','r') as file: 
        corpora = json.load(file)
    target_era = input("Enter era or All: ")
    target_prefix = input("Enter prefix or All: ")

    # target_era = "WilliamAndMary"
    # target_prefix = "B"

    for era in corpora:
       
        if target_era != "All":
            if era != target_era: 
                continue 
        
        for prefix,tcpIDs in corpora[era].items(): 

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
    