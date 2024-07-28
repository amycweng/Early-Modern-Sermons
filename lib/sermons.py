import json,csv 
import sys,re
sys.path.append('../')

class Sermons():
    def __init__(self, era, prefix):
        self.era = era
        self.prefix = prefix
        self.sent_id = [] # tuples of ((tcpID, chunk idx, location), subchunk idx) representing the subchunk's ID
        self.standard = [] # subchunk strings that are standardized
        self.fw_subchunks = {} # IDs of subchunks with more than three foreign words
        self.tokens = [] # subchunk strings that are tokenized

        self.get_texts_from_json()
        self.get_marginalia_from_json()
        self.get_indices()

    def get_indices(self):
        self.sent_id_to_idx = {x:idx for idx, x in enumerate(self.sent_id)}

    def get_marginalia_from_json(self):
        # reorganize marginalia dictionary from the JSON file
        with open(f'../assets/processed/{self.era}/json/{self.prefix}_marginalia.json','r') as file:
            marginalia = json.load(file)
            print('Loaded marginalia')
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
            print('Processed marginalia')

    def get_texts_from_json(self):
        with open(f'../assets/processed/{self.era}/json/{self.prefix}_texts.json','r') as file:
            texts = json.load(file)
            print('Loaded texts')
        self.create_corpus(texts)
        print('Processed texts')

    def create_corpus(self, data,is_margin=False):
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

              fw = [] # contains indices of the foreign words
              fw_idx = 0

              for idx, x in enumerate(encodings):
                  segment = False

                  token, pos, standard_spelling = x[0], x[1], x[2]
                  if len(token) == 0: continue
                  tokens.append(token)
                  
                  if token != "<NOTE>": 
                    current.append(standard_spelling)

                  if 'fw' in pos: # foreign words
                      fw.append(fw_idx)
                  fw_idx +=1

                  if "." in pos or ';' in pos or ':' in pos or '?' in pos:
                      segment = True
                  elif "." in token:
                      if (idx+1) < len(encodings):
                        if len(encodings[idx+1][0]) == 0: continue
                        if encodings[idx+1][0][0].isupper(): # case of "L. 6 17. By faith Noah"
                            segment = True

                  def check_foreign(fw):
                      consec = 1
                      for i in range(len(fw) - 1):
                          if fw[i] + 1 == fw[i + 1]:
                              consec += 1
                              if consec == 3:
                                  return True
                          else:
                              consec = 1
                      return False

                  if segment or (idx == (len(encodings)-1)):
                      self.standard.append(" ".join(current))
                      self.sent_id.append((sid,part_id))
                      self.tokens.append(" ".join(tokens))
                      if check_foreign(fw):
                          self.fw_subchunks[f"{sid[0]},{sid[1]},{sid[2]},{part_id}"] = fw

                      current = []
                      tokens = []
                      fw = []

                      fw_idx = 0
                      part_id += 1
    
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
                  chunks[curr_sid][s_id[-1]] = chunks[curr_sid][s_id[-1]] + " " + targets[self.sent_id_to_idx[(s_id,part_id)]]
          else:
              curr_sid = f"{s_id[0]},{s_id[1]},False"
              if curr_sid not in chunks:
                  chunks[curr_sid] = targets[self.sent_id_to_idx[(s_id,part_id)]]
              else: 
                  chunks[curr_sid] = chunks[curr_sid] + " " + targets[self.sent_id_to_idx[(s_id,part_id)]]
      return chunks 
    
if __name__ == "__main__": 
    with open('../assets/corpora.json','r') as file: 
        corpora = json.load(file)

    # era = input('Enter subcorpus name: ')
    for era in corpora: 
        for prefix,tcpIDs in corpora[era].items():
            print(era,prefix)
            if len(tcpIDs) == 0: continue

            tcpIDs = sorted(tcpIDs)
            seen = {}
            corpus = Sermons(era,prefix)
            body_formatted = []
            margins_formatted = []

            tokenized = corpus.get_chunks(corpus.tokens)
            standardized = corpus.get_chunks(corpus.standard)

            with open(f"../assets/processed/{era}/json/{prefix}_info.json") as file: 
                info = json.load(file)

            def combine_punc_with_text(segment): 
                segment = re.sub(r'\s+([,.?!;:)])', r'\1', segment)
                segment = re.sub(r'([(])\s+', r'\1', segment) 
                segment = re.sub(r"\s+"," ",segment)
                return segment 

            for key, segment in tokenized.items():
                key = key.split(",")
                tcpID = key[0]
                if tcpID not in seen: 
                    nidx = 0
                    seen[tcpID] = True 

                i = info[key[0]][key[1]]
                if i[1] is None: loc_type = None
                elif 'IMAGE' in i[1]: loc_type = "IMAGE"
                else: loc_type = "PAGE"

                if key[-1] == 'False':
                    body_formatted.append({
                        'tcpID': tcpID,
                        'sid': key[1],
                        'section': i[0],
                        'loc': [i[1].split(loc_type)[-1] if loc_type is not None else None][0], 
                        'loc_type': loc_type, 
                        'pid': i[2], 
                        'tokens': combine_punc_with_text(segment), 
                        'standardized': combine_punc_with_text(standardized[",".join(key)])
                    })
                else: 
                    for nid, part in segment.items(): 
                        margins_formatted.append({
                            'tcpID': tcpID,
                            'sid': key[1],
                            'nid': nid,
                            'tokens': combine_punc_with_text(segment[nid]), 
                            'standardized': combine_punc_with_text(standardized[",".join(key)][nid])
                        })
            
            if len(body_formatted) == 0: continue

            with open(f'/Users/amycweng/DH/SERMONS_APP/db/data/{era}/{prefix}_body.csv','w+') as file: 
                writer = csv.DictWriter(file, fieldnames=body_formatted[0].keys())
                writer.writerows(body_formatted)
                print(f'{prefix} body done')
            with open(f'/Users/amycweng/DH/SERMONS_APP/db/data/{era}/{prefix}_margin.csv','w+') as file: 
                writer = csv.DictWriter(file, fieldnames=['tcpID','sid','nid','tokens','standardized'])
                writer.writerows(margins_formatted)
                print(f'{prefix} marginalia done')

            with open(f'../assets/processed/{era}/sub-segments/{prefix}.json','w+') as file: 
                json.dump([corpus.sent_id,corpus.standard,corpus.fw_subchunks],file)
