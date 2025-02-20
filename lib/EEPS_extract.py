from bs4 import BeautifulSoup, SoupStrainer
import re,sys,os
sys.path.append('../') 
TCP = '/Users/amycweng/DH/TCP'

def findTextTCP(id):
    if re.match('B1|B4',id[0:2]):
        path = f'{TCP}/P2{id[0:2]}/{id}.P4.xml'
    else: 
        if f'{id}.P4.xml' in os.listdir(f'{TCP}/P1{id[0:2]}'):
            path = f'{TCP}/P1{id[0:2]}/{id}.P4.xml'
        elif f'{id}.P4.xml' in os.listdir(f'{TCP}/P2{id[0:2]}'): 
            path = f'{TCP}/P2{id[0:2]}/{id}.P4.xml'
    return path 

def extract(tcpID, filepath):
    # read the input XML file 
    with open(filepath,'r') as file: 
        data = file.read()
    # use soupstrainer to only parse the main body
    tag = SoupStrainer("DIV1")
    soup = BeautifulSoup(data,features="xml",parse_only=tag)
    
    contents = soup.find_all(['DIV1'])

    doc_text = []
    body_text = []
    num_sermons = 0
    # need to place delimiters between each sermon, marginal note, and page
    p_idx = 0 
    for idx, doc in enumerate(contents):
        n_idx = 0 # note's relative position within doc
        for t in doc.find_all(['PB']):
            # page numbers 
            if t.name == "PB" and "N" in t.attrs: 
                page = t["N"]
                t.string = f' PAGE{page} '
            else: 
                page = t["REF"]
                t.string = f' PAGEIMAGE{page} '

        for t in doc.find_all(['P']):
            # show display characters for GAP elements (illegible characters, non-Latin alphabet) 
            for gap in t.find_all("GAP"):
                if gap["DESC"] == "foreign": 
                    gap.string = " NONLATINALPHABET " # 〈 in non-Latin alphabet 〉
                # elif "DISP" in gap.attrs: 
                #     disp = gap["DISP"]
                #     disp = re.sub("•","\^",disp) # illegible letters 
                #     disp = re.sub("◊","\*",disp) # illegible words 
                #     gap.string = disp
            for italics in t.find_all("HI"):
                italics.string = f" STARTITALICS {italics.text} ENDITALICS "
            for item in t.find_all(["NOTE"]):
                if item.name == "NOTE":
                    # add note delimiters 
                    item.string = f" STARTNOTE{n_idx} {item.text} ENDNOTE{n_idx} "
                    n_idx += 1 
            t.string = f" STARTPARAGRAPH{p_idx} {t.text} "
            p_idx += 1 
        text = re.sub(r"[^\x00-\x7F]","",str(doc.text))
        text = re.sub(r"[\{\}\[\]]","",text)
        section_type = doc.get("TYPE").lower().split(" ")
        section_type = "_".join(section_type)
        text = f"{f' SECTION{idx}^{section_type}'} {text}"
        text = re.sub(r"\s+"," ",text)
            # wanted_types = ["sermon","part","text","treatise","discourse","appendix", "funeral sermon","body of text","verse",
    #             "biblical commentary","treatise","tract","doctrine",
    #             "lecture", "book","conclusion","section","commentary","chapter",
    #             "panegyric","funeral speech","arguments","homily","colophon","polemic",
    #             "scaffold speech","speech","lamentation","essay","theological discourse",
    #             "memorial","consolatio","religious tract","oration and sermon","hymns",
    #             "vindication","scripture","criticism","observation","mock sermon"]
        if re.search(r"sermon|speech|oratio|homil|eulog|lecture|encomi|exhortation|memorial|consolatio",section_type): 
            num_sermons += 1 
            body_text.append(text)
            doc_text.append(f' SECTION{idx}^{section_type}')
        elif re.search(r"part|text|treatise|doctrine|book|conclusion|polemic|lamentation|essay|discourse|tract|criticism|response|animadversion|observation|disputation|allegations|extract|exposition|refutation|discourse|examination|comment|remarks|panegyric|censure|analysis|volume|articles|chapter|errata|typological_category|section",section_type): 
            body_text.append(text)
    with open(f"../assets/plain_all/{tcpID}.txt","w+") as file:
        file.writelines(" ".join(doc_text)) # write as one long string
    if len(body_text) > 0: 
        with open(f"../assets/plain_body/{tcpID}.txt","w+") as file:
            file.writelines(" ".join(body_text)) # write as one long string          
    return num_sermons

from tqdm import tqdm 
import pandas as pd 

if __name__ == "__main__": 
    tcpIDs = pd.read_csv(f"../assets/sermons.csv")['id']
    tcpIDs = list(tcpIDs)
    tcpIDs.extend(pd.read_csv("../assets/sermons_missing.csv")['id'])
    tcpIDs = sorted(tcpIDs)
    progress_bar = tqdm(tcpIDs)
    num_sermons = 0 
    for tcpID in progress_bar: 
        progress_bar.set_description(tcpID)
        fp = findTextTCP(tcpID)
        num_sermons += extract(tcpID, fp)
    print(f"{num_sermons} primary sections in these texts are originally oral.")
        