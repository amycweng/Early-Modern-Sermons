from lib.standardization import * 
from bs4 import BeautifulSoup, SoupStrainer
from nltk import sent_tokenize
class Sermon(): 
    def __init__(self,filepath):
        self.paragraphs, self.notes = self.parse_TCP_xml(filepath)
        print(f"Finished parsing")
        self.citations, self.outliers = {},{}
        self.cleaned_p = {} # cleaned paragraphs 
        self.cleaned_n = {} # cleaned notes 
        self.replaced = {} # replaced text 
        self.note_covering_sentIdx = {} 
        self.sentIdx = {}
        self.identify_citations(self.paragraphs, "P")
        self.identify_citations(self.notes, "N") 
        print(f"Finished extracting all citations")
        self.segment(self.cleaned_p, "P")
        self.segment(self.cleaned_n, "N")
        print(f"Finished segmenting sentences")
        # self.contexts()
        # print(self.citations, "\n\n", self.outliers)
        # for idx, c in self.citations.items(): 
        #     if "N" in idx: 
        #         print(c)
    
    def segment(self,cleaned,type): 
        for text_id, text in cleaned.items(): 
            # segment into individual sentences 
            sentences = sent_tokenize(text)
            if type == "P":
                # map each citation to the paragraph id and sentence index 
                for idx, sent in enumerate(sentences):
                    n_tags = re.findall(r"\(NOTE_(\d+:\d+_\d+)\)",sent)
                    for n in n_tags: 
                        self.note_covering_sentIdx[n] = idx
                    r_tags = re.findall(r"REF(\d+)",sent)
                    for r in r_tags: 
                        if text_id not in self.sentIdx: 
                            self.sentIdx[text_id] = {}
                        self.sentIdx[text_id][r] = idx  
                self.cleaned_p[text_id] = sentences 
            elif type == "N": 
                self.cleaned_n[text_id] = sentences
                for idx, sent in enumerate(sentences):
                    r_tags = re.findall(r"REF(\d+)",sent)
                    for r in r_tags: 
                        if text_id not in self.sentIdx: 
                            self.sentIdx[text_id] = {}
                        self.sentIdx[text_id][r] = idx

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
                # if curr_page != "53": continue
                notes = t.find_all("NOTE")
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
                c, o, cleaned,replaced = extract_citations(text)
                if type == "N": 
                    self.cleaned_n[f"{loc}_{type}_{idx}"] = cleaned 
                else: 
                    self.cleaned_p[f"{loc}_{type}_{idx}"] = cleaned 
                # print(c,o, text)
                if len(c) > 0: 
                    self.citations[f"{loc}_{type}_{idx}"] = c 
                    self.replaced[f"{loc}_{type}_{idx}"] = replaced
                if len(o) > 0: 
                    self.outliers[f"{loc}_{type}_{idx}"] = o 

    def contexts(self):
        self.info = {}
        for loc_type_idx in self.citations: 
            loc, type, idx = loc_type_idx.split("_")
            # print("----\n",c_list,"\n",self.replaced[loc_type_idx])
            preceding,succeeding = None, None
            if type == "N":
                page, p_idx = loc.split(":")
                clean_note = self.cleaned_n[loc_type_idx]
                sent_len = self.cleaned_p[f"{page}_P_{p_idx}"]
                sentidx = self.note_covering_sentIdx[f"{loc}_{idx}"]
                # print(f"NOTE_{loc}_{idx}", clean_note)
            else: 
                sentidx = self.sentIdx[loc_type_idx][idx]
                sent_len = self.cleaned_p[loc_type_idx]
            if sentidx > 0: 
                preceding = sentidx-1
            if sentidx < (len(sent_len)-1):
                succeeding = sentidx+1
            self.info[loc_type_idx] = (sentidx, preceding, succeeding)
            # print(info[loc_type_idx])

def write_outputs(outpath,fields,outputs): 
    if len(outputs) > 0: 
        outfile = open(outpath,"w+")
        writer = csv.DictWriter(outfile, fieldnames=fields)
        writer.writeheader()
        for dict in outputs: 
            writer.writerow(dict)
        outfile.close()


SFIELDS = ["tcp_id", "id", "page","p_idx", "s_idx", "text"]
    # PRIMARY KEY (tcpid, id)
NFIELDS = ["tcp_id","n_id","id","n_idx","text"]
    # PRIMARY KEY for notes (tcpid, n_id)
    # FOREIGN KEY (tcpid, id) on sentences 
CFIELDS = ["tcp_id", "c_id", "c_group","citation"]  # individual citations
    # PRIMARY KEY (tcp_id, c_id)
    # FOREIGN KEY (tcpid, c_group) on c_locations
