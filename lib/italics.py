import re,json
import sys 
sys.path.append('../')

from collections import Counter 

tcpID = 'A41135'
with open(f"../assets/encoded/{tcpID}.json","r") as file: 
    data = json.load(file)

encodings, citation_info = data 
italicized = [item[4] for item in encodings if 
                                        item[5] in ["B-IT","I-IT"] 
                                        and len(item[2]) > 3 
                                        and re.search(r"^[A-Z]",item[2])
                                        and re.search(r"np",item[3])
                                        and item[-1] == "O-REF"]
print(Counter(italicized).most_common())
