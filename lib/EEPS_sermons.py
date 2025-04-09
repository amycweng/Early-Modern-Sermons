import json,csv
import sys,re
import pandas as pd 
sys.path.append('../')
import os, math
# standardized with GPT 3.5 
standardizer = {}
for fp in os.listdir('../assets/vocab'):
    if "standard" not in fp: continue
    with open(f"../assets/vocab/{fp}") as file: 
        new_standard = json.load(file)
        standardizer.update({k.lower():v for k,v in new_standard.items() if len(k) > 1 and len(v) > 1 and not re.search("\d",k) and (len(re.findall("\^",k)) < math.floor(len(k)/2))})


with open('../assets/corpora.json','r') as file: 
        corpora = json.load(file)

def combine_punc_with_text(segment): 
    segment = re.sub(r'\s+([,.?!;:)])', r'\1', segment)
    segment = re.sub(r'([(])\s+', r'\1', segment) 
    segment = re.sub(r"\s+"," ",segment)
    start_it = re.findall(r"\<i\>",segment)
    end_it = re.findall(r"\<\/i\>",segment)
    if len(start_it) > len(end_it):
        segment = segment + " </i>"
    elif len(start_it) < len(end_it):
        segment = "<i> " + segment 
    return segment

class Sermons():
    def __init__(self, era, prefix,texts,marginalia):
        self.era = era
        self.prefix = prefix
        self.sent_id = [] # tuples of ((tcpID, chunk idx, location), subchunk idx) representing the subchunk's ID
        self.standard = [] # subchunk strings that are standardized
        self.fw_subchunks = {} # IDs of subchunks with more than three foreign words
        self.tokens = [] # subchunk strings that are tokenized

        self.get_texts(texts)
        self.get_marginalia(marginalia)
        self.get_indices()

    def get_indices(self):
        self.sent_id_to_idx = {x:idx for idx, x in enumerate(self.sent_id)}

    def get_marginalia(self,marginalia):
        new_marginalia = {}
        note_id = 0 # id of the note within the current sentence chunk
        curr_s = 0 # index of the current sentence chunk
        for tcpID, items in marginalia.items():
            if tcpID not in new_marginalia:
                new_marginalia[tcpID] = {}
                note_id = 0
            for item in items:
              s_idx = item[0]
              if (s_idx,note_id) not in new_marginalia[tcpID]:
                  if s_idx != curr_s:
                      note_id = 0
                  else:
                      note_id += 1
                  new_marginalia[tcpID][(s_idx, note_id)] = []
              else:
                  note_id += 1

              if s_idx != curr_s: curr_s = s_idx
              new_marginalia[tcpID][(s_idx, note_id)] = item[-1]
        marginalia = new_marginalia
        if len(marginalia) > 0: 
            self.create_corpus(marginalia,True)
            # print('Processed marginalia')

    def get_texts(self,texts):
        self.create_corpus(texts)
        # print('Processed texts')

    def create_corpus(self, data,is_margin=False):
      def check_foreign(fw): # at least three consecutive foreign words 
        consec = 1
        for i in range(len(fw) - 1):
            if fw[i] + 1 == fw[i + 1]:
                consec += 1
                if consec == 3:
                    return True
            else:
                consec = 1
        return False
      
      for tcpID, items in data.items():    
      
          for s_idx, encodings in items.items():
              current = []
              tokens = []
              part_id = 0

              if is_margin:
                  s_idx, note_id = s_idx
                  s_idx = int(s_idx)
                  sid = (tcpID,s_idx,note_id)
              else:
                  s_idx = int(s_idx)
                  sid = (tcpID,s_idx,-1)


              fw = [] # contains indices of the foreign tokens
              fw_idx = 0  

              for idx, x in enumerate(encodings):
                  segment = False

                  token, pos, standard_spelling = x[0], x[1], x[2]
                  if len(token) == 0: continue
                  if len(standard_spelling) == 0: continue
                  tokens.append(token)
                  
                  # standardize spelling 
                  if token != "<NOTE>" and token != "NONLATINALPHABET" and not re.search("\<i\>|\<\/i\>",token): 
                    all_caps, caps = False, False
                    
                    if standard_spelling.isupper() and len(standard_spelling.strip(".")) > 1: # all uppercase 
                        all_caps = True 
                    elif standard_spelling[0].isupper(): # capitalized  
                        caps = True 
                    # strip ending punctuation 
                    if token.lower() == "an" and standard_spelling.lower() == "and": 
                        standard_spelling = "an"
                    elif standard_spelling.strip(".").lower() in standardizer:
                        s =  standardizer[standard_spelling.strip(".").lower()]
                        if all_caps: 
                            standard_spelling = "".join([l.capitalize() for l in s])
                        elif caps: 
                            standard_spelling = s.capitalize()
                        else: 
                            standard_spelling = s 
                    
                    current.append(standard_spelling)

                  if 'fw' in pos: # foreign words
                      fw.append(fw_idx)
                  fw_idx += 1 
              
              self.standard.append((" ".join(current)))
              self.sent_id.append((sid,part_id))
              self.tokens.append(" ".join(tokens))
              if check_foreign(fw):
                fid = [str(s) for s in sid]
                fid = [fid,str(part_id)] 
                self.fw_subchunks[str(fid)] = fw
    
    def get_chunks(self, targets):
      chunks = {} # keys are just (tcpID, chunk idx, is_note)
      for s_id, part_id in self.sent_id:
          if s_id[-1] > -1:
              curr_sid = f"{s_id[0]},{s_id[1]},True"
              if curr_sid not in chunks:
                  chunks[curr_sid] = {}
              if s_id[-1] not in chunks[curr_sid]:
                  chunks[curr_sid][s_id[-1]] = targets[self.sent_id_to_idx[(s_id,part_id)]]
          else:
              curr_sid = f"{s_id[0]},{s_id[1]},False"
              if curr_sid not in chunks:
                  chunks[curr_sid] = targets[self.sent_id_to_idx[(s_id,part_id)]]
              else: 
                  chunks[curr_sid] = chunks[curr_sid] + " " + targets[self.sent_id_to_idx[(s_id,part_id)]]
      return chunks 
    
