import csv,os,re
from collections import Counter,defaultdict 
from bs4 import BeautifulSoup, SoupStrainer
from nltk.tokenize import sent_tokenize

info = {}
with open('../assets/sermons.csv', 'r') as file:          
    sermons = csv.reader(file, delimiter=',')
    for idx, s in enumerate(sermons): 
        if idx == 0: continue
        info[s[0]] = {'title':s[3],'author':s[4],'pubplace': s[6],'subject_headings':s[7],'date':s[8]}

sources = {}
with open('../assets/sermons_marginalia.csv', 'r') as file:          
    sermons = csv.reader(file, delimiter=',')
    for idx, s in enumerate(sermons): 
        if idx == 0: continue
        sources[idx] = (s[2],s[3]) # (sourceline, sourcepos within line)
        
def get_citations(filepath): 
    citations = defaultdict(list)
    with open(filepath, 'r') as file:          
        data = csv.reader(file, delimiter=',')
        for idx, s in enumerate(data): 
            if idx == 0: continue
            if len(s[2]) == 0: continue # no citations 
            citations[s[1]].append((s[2],s[0])) # (citations, original index)
    return citations 

def find_target(target,citations):
    hits = []
    positions = {}
    for tcpID, c_list in citations.items():
        positions[tcpID] = [] 
        for cited in c_list:
            pos = cited[1]
            cited = cited[0].split("; ")
            for c in cited:
                if target in c: 
                    hits.append(tcpID)
                    positions[tcpID].append(pos)
    return Counter(hits),positions

# get file path to TCP XML 
TCP = '/Users/amycweng/Digital Humanities/TCP'

def findTextTCP(id):
    if re.match('B1|B4',id[0:2]):
        path = f'{TCP}/P2{id[0:2]}/{id}.P4.xml'
    else: 
        if f'{id}.P4.xml' in os.listdir(f'{TCP}/P1{id[0:2]}'):
            path = f'{TCP}/P1{id[0:2]}/{id}.P4.xml'
        elif f'{id}.P4.xml' in os.listdir(f'{TCP}/P2{id[0:2]}'): 
            path = f'{TCP}/P2{id[0:2]}/{id}.P4.xml'
    return path 


# get contexts for marginal citations 
def context(tcpID, positions):
    filepath = findTextTCP(tcpID)
    find_pos = {int(sources[int(k)][0]):[] for k in positions[tcpID]}
    for k in positions[tcpID]: 
        find_pos[int((sources[int(k)][0]))].append(int(sources[int(k)][1]))
    # read the input XML file 
    with open(filepath,'r') as file: 
        data = file.read()
    # use soupstrainer to only parse the main body
    tag = SoupStrainer("div1")
    # create a parsed tree, i.e., soup, of the body text using an html parser, which keeps track of line numbers
    soup = BeautifulSoup(data,features="html.parser",parse_only=tag)
    # iterate through every marginal note tag of this file 
    notes = soup.find_all('note')
    notes_contexts = defaultdict(list)
    for note in notes: 
        if note.get("place") == "marg":
            if note.sourceline in find_pos:
                if note.sourcepos in find_pos[note.sourceline]:
                    parent = note.parent  
                    parent_text = re.sub(re.escape(note.text), "<CITATION>", parent.text)
                    parent_text = re.sub(r"[\s+\n]"," ", parent_text)
                    sentences = sent_tokenize(parent_text)
                    for s in sentences: 
                        if "<CITATION>" in s: 
                            if note.sourceline not in notes_contexts: 
                                notes_contexts[note.sourceline] = {}
                            notes_contexts[note.sourceline][note.sourcepos] = s 
                    
    return notes_contexts