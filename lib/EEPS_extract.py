from bs4 import BeautifulSoup, SoupStrainer
import re,sys,os
sys.path.append('../') 
from lib.dictionaries.sermon_annotations import * 
TCP = '/Users/amycweng/DH/TCP'

wanted_sections = [
    'text','treatise','part','tract','lecture','lectures','chapter','book',
    'discourse','commentary','doctrine','application','conclusion',
    'exposition','body_of_text','homily','memorial','funeral_sermon',
    'extracts_from_sermon','oration_and_sermon','collection_of_lectures',
    'collection_of_sermons_on_isaiah','collection_of_sermons_on_haggai',
    'whit_sunday_sermons','ordination_sermons','penitential_sermons_preached_at_wells',
    'sermon_extract','application_of_sermon','summary_of_sermons',
    'two_sermons','greek_text_bound_with_sermon','collection_of_sermons','visitation_sermon',
]
wanted_sections = {s:None for s in wanted_sections}
def isSermon(section_name): 
    if re.search(r"^sermon",section_name): 
        return True 
    return False 

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
    
    contents = soup.find_all(['DIV1', 'DIV2', 'DIV3', 'DIV4', 'DIV5', 'DIV6', 'DIV7'])

    div_text = []
    num_sermons = 0
    # need to place delimiters between each sermon, marginal note, and page
    p_idx = 0 
    section_count = 0 
    for div in contents:
        toAdd = False 
        section_name = div.name 
        section_idx = "" 
        if "N" in div.attrs: 
            section_idx = div["N"]
        section_type = div.get("TYPE").lower().split(" ")
        section_type = "_".join(section_type)

        if tcpID in custom_subsections: 
            if section_name in custom_subsections[tcpID]:
                if (section_type,section_idx) == custom_subsections[tcpID][section_name]: 
                    toAdd = True  
        elif tcpID in sermon_subsections: 
            if section_type == "sermon": 
                toAdd = True 
        elif section_name == "DIV1":
            if tcpID in custom: 
                annotated = custom[tcpID]
                if isinstance(annotated,str): 
                    annotated = [annotated]
                if section_type in custom[tcpID]: 
                    toAdd = True
            elif tcpID in custom_exceptions: 
                if section_type in custom_exceptions[tcpID]:
                    if section_count in custom_exceptions[tcpID][section_type]: 
                        toAdd = True 
                    section_count += 1
            else: 
                if isSermon(section_type): 
                    toAdd = True  
                elif section_type in wanted_sections: 
                    if tcpID not in sermons: 
                        toAdd = True 
        
        if toAdd: 
            num_sermons += 1 
            text = []
            # text = re.sub(r"[^\x00-\x7F]","",str(div.text))
            # text = re.sub(r"[\{\}\[\]]","",text)
            for page_info in div.find_all(['PB']):
                if "N" in page_info.attrs: 
                    page = page_info["N"]
                    page = f' PAGE{page} '
                else: 
                    page = page_info["REF"]
                    page = f' PAGEIMAGE{page} '
                page_info.string = page

            n_idx = 0 # note's relative position within div
            for t in div.find_all(['P']):
                for gap in t.find_all("GAP"):
                    if gap["DESC"] == "foreign": 
                        gap.string = " NONLATINALPHABET " # 〈 in non-Latin alphabet 〉
                    elif gap["DESC"] == "missing":
                        gap.string = "^".join(gap["EXTENT"].upper().split(" ")) + "^MISSING"
                    elif gap["DESC"] == "illegible": 
                        if "DISP" in gap.attrs: 
                            disp = gap["DISP"]
                            # disp = re.sub("•","\^",disp) # illegible letters 
                            # disp = re.sub("◊","\*",disp) # illegible words 
                            gap.string = gap["DISP"]
                for italics in t.find_all("HI"):
                    italics.string = f" STARTITALICS {italics.text} ENDITALICS "
                for item in t.find_all(["NOTE"]):
                    if item.name == "NOTE":
                        # add note delimiters 
                        item.string = f" STARTNOTE{n_idx} {item.text} ENDNOTE{n_idx} "
                        n_idx += 1 
                t.string = f" STARTPARAGRAPH{p_idx} {t.text} "
                p_idx += 1 
                

            for child in div.children:
                if child.name in ['DIV1', 'DIV2', 'DIV3', 'DIV4', 'DIV5', 'DIV6', 'DIV7']:
                    ss_type = "_".join(child.get("TYPE").lower().split(" "))
                    ss_N = ""
                    if "N" in child.attrs: 
                        ss_N = child["N"]
                    text.append(f" {child.name}^{ss_type}^{ss_N} " + child.get_text() + " ")
                
                else: 
                    text.append(" " + child.get_text() + " ")
            text = f" {f' {section_name}^{section_type}^{section_idx}'} {' '.join(text).strip()} "
            if tcpID in custom_pages: 
                position = text.find(custom_pages[tcpID])
                preceding = re.findall(r'(\bDIV[\d+\_\w+\^]+)\s', text[:position])
                text = " ".join(preceding) + " " + text[position:]
            div_text.append(text)
        else: 
            div_text.append(f' {section_name}^{section_type}^{section_idx}')
    
    with open(f"../assets/plain_body/{tcpID}.txt","w+") as file:
        div_text = re.sub(r"\s+"," "," ".join(div_text).strip())
        file.writelines(div_text) # write as one long string         
    return num_sermons

from tqdm import tqdm 
import pandas as pd 

if __name__ == "__main__": 
    # tcpIDs = ["A80317"] # ["A50253", "A92163","A02181","A22562", "A42583"] #
    
    # tcpIDs = custom_subsections.keys() # 3  
    # tcpIDs = custom_exceptions.keys() # 18 
    # tcpIDs = custom_pages.keys() # 2 
    # tcpIDs = sorted(custom.keys()) # 638
    # tcpIDs = sorted(sermons_missing.keys()) # 2658+39
    # tcpIDs = sorted(sermons.keys()) # 10,071
    tcpIDs = sermon_subsections.keys() # 2413
    # tcpIDs = ['A13812', 'A21069', 'A43399', 'A44308', 'A44843', 'A46371', 'A48172', 'A58328']
    
    
    progress_bar = tqdm(tcpIDs)
    num_sermons = 0 
    missing = []
    for idx, tcpID in enumerate(progress_bar): 
        progress_bar.set_description(f"{tcpID}, {num_sermons} so far")
        fp = findTextTCP(tcpID)
        num = extract(tcpID, fp)
        if num == 0: 
            missing.append(tcpID)
        num_sermons += num
    print(missing)
    print(f"{num_sermons} sermon-related sections")
        