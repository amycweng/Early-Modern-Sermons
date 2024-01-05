from bs4 import BeautifulSoup,SoupStrainer
import re,ast,os
import pandas as pd
'''
This is an adaptation of the text extraction code in the clean.ipynb file from the ECBC Data+ Team's github: 
https://github.com/amycweng/ECBC-Data-2022/blob/main/2b)%20stageTwo/clean.ipynb 
'''

def text(soup):
    '''Extracting body texts from TCP'''
    text_list = []
    for part in soup.find_all('p'):  
        text = str(part)
        pattern1 = re.compile(r'</seg>', re.DOTALL)
        text = pattern1.sub('',text)
        pattern2 = re.compile(r'</hi>|<hi>', re.DOTALL)
        text = pattern2.sub(' ',text)
        pattern3 = re.compile(r'<note(.*?)place="marg">(.*?)</note>', re.DOTALL)
        text = pattern3.sub(' ',text)
        pattern4 = re.compile(r'<.*?>|\n', re.DOTALL)
        text = pattern4.sub(' ',text)
        text = text.strip()
        text_list.append(text)   
    return ' '.join(text_list)

def cleanText(text):  
    '''Text cleaning function to remove all non-alphabetical characters from the text'''  
    dashes = text.replace('-',' ')
    tokens = [x for x in re.sub(r'[^a-zA-Z\s\u25CF]','', dashes).split(' ') if x != '' and len(x) > 1]
    tokens = ' '.join(tokens)
    tokens = tokens.replace('  ',' ')
    return tokens
    
def getLemmaDict(path):
    '''
    Args: 
        path: File path to your lemmatization & standardization dictionary in TXT format 
                The TXT file should only contain a dictionary like this: {'fravncis':'francis','frauncis':'francis'} 
                See https://github.com/amycweng/ECBC-Data-2022/blob/main/2b)%20stageTwo/lemmas.txt as an example. 
    '''
    if 'None' in path: 
        return None
    if 'Default' in path or 'default' in path:
        path = 'Standardization_Files/lemmas.txt'
    with open(path) as f:
        data = f.read()
    lemmaDict = ast.literal_eval(data)
    return lemmaDict

lemmaDict = getLemmaDict(input(f'Enter the path to your own standardizer dictionary, write Default if you would like to use ours, or write None: '))

def replaceTextLemma(textString,lemmaDict):
    if lemmaDict is not None: 
        for key,value in zip(list(lemmaDict.keys()), list(lemmaDict.values())):
            textString = re.sub(rf' {key} ', f' {value} ', textString)
    return textString

def findTextTCP(id):
    if re.match('B1|B4',id[0:2]):
        path = f'{TCP}/P2{id[0:2]}/{id}.P4.xml'
    else: 
        if f'{id}.P4.xml' in os.listdir(f'{TCP}/P1{id[0:2]}'):
            path = f'{TCP}/P1{id[0:2]}/{id}.P4.xml'
        elif f'{id}.P4.xml' in os.listdir(f'{TCP}/P2{id[0:2]}'): 
            path = f'{TCP}/P2{id[0:2]}/{id}.P4.xml'
    return path 

EP = '/Users/amycweng/Digital Humanities/eebotcp/texts'
EP = input('Enter the path to a folder containing EP texts or write None: ')
# Each subfolder must be named like this: "P1A0" for Phase 1 A0 texts
# Let all phase 1 and phase 2 folders be located under the same directory 
# e.g.,  '.../TCP/P1A0' and '.../TCP/P2A5'
TCP = '/Users/amycweng/Digital Humanities/TCP'
# TCP = input('Enter the path to a folder containing all TCP texts or write None: ')

