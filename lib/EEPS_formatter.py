import pandas as pd 
import json 
import re 
import os 
import warnings
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

# get Bibles 
bible_dir = "../../DH/SERMONS_APP/db/data/Bibles"
bibles = ['Douay-Rheims','Geneva','KJV','Tyndale','Wycliffe','Vulgate']
bible_verses = {}
for b in bibles: 
    with open(f"{bible_dir}/{b}.json",'r') as f: 
        verses = json.load(f)
    for v in verses: 
        bible_verses[f'{v} ({b})'] = verses[v]
list(bible_verses.keys())[0]

main_dir = "../../DH/EEPS"
def process_file(tcpID,era): 
    use_cols = ["token","cite_label","qp_label","sent_idx"]
    df = pd.read_csv(f"{main_dir}/encodings_new/{tcpID}_encoded.csv",
                    usecols = use_cols)
    df['scriptural'] = ''
    df['non-scriptural'] = ''
    grouped_df = df.groupby('sent_idx').agg({
        'token': lambda x: ' '.join(x),  
        'cite_label':lambda x: list(set(x)),
        'qp_label':lambda x: list(set(x)),
        'scriptural': lambda x: ''.join(x),
        'non-scriptural': lambda x: ''.join(x),
    }).reset_index()
    grouped_df['qp_text']  = ''
    pattern = r"\('([^']+)', ([0-9.]+)\)"
    for idx, qp in enumerate(grouped_df['qp_label']): 
        for qp_labels in qp: 
            if not isinstance(qp_labels,float): 
                matches = re.findall(pattern, qp_labels)
                result = [(text, float(score)) for text, score in matches]
                grouped_df['qp_text'][idx] = []
                for r in result: 
                    grouped_df['qp_text'][idx].append(bible_verses[r[0]])
    new_order = ['sent_idx','token',
                'cite_label','qp_label',
                'scriptural','non-scriptural','qp_text']
    grouped_df = grouped_df[new_order]
    grouped_df.to_csv(f"{main_dir}/pending_new/{era}_{tcpID}.csv",index=False)

if __name__ == "__main__": 
    for fp in sorted(os.listdir(f"{main_dir}/pending_new")): 
        if 'Store' in fp: continue 
        tcpID = fp.split("_")[-1]
        era =  fp.split("_")[0]
        tcpID = tcpID.split(".csv")[0]
        print(tcpID,era)
        process_file(tcpID,era)
    if fp in ['Interregnum_A59589','CivilWar_A43141','CivilWar_A86098','WilliamAndMary_A58375']:  
        tcpID = fp.split("_")[-1]
        era =  fp.split("_")[0]
        process_file(tcpID,era)
