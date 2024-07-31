import os, json,re
standardizer = {} # conversion dictionary 

# morphadorner 
with open("/Users/amycweng/DH/morphadorner-2/data/standardspellings.txt","r") as file: 
    standard = file.readlines()
standard = {x.strip("\n"):None for x in standard} # known spellings 

# standardized with GPT 3.5 
for fp in os.listdir('../assets/vocab'):
    if "standard" not in fp: continue
    with open(f"../assets/vocab/{fp}") as file: 
        new_standard = json.load(file)
        standardizer.update({n.lower():k for n,k in new_standard.items()})
        standard.update({n.lower():None for n in new_standard})

# Biblical entities 
with open(f"../assets/bible/TIPNR - Translators Individualised Proper Names with all References - STEPBible.org CC BY.txt") as file: 
    data = file.readlines()
in_entities_section = False
entities = []
for idx, line in enumerate(data): 
    line = line.strip()
    if not line:
        continue
    
    if line.startswith('$========== P'):
        in_entities_section = True
        continue  
    
    if idx < 112: continue
    if idx > 14456: continue
    if in_entities_section:
        name = line.split('=')[0]
        name_parts = name.split('@')
        if len(name_parts) > 1: 
            name = name_parts[0].strip() 
            if "–" in name or "ADDED" in name or "(" in name or "-" in name: 
                name = name.split("	")[-1]

            if name[0].islower() or "–" in name[0]: continue
            if "|" in name: 
                entities.extend(name.split("|"))
            else: 
                entities.append(name)
    else:
        continue
entities = list(sorted(set(entities)))
standard.update({e.lower():None for e in entities})

# canonical author names 
author_ids = {}
with open("../assets/misc/authors.csv","r",encoding="utf-8") as file: 
    data = file.readlines()

unicode_pattern = re.compile(r'[^\x00-\x7F]+')
for l, line in enumerate(data):
    if l == 0: continue 
    a_id, name_type, name = line.split('","')
    a_id = a_id.split("authors/")[-1].strip('\"')
    name = re.sub(r'\"|\[|\]','',name)
    orig_name = name.strip("\n") 
    orig_name = unicode_pattern.sub('', orig_name)
    name = orig_name.split(" ")
    if a_id not in author_ids: 
        author_ids[a_id] = []
    if len(name) < 5: 
        if name_type in ['lat','default','eng']:
            # if len(name) == 3 and name_type == "eng": 
            #     name = name[1]
            # elif len(name) == 2 and name_type == "eng": 
            #     if len(name[0].split(" ")) == 1: 
            #         name = name[1]
            #     else: 
            #         name = name[0]
            author_ids[a_id].append(orig_name)

for name_list in author_ids.values(): 
    for name in name_list: 
        for n in name.split(" "): 
            standard[n.lower()] = None

standard = {s:None for s in standard if not re.search("\d",s)}

# nltk.download('wordnet')
from nltk.corpus import wordnet as wn
wordnet_words = set(wn.words())
standard.update({w.lower():None for w in wordnet_words})
standard = {s:None for s in standard if not re.search("\d",s)}
print(f"{len(standardizer)} corrected spellings")