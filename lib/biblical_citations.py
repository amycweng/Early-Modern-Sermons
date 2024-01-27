from standardization import * 
from bs4 import BeautifulSoup, SoupStrainer
from nltk import sent_tokenize
class Biblical_Citations(): 
    def __init__(self,filepath):
        self.paragraphs, self.notes = self.parse_TCP_xml(filepath)
        self.citations, self.outliers = {},{}
        self.cleaned = {} # cleaned text 
        self.identify_citations(self.paragraphs, "P")
        self.identify_citations(self.notes, "N")
        
        for text_id, text in self.cleaned.items(): 
            self.cleaned[text_id] = sent_tokenize(text)
        
        print(self.citations, "\n\n", self.outliers)
        # for idx, c in self.citations.items(): 
        #     if "N" in idx: 
        #         print(c)
    
    def parse_TCP_xml(self, filepath):
        # read the input XML file 
        with open(filepath,'r') as file: 
            data = file.read()
        # use soupstrainer to only parse the main body
        tag = SoupStrainer("DIV1",attrs={"TYPE":"sermon"})
        # create a parsed tree, i.e., soup, of the body text using an html parser, which keeps track of line numbers
        self.soup = BeautifulSoup(data,features="xml",parse_only=tag)
        paragraphs = {} # page number to dict mapping paragraph_id to paragraph text 
        notes_dict = {} # paragraph idx to dict mapping note_id to note text 
        curr_page, p_idx = -1, 0 
        count = 0 
        for t in self.soup.find_all(['PB','P']):
            # page number 
            if t.name == "PB" and "N" in t.attrs: 
                curr_page = t["N"]
                paragraphs[curr_page] = {}
                p_idx = 0 
            elif t.name == "P": # paragraph 
                notes = t.find_all("NOTE")
                # if curr_page != '49': continue
                # print(t.text)
                if notes: # there are marginal notes in this paragraph
                    notes_dict[f"{curr_page}:{p_idx}"] = {}
                    for idx, note in enumerate(notes): 
                        note_id = f" (NOTE_{curr_page}:{p_idx}_{idx}) "
                        # map the placeholder note_id to note's text 
                        notes_dict[f"{curr_page}:{p_idx}"][idx] = note.text
                        # replace the note's text with the placeholder  
                        note.string = note_id
                # add paragraph to dictionary 
                paragraphs[curr_page][p_idx] = t.text
                p_idx += 1 
        return paragraphs, notes_dict
    
    def identify_citations(self,text_dict,type):
        for loc, info in text_dict.items():
            for idx, text in info.items(): 
                if type != "N": break
                if f"{loc}_{type}_{idx}" != "84:0_N_2": continue
                # print(sent_tokenize(text))
                c, o, cleaned = extract_citations(text)
                self.cleaned[f"{loc}_{type}"] = cleaned 
                # print(c,o, text)
                if len(c) > 0: 
                    self.citations[f"{loc}_{type}_{idx}"] = c 
                if len(o) > 0: 
                    self.outliers[f"{loc}_{type}_{idx}"] = o 

    def contexts(self):
        note, cleaned,following,preceding = '','','',''
        for loc_type_idx, c_list in self.citations.items(): 
            loc, type, idx = loc_type_idx.split("_")
            clean = self.cleaned[f"{loc}_P"]
            if type == "N":
                page, p_idx = loc.split(":")
                p_idx = int(p_idx)
                n_idx = int(idx)
                note = self.notes[loc][n_idx]
                paragraph = self.paragraphs[page][p_idx]
                # for i, sent in enumerate(clean): 
                #     if f"(NOTE_" in sent: 
                #         cleaned = sent 
                #         if (i+1) < len(clean):
                #             following = clean[i+1]
                #         if (i-1) >= 0: 
                #             preceding = clean[i-1]
            else: 
                for i, sent in enumerate(clean): 
                    if f"(REF{idx})" in sent: 
                        cleaned = sent
                        if (i+1) < len(clean):
                            following = clean[i+1]
                        if (i-1) >= 0: 
                            preceding = clean[i-1]
            if type == "N": continue
            
            print("----\n",loc_type_idx, c_list,'\n',note)
            print(preceding, '\n', cleaned, '\n', following)

if __name__ == "__main__":
    filepath = '/Users/amycweng/Digital Humanities/sermonsTCP/A19277.P4.xml'
    citations = Biblical_Citations(filepath)
    citations.contexts()
    # tcp_id = filepath.split("/")[-1].split(".")[0]