LFIELDS = ["tcp_id", "group", "id","type","n_id","original"]
    # PRIMARY and FOREIGN KEY (tcp_id, c_group)
    # FOREIGN KEY (tcp_id, id) on sentences 
    # FOREIGN KEY (tcp_id, n_id) on notes 
OFIELDS = ["tcp_id", "group","id","type","n_id","original"]

def process(filename, tcpids):
    sentences, notes, citations, c_locations, outliers = [],[],[],[],[]
    for tcpID in tcpids: 
        sent_dict = {}
        note_dict = {}
        filepath = f'/Users/amycweng/Digital Humanities/sermonsTCP/{tcpID}.P4.xml'
        S = Sermon(filepath)
        print(f"Finished processing {tcpID}")
        id = 0 
        for loc_type_idx,sents in S.cleaned_p.items(): 
            loc, type, idx = loc_type_idx.split("_")
            for i, sent in enumerate(sents): 
                sentences.append({"tcp_id":tcpID, "id":id, "page":loc,"p_idx":idx, "s_idx":i, "text":sent})
                sent_dict[(loc,idx,i)] = id  # (page num, paragraph index, sentence index)
                id += 1 
        
        id = 0 
        for loc_type_idx,sents in S.cleaned_n.items(): 
            loc, type, idx = loc_type_idx.split("_")
            page, p_idx = loc.split(":")
            for i, sent in enumerate(sents): 
                s_idx = S.note_covering_sentIdx[f"{loc}_{idx}"]
                notes.append({"tcp_id":tcpID, "n_id": id, "id": sent_dict[(page,p_idx,s_idx)], "n_idx":i, "text":sent})
                # n_id is index within document 
                # n_idx is index within the sentences of the entire marginal note 
                note_dict[(loc,idx,i)] = id  # (page#:p_idx, index within paragraph, n_idx)
                id += 1 

        id = 0 
        c_id = 0
        for loc_type_idx, c_dict in S.citations.items(): 
            loc, type, idx = loc_type_idx.split("_")
            for ref, c_list in c_dict.items():
                n_id = None
                if type == "N":
                    page, p_idx = loc.split(":")
                    s_idx = S.sentIdx[loc_type_idx][f"{ref}"]
                    n_id = note_dict[(loc,idx,s_idx)]
                else: 
                    page, p_idx = loc, idx 
                    s_idx = S.sentIdx[loc_type_idx][f"{ref}"]
                covering_id = sent_dict[(page,p_idx,s_idx)]
                c_locations.append({"tcp_id":tcpID, "group": id, "id":covering_id,"type":type,"n_id":n_id,"original":S.replaced[loc_type_idx][ref]})
                # print(c_locations[-1])
                for c in c_list:
                    citations.append({"tcp_id":tcpID, "c_id": c_id, "c_group":id,"citation":c}) 
                    # print(citations[-1])
                    c_id += 1 
                id += 1 
        

        id = 0 
        for loc_type_idx, c_dict in S.outliers.items(): 
            loc, type, idx = loc_type_idx.split("_")
            for ref, c_list in c_dict.items():
                n_id = None
                if type == "N":
                    page, p_idx = loc.split(":")
                    s_idx = S.sentIdx[loc_type_idx][f"{ref}"]
                    n_id = note_dict[(loc,idx,s_idx)]
                else: 
                    page, p_idx = loc, idx 
                    s_idx = S.sentIdx[loc_type_idx][f"{ref}"]
                covering_id = sent_dict[(page,p_idx,s_idx)]
                outliers.append({"tcp_id":tcpID, "group": id, "id":covering_id,"type":type,"n_id":n_id,"original":S.outliers[loc_type_idx]})
                id += 1 

    out_body = f"../outputs/sentences_body/{filename}.csv"
    out_margins = f"../outputs/sentences_margin/{filename}.csv"
    write_outputs(out_body, SFIELDS,sentences)
    write_outputs(out_margins, NFIELDS, notes)
    out_citations = f"../outputs/citations/{filename}.csv"
    out_clocations = f"../outputs/c_locations/{filename}.csv"
    out_outliers = f"../outputs/outliers/{filename}.csv"
    write_outputs(out_clocations, LFIELDS, c_locations)
    write_outputs(out_citations, CFIELDS, citations)
    write_outputs(out_outliers, OFIELDS, outliers)


# groups = {"A1":["A19277"],"A4":["A40728"]}

# for filename, tcpids in groups.items(): 
#     process(filename, tcpids)