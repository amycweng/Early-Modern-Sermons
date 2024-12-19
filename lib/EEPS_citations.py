import pandas as pd 
import os, json
from tqdm import tqdm 

already_adorned = os.listdir('../assets/adorned')
already_adorned = {k.split(".txt")[0]:None for k in already_adorned}

with open('../assets/corpora.json','r') as file: 
    corpora = json.load(file)

for era in corpora:  
    qp_file = f"/Users/amycweng/DH/SERMONS_APP/db/data/{era}/paraphrases.csv"
    qp = pd.read_csv(qp_file,header=None)
    qp_tcpIDs = qp[0].tolist()
    qp_sidx = qp[1].tolist()
    qp_indices = {}
    for idx, tcpID in enumerate(qp_tcpIDs): 
        if tcpID not in qp_indices: qp_indices[tcpID] = {}
        if qp_sidx[idx] not in qp_indices: 
            qp_indices[tcpID][qp_sidx[idx]] = None 

    for prefix,tcpIDs in corpora[era].items(): 
        if era == "WilliamAndMary" and prefix in ["A0"]: continue
        tcpIDs = sorted(tcpIDs)
        tcpIDs = [tcpID for tcpID in tcpIDs if tcpID in already_adorned]
        if len(tcpIDs) == 0: continue
        citations_file = f"/Users/amycweng/DH/SERMONS_APP/db/data/{era}/{prefix}_citations.csv"
        citations = pd.read_csv(citations_file,header=None)
        sindices = citations[1].tolist()
        stcpIDs = citations[0].tolist()
        s_cited = citations[6].tolist()
        c_dict = {}
        c_endings = {}
        for idx,sidx in enumerate(sindices):
            tcpID = stcpIDs[idx]
            if tcpID not in c_dict: c_dict[tcpID] = {}
            if sidx not in c_dict[tcpID]: c_dict[tcpID][sidx] = ([],[]) 
            c = s_cited[idx].split(' ')
            if len(c[0]) == 1: 
                start = c[1]
            else: start = c[0]
            end = c[-1]
            c_dict[tcpID][sidx][0].append(start)
            c_dict[tcpID][sidx][1].append(end)


        tcpIDs = tqdm(tcpIDs)
        for tcpID in tcpIDs:
            tcpIDs.set_description(f"{era} {tcpID}")
            encoding_file = f"/Users/amycweng/DH/EEPS/encodings/{tcpID}_encoded.csv"
            encoding = pd.read_csv(encoding_file)
            encoding = encoding.to_dict(orient='records')

            citation_enc = []
            in_cited = False 

            def skip(sidx): 
                if tcpID in qp_indices: 
                    if sidx+1 in qp_indices[tcpID]: return False 
                    if sidx-1 in qp_indices[tcpID]: return False
                    if sidx in qp_indices[tcpID]: return False 
                return True 
            
            if tcpID not in c_dict: continue

            for e in encoding: 
                sidx = e['sent_idx']
                if isinstance(e['token'],float): 
                    continue 
                if sidx not in c_dict[tcpID]: 
                    e['cite_tag'] = 'O'
                    if skip(sidx): 
                        continue  
                elif e['token'].strip(".,") in c_dict[tcpID][sidx][0]: 
                    e['cite_tag'] = 'B-S' 
                    in_cited = True
                elif in_cited:
                    if e['token'].strip(".,") in c_dict[tcpID][sidx][1]: 
                        in_cited = False 
                    e['cite_tag'] = 'I-S'
                else:  
                    e['cite_tag'] = 'O' 
                
                if tcpID in qp_indices: 
                    if sidx in qp_indices[tcpID]: 
                        e['qp_tag'] = True
                    else: 
                        e['qp_tag'] = False  
                else: 
                    e['qp_tag'] = False 
                citation_enc.append(e) 
            df = pd.DataFrame(citation_enc)
            df.to_csv(encoding_file,index=False)