underscores = []
def findText(id,getActs=False):
    '''
    Args: 
        id: TCP ID for a single text 
        getActs: Boolean value (True or False) for whether you want to extract each act of a play individually 
    '''
    foundEP = False
    for file in os.listdir(f'{EP}/{id[0:3]}'):
        if id in file: 
            foundEP = True                 
            if '_' in file and not getActs:
                trueID = file.split('.')[0]
                if trueID in underscores: path = f'{EP}/{id[0:3]}/{file}'
                else: 
                    path = ''
                    underscores.append(trueID)
            else: 
                path = f'{EP}/{id[0:3]}/{file}'    
    if foundEP:
        return path, 'EP'
    else: 
        # Not in EP, so extract from TCP
        if re.match('B1|B4',id[0:2]):
            path = f'{TCP}/P2{id[0:2]}/{id}.P4.xml'
        else: 
            if f'{id}.P4.xml' in os.listdir(f'{TCP}/P1{id[0:2]}'):
                path = f'{TCP}/P1{id[0:2]}/{id}.P4.xml'
            elif f'{id}.P4.xml' in os.listdir(f'{TCP}/P2{id[0:2]}'): 
                path = f'{TCP}/P2{id[0:2]}/{id}.P4.xml'
        return path, 'TCP'

def textEP(soup):
    '''
    Gets the body of the text file into string format.
    -----------------------------------
    Does not grab any text in the tag <front> which contains div tags such as ['title_page', 'dedication',
    'to_the_reader', 'list'...] that are not part of the main text. 
    Does not grab any text in the tag <back> which contains div tags such as ['errata', 'index', 
    'supplied_by_editor', ...] that are not part of the main text. 
    Does not grab any text under the <table>, <note>, <speaker>, <foreign>, <pc>, <head> or <stage> tags
    Does not grab any text under div type 'coat_of_arms' or attribute 'lat'

    '''
    text_list = []
    for sibling in soup.find_all('w'):
        parent_name = [parent.name for parent in sibling.parents]
        parent_attrs = [parent.attrs for parent in sibling.parents]
        divType = [ats['type'] for ats in parent_attrs if 'type' in ats.keys() and ats['type'] == 'coat_of_arms']
        divLat = [ats['xml:lang'] for ats in parent_attrs if 'xml:lang' in ats.keys() and ats['xml:lang'] == 'lat']
        ignoreTags = ['front', 'table', 'back','foreign','note','speaker','head','stage','pc']
        if not any(x in parent_name for x in ignoreTags) and 'coat_of_arms' not in divType and 'lat' not in divLat and re.search('lemma',str(sibling)) and str(sibling['lemma']) != 'n/a':
            text_list.append(sibling['lemma'])
    return ' '.join(text_list)

def convert(tcpIDs,outputfolder):
    '''
    Args: 
        tcpIDs: List of TCP IDs 
        outputfolder: path to the folder where you want your output TXT files to be located 
    '''
    if EP is None: 
        return "No folder of EP texts has been provided."
    if TCP is None: 
        return 'No folder of TCP texts has been provided.'
    count = 0
    for id in tcpIDs:
        path,source = findText(id,False)
        if path == '': continue
        with open(path,'r') as file: 
            data = file.read()
        bodyTag = SoupStrainer("body")
        soup = BeautifulSoup(data,parse_only=bodyTag,features='html.parser')
        if source == 'TCP': 
            print(f'{id} is not in EP')
            bodytext = text(soup).lower()
        if source == 'EP': 
            bodytext = textEP(soup).lower()
            bodytext = re.sub('●','^',bodytext)
        with open(f'{outputfolder}/{id}.txt', 'w+') as file:
            cleaned = cleanText(bodytext)
            bodytext = replaceTextLemma(cleaned,lemmaDict)
            file.write(bodytext) 
        count += 1 
        if not count % 10: print(f'processed {count}')
    print(f'Processed {count} in total')

def getIDs(csv_file): 
    '''
    Args: 
        csv_file: CSV file of relevant metadata (e.g., all the TCP info for a particular author)
                    See https://github.com/amycweng/Early-Modern-London/tree/main/Relevant_Metadata for examples 
    '''
    csv_data = pd.read_csv(csv_file)
    return [ _ for _ in csv_data['id']]


