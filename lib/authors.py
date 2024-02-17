import re
import sys 
sys.path.append('../')
import pandas as pd 
# Paracelsus, Wollebius, Calvin, Aquinas, 

author_ids = {}

with open("../assets/authors.csv","r") as file: 
    data = file.readlines()

for l, line in enumerate(data):
    if l == 0: continue 
    a_id, name_type, name = line.split('","')
    a_id = a_id.split("authors/")[-1].strip('\"')
    name = re.sub(r'\"|\[|\]','',name)
    orig_name = name.strip("\n") 
    name = orig_name.split(" ")
    if len(name) < 5: 
        if name_type in ['lat','default','eng','abbr']:
            if len(name) == 3 and name_type == "default": 
                name = name[1]
            elif len(name) == 2 and name_type == "default": 
                if len(name[0].split(" ")) == 1: 
                    name = name[1]
                else: 
                    name = name[0]
            print(a_id, orig_name, name_type, name)
    if l > 25: break