def PROCESS_SERMONS(era,prefix,text,marginalia,info):
    tcpIDs = corpora[era][prefix]

    if len(tcpIDs) == 0: return
    # print(era,prefix)
    tcpIDs = sorted(tcpIDs)
    corpus = Sermons(era,prefix,text,marginalia)

    body_formatted = []
    margins_formatted = []

    tokenized = corpus.get_chunks(corpus.tokens)
    standardized = corpus.get_chunks(corpus.standard)

    for key, segment in tokenized.items():
        if len(segment) == 0: continue 
        key = key.split(",")
        tcpID = key[0]
        sidx = int(key[1])
        i = info[tcpID][sidx]
        if i[1] is None: loc_type = None
        elif 'IMAGE' in i[1]: loc_type = "IMAGE"
        else: loc_type = "PAGE"

        if key[-1] == 'False':
            body_formatted.append({
                'tcpID': tcpID,
                'sid': sidx,
                'section': i[0],
                'loc': [i[1].split(loc_type)[-1] if loc_type is not None else None][0], 
                'loc_type': loc_type, 
                'pid': i[2], # paragraph index 
                'tokens': combine_punc_with_text(segment), 
                'standardized': combine_punc_with_text(standardized[",".join(key)])
            })
            # body_formatted.append({
            #     'tcpID': tcpID,
            #     'pid': i[2], # paragraph index 
            #     'tokens': combine_punc_with_text(segment), 
            # })
        else: 
            for nid, part in segment.items(): 
                margins_formatted.append({
                    'tcpID': tcpID,
                    'sid': sidx,
                    'nid': nid,
                    'tokens': combine_punc_with_text(part), 
                    'standardized': combine_punc_with_text(standardized[",".join(key)][nid])
                })
    
    if len(body_formatted) > 0: 
        # # for testing purposes: 
        # with open(f'../assets/segments.csv','w+') as file: 
        #     writer = csv.DictWriter(file, fieldnames=body_formatted[0].keys())
        #     writer.writerows(body_formatted)

        with open(f'/Users/amycweng/DH/SERMONS_APP/db/data/{era}/{prefix}_body.csv','w+') as file: 
            writer = csv.DictWriter(file, fieldnames=body_formatted[0].keys())
            writer.writerows(body_formatted)
            # print(f'{prefix} body done')

        with open(f'/Users/amycweng/DH/SERMONS_APP/db/data/{era}/{prefix}_margin.csv','w+') as file: 
            writer = csv.DictWriter(file, fieldnames=['tcpID','sid','nid','tokens','standardized'])
            writer.writerows(margins_formatted)
            # print(f'{prefix} marginalia done')

        with open(f'../assets/foreign/{era}_{prefix}.json','w+') as file: 
            json.dump(corpus.fw_subchunks,file)
