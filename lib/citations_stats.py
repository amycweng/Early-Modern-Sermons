import sys,re,json
sys.path.append('../')
from lib.visualization import * 
from lib.dictionaries.authors import * 
from lib.standardization import * 
from collections import defaultdict
import pandas as pd

def read_citations(era_name):
    citation_info = pd.read_csv(f"/Users/amycweng/DH/SERMONS_APP/db/data/{era_name}/citations.csv",
                            names=['tcpID',"sidx","loc","cidx","citation","outlier","replaced"]
                            )

    citations = {}
    tcpIDs = citation_info['tcpID']
    for idx, tcpID in enumerate(tcpIDs):
        
        if 'B' in tcpID: 
            prefix = 'B'
        else: 
            prefix = tcpID[:2]
        if tcpID not in era_ids[prefix]: continue
        sidx = citation_info['sidx'][idx]

        if (tcpID,sidx) not in citations:     
            citations[(tcpID,sidx)] = [[],[]]
        else: 
            decomposed = citation_info['citation'][idx]
            if isinstance(decomposed,float): continue
            decomposed = decomposed.split("; ")
            book = decomposed[0].split(" ")[0]
            if book == "Ibidem" and len(citations[(tcpID,sidx)][0]) > 0: 
                # address ibidem problem; still need to address the verse/ver problem 
                prior = citations[(tcpID,sidx)][0][-1].split(" ")
                if re.search(r"\d|\^",prior[0]): 
                    book = prior[0] + " " + prior[1]
                else: 
                    book = prior[0] 
                priornum = prior[1].split(".")
                for d, decomposed_citation in enumerate(decomposed):
                    currnum = decomposed_citation.split(" ")[1]
                    if len(priornum) == 2 and len(currnum.split(".")) == 1: 
                        decomposed[d] = f"{book} {priornum[1]}.{currnum}"
                    else: 
                        decomposed[d] = f"{book} {currnum}"
            sidx = citation_info['sidx'][idx]
            citations[(tcpID,sidx)][0].extend(decomposed)
            if 'Note' in citation_info['loc'][idx]: 
                location =  "marginal"
            else: location = "in-text"
            citations[(tcpID,sidx)][1].extend([location]*len(decomposed))
    return citations 

def get_citations(citations, tcpIDs, loc="all"): 
    tcpIDs = {k:None for k in tcpIDs}
    all_books = {}
    all_chapters = {}
    all_verses = {}
    segment_ids = {}
    segment_ids_c = {} # associated with chapter citations only 
    for cid,cited in citations.items(): 
        tcpID, sidx = cid 
        if tcpID not in tcpIDs: continue
        if len(cited[0]) == 0: continue
        if loc != "all" and cited[1][0] != loc:  
            continue
        cited = cited[0]
        for c in cited: 
            c = c.split(" ")
        
            if re.match(r'[\d\^]',c[0]): 
                # numbered book with unknown number
                if c[0] == '^':  
                    continue
                book = f"{c[0]}-{c[1]}"
                ref = c[2]
            else: 
                book = c[0]
                ref = c[1]
            
            if book not in all_books: 
                all_books[book] = []
            all_books[book].append(tcpID)

            ref = ref.split(".")
            chapter = ref[0]
            if '*' not in chapter and "^" not in chapter: 
                key = f"{book} {chapter}"
                if key not in all_chapters: 
                    all_chapters[key] = []
                all_chapters[key].append(tcpID)
                if len(ref) == 2: 
                    verse = ref[1]
                    if '*' not in verse and "^" not in verse: 
                        key = f"{book}-{chapter}-{verse}"
                        
                        if key not in all_verses: 
                            all_verses[key] = []
                            segment_ids[key] = []
                        all_verses[key].append(tcpID)
                        segment_ids[key].append(f"{tcpID},{sidx}")
                else: 
                    key = f"{book}-{chapter}" 
                    if key not in segment_ids_c: 
                        segment_ids_c[key] = []
                    segment_ids_c[key].append(f"{tcpID},{sidx}")
    with open(f'../assets/citations/{era_name}_verse_citation_segments.json','w+') as file: 
        json.dump(segment_ids,file)
    with open(f'../assets/citations/{era_name}_chapter_citation_segments.json','w+') as file: 
        json.dump(segment_ids_c,file)
    print(era_name)
    print("{} labels and {} verse citations".format(len(segment_ids),sum([len(_) for c, _ in segment_ids.items()])))
    print("{} labels and {} chapter citations".format(len(segment_ids_c),sum([len(_) for c, _ in segment_ids_c.items()])))
    return all_books, all_chapters, all_verses

def count_citations(c,v): # chapter and verse citations only 
    c_count = defaultdict(list)
    for k, ver in v.items(): 
        k = k.split(" ")
        if k[0].isdigit():
            chap, verse = k[2].split(".")
            new_k = f"{k[0]}-{k[1]}-{chap}.{verse}"
        else: 
            chap, verse = k[1].split(".")
            new_k = f"{k[0]}-{chap}.{verse}"
        c_count[new_k].append(len(ver))

    for k, ver in c.items(): 
        k = k.split(" ")
        if k[0].isdigit():
            chap = k[2]
            new_k = f"{k[0]}-{k[1]}-{chap}"
        else: 
            chap = k[1]
            new_k = f"{k[0]}-{chap}"
        c_count[new_k].append(len(ver))
    c_count = {k:sum(v) for k,v in c_count.items()}
    return c_count


if __name__ == "__main__": 
    with open(f"../assets/corpora.json") as file:
        era_tcpIDs = json.load(file)

    for era_name in era_tcpIDs: 

        era_ids = era_tcpIDs[era_name]

        # read citations from file 
        citations = read_citations(era_name)

        # format citations 
        all_era = []
        for prefix, id_list in era_ids.items(): 
            all_era.extend(id_list)
        b, c,v = get_citations(citations, all_era)

        # c_count = count_citations(c,v)
        # with open(f'../assets/citations/{era_name}_citations.json','w+') as file: 
        #     json.dump((b,c,v),file)
        
