import sys,csv,json
sys.path.append('../')
import pandas as pd 
from EEPS_citationID import * 
from tqdm import tqdm 
import warnings 
warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)

FOLDER = '/Users/amycweng/DH/SERMONS_APP/db/data'
OUTPUT_FOLDER = '/Users/amycweng/DH/CITATIONS'

def PROCESS_CITATIONS(ERA,prefix): 
    formatted_citations = []
    
    body = pd.read_csv(f"{FOLDER}/{ERA}/{prefix}_body.csv",
                            names = ["tcpID","sidx","section","loc","loc_type","pid","tokens","standardized"])
    progress = tqdm(enumerate(body["tokens"]))
    # progress = enumerate(body["tokens"])
    for idx, token_str in progress: 
        tcpID = body["tcpID"][idx]
        # progress.set_description(tcpID)
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
    with open('../assets/corpora.json','r') as file: 
        corpora = json.load(file)
    target_era = input("Enter era or All: ")
    target_prefix = input("Enter prefix or All: ")
    target_tcpID = input("Enter tcpID or All: ")
    # target_era = "pre-Elizabeth"
    # target_prefix = "A1"
    # target_tcpID = "A17223"
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

            if len(tcpIDs) == 0: continue 
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
    