''' 
Separately extract each act of a play as a TXT file. 

NOTE: For EP XML files that contain only one play  
'''
def writeToFile(bodytext,folder,tcpID,head):
    with open(f'{folder}/{tcpID}_{head}.txt', 'w+') as file:
        bodytext = replaceTextLemma(bodytext,lemmaDict)
        cleaned = cleanText(bodytext)
        cleaned = cleaned.replace('\n',' ')
        file.write(f'{cleaned}') 

def extractActs(tcpIDs,outputfolder):
    '''
    Args: 
        tcpIDs: list of TCP IDs for XMLs of plays that you want to extract each individual act for 
        outputfolder: path for the folder where you want your output TXT files to be located
    '''
    getActs = True
    for tcpID in tcpIDs: 
        path = findText(tcpID,getActs)[0]
        with open(path,'r') as file: 
            data = file.read()
        targetTag = SoupStrainer("div",attrs={"type":"act"})
        soup = BeautifulSoup(data,parse_only=targetTag,features='html.parser')
        acts = soup.find_all('div',attrs={"type":"act"})
        for idx,act in enumerate(acts): 
            head = f'Act {idx+1}' 
            bodytext = textEP(act).lower()
            writeToFile(bodytext,outputfolder,tcpID,head)

''' 
Extract a particular play from an xml version of an anthology, 
    e.g., A53060 (Playes written by the thrice noble, illustrious and excellent princess, the Lady Marchioness of Newcastle.)
EP breaks most anthologies into indiviudal XML files for each work, but there are exceptions. 

IMPORTANT: The trick is to manually identify the section of the XML
and then add the <play>... </play> tag to the beginning and end of the section. 
--- you must modify the xml file for this to work 
'''
def getPlayFromAnthology(outputfolder,tcpID,title,source,filepath,getActs): 
    '''
    Args: 
        outputfolder: path for the folder where you want your output TXT files to be located
        tcpID: the TCP ID of the EP anthology you want to extract a play from 
        title: the exact title of the section you want to extract 
        source: EP or TCP 
        filepath: the path to the modified EP XML file 
        getActs: Boolean True/False value whether you want to extract each act of the play into individual TXT files
    '''
    with open(filepath,'r') as file: 
        data = file.read()
    targetTag = SoupStrainer("play")
    soup = BeautifulSoup(data,parse_only=targetTag,features='html.parser')
    if getActs: 
        acts = soup.find_all('div',attrs={"type":"act"})
        for idx,act in enumerate(acts): 
            head = f'{title}_Act {idx+1}' 
            if source == 'EP': 
                bodytext = textEP(act).lower()
            else: 
                bodytext = text(act).lower()
            writeToFile(bodytext,outputfolder,tcpID,head)
    else: 
        if source == 'EP': 
                bodytext = textEP(act).lower()
        else: 
            bodytext = text(act).lower()
        writeToFile(bodytext,outputfolder,tcpID,title)

''' 
Extract a particular English section from a TCP document with many languages and/or works 

NOTE: Once you have found your target section under a tag in a TCP xml file, 
move the </HEAD> concluding tag to the bottom of the section. 
That way, only the target section has the associated text, not just the heading title 

Outputs the body text of a particular section to a TXT file. 
Names each TXT file by the {tcpID}_{section heading}
'''
def getParticularEnglishSectionTCP(head, tcpID, tcpPath, folder):
    '''
    Args: 
        head: The exact name of the section you want to extract, e.g., 'The Conclusion of the Parlement of Pratlers.'
        tcpID: The TCP ID of the text 
        tcpPath: File path
        folder: Folder for the output files 
    '''
    with open(tcpPath,'r') as file: 
        data = file.read()
    targetTag = SoupStrainer("div3",attrs={"lang": "eng"})
    soup = BeautifulSoup(data,parse_only=targetTag,features='html.parser')
    bodytext = partialTextTCP(soup,head).lower()
    writeToFile(bodytext,folder,tcpID,head)

def partialTextTCP(soup,target):
    text_list = []
    headings = soup.find_all('head')
    for tag in headings:
        children = tag.children
        if target in tag.text: 
            for child in children:
                text_list.append(child.text.strip())
    return ' '.join(text_list[1:])