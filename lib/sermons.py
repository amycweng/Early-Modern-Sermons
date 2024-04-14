import json 
import sys
sys.path.append('../')

class Sermons():
    def __init__(self, prefix):
        self.prefix = prefix
        self.sent_id = [] # tuples of ((tcpID, chunk idx, location), subchunk idx) representing the subchunk's ID
        self.sentences = [] # subchunk strings that are lemmatized
        self.fw_subchunks = {} # IDs of subchunks with more than three foreign words
        self.chunks = [] # subchunk strings that are tokenized

        self.get_texts_from_json()
        self.get_marginalia_from_json()
        self.get_indices()
        self.get_chunks(self.chunks)

    def get_indices(self):
        self.sent_id_to_idx = {x:idx for idx, x in enumerate(self.sent_id)}

    def get_marginalia_from_json(self):
        # reorganize marginalia dictionary from the JSON file
        with open(f'../assets/processed/{self.prefix}_marginalia.json','r') as file:
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
        self.create_corpus(marginalia,True)
        print('Processed marginalia')

    def get_texts_from_json(self):
        with open(f'../assets/processed/{self.prefix}_texts.json','r') as file:
            texts = json.load(file)
            print('Loaded texts')
        self.create_corpus(texts)
        print('Processed texts')

    def create_corpus(self, data,is_margin=False):
      for tcpID, items in data.items():
          if self.prefix not in tcpID: continue

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

                  token, pos, lemma = x[0], x[1], x[2]
                  if len(token) == 0: continue
                  tokens.append(token)
                  if lemma == "encage" and token.isdigit():
                      current.append(x[0])
                  else:
                      current.append(lemma)

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
                      self.sentences.append(" ".join(current))
                      self.sent_id.append((sid,part_id))
                      self.chunks.append(" ".join(tokens))
                      if check_foreign(fw):
                          self.fw_subchunks[f"{sid[0]},{sid[1]},{sid[2]},{part_id}"] = fw

                      current = []
                      tokens = []
                      fw = []

                      fw_idx = 0
                      part_id += 1
    
    def get_chunks(self, original):
      chunks = {} # keys are just (tcpID, chunk idx, is_note)
      for s_id, part_id in self.sent_id:
          if s_id[-1] > -1:
              curr_sid = f"{s_id[0]},{s_id[1]},True"
              if curr_sid not in chunks:
                  chunks[curr_sid] = {}
              if s_id[-1] not in chunks[curr_sid]:
                  chunks[curr_sid][s_id[-1]] = original[self.sent_id_to_idx[(s_id,part_id)]]
              else: 
                  chunks[curr_sid][s_id[-1]] = chunks[curr_sid][s_id[-1]] + " " + original[self.sent_id_to_idx[(s_id,part_id)]]
          else:
              curr_sid = f"{s_id[0]},{s_id[1]},False"
              if curr_sid not in chunks:
                  chunks[curr_sid] = original[self.sent_id_to_idx[(s_id,part_id)]]
              else: 
                  chunks[curr_sid] = chunks[curr_sid] + " " + original[self.sent_id_to_idx[(s_id,part_id)]]
      self.chunks = chunks

prefix = 'B'
corpus = Sermons(prefix)
with open(f'../assets/processed/{prefix}.json','w+') as file: 
    json.dump([corpus.sent_id,corpus.sentences,corpus.chunks,corpus.fw_subchunks],file)
