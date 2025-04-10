from bs4 import BeautifulSoup, SoupStrainer
import re,sys,os
sys.path.append('../') 
from lib.dictionaries.sermon_annotations import * 
from EEPS_helper import * 

def format_name(item):
    item = "\^".join(item.split(" "))
    item = re.sub(r"[^\d\^\\\'\w1]","\^",item)
    return item 

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
    last_added_section = None 
    for div in contents:
        toAdd = False 
        
        section_name = div.name 
        section_note = "" 
        if "N" in div.attrs: 
            section_note = div["N"]
            section_note = format_name(section_note)
        section_type = div.get("TYPE").lower()
        section_type_output = format_name(section_type) 
        section_type = "_".join(section_type.split(" "))

        if tcpID in custom_subsections: 
            if section_name in custom_subsections[tcpID]:
                if (section_type,section_note) == custom_subsections[tcpID][section_name]: 
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
            last_added_section = section_name
            num_sermons += 1 
            text = []
            # text = re.sub(r"[^\x00-\x7F]","",str(div.text))
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
                            if "page" in disp: 
                                disp = re.sub(" ","^",disp)
                                disp = disp+"^illegible"
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
                    ss_type = child.get("TYPE").lower()
                    if re.search("table|errata|index",ss_type): 
                        continue 
                    ss_type = format_name(ss_type)
                    ss_N = ""
                    if "N" in child.attrs: 
                        ss_N = child["N"]
                        ss_N = format_name(ss_N)
                    text.append(f" {child.name}^{ss_type}^{ss_N} " + child.get_text() + " ")
                
                else: 
                    text.append(" " + child.get_text() + " ")
        
            text = f" {f' {section_name}^{section_type_output}^{section_note}'} {' '.join(text).strip()} "
            text = re.sub(r"|","",text)
            if tcpID in custom_pages: 
                position = text.find(custom_pages[tcpID])
                preceding = re.findall(r'(\bDIV[\d+\_\w+\^]+)\s', text[:position])
                text = " ".join(preceding) + " " + text[position:]
            div_text.append(text)
        else: 
            if last_added_section is None or (int(last_added_section[-1]) > int(section_name[-1])): 
                div_text.append(f' {section_name}^{section_type_output}^{section_note} ')
    
    with open(f"../assets/plain_body/{tcpID}.txt","w+") as file:
        div_text = re.sub(r"\s+"," "," ".join(div_text).strip())
        file.writelines(div_text) # write as one long string         
    return num_sermons

from tqdm import tqdm 
import pandas as pd 

if __name__ == "__main__": 

    all_sermons = list(sermons.keys())
    all_sermons.extend(sermons_missing.keys())
    tcpIDs = sorted(all_sermons) 
    already_extracted = os.listdir('../assets/plain_body')
    already_extracted = {k.split(".txt")[0]:None for k in already_extracted}

    progress_bar = tqdm([tcpID for tcpID in tcpIDs if tcpID not in already_extracted]) 
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
        