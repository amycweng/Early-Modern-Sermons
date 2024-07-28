import os, subprocess,json 
import pandas as pd 
# NUPOS: https://morphadorner.northwestern.edu/documentation/nupos/
def adorn(group): 
    repo = '/Users/amycweng/DH/Early-Modern-Sermons' # github repo 
    os.chdir('/Users/amycweng/DH/morphadorner-2')
    subprocess.run(['./adornplainemetext', f"{repo}/assets/adorned", f"{repo}/assets/plain_body/{group}*.txt"])

if __name__ == "__main__": 
    with open('../assets/corpora.json','r') as file: 
        corpora = json.load(file)
    era_name = input('Enter subcorpus name: ')
    already_adorned = os.listdir('../assets/adorned')
    already_adorned = {k.split(".txt")[0]:None for k in already_adorned}
    selected_prefix = input("Enter prefix or All: ")
    if selected_prefix == "All":
        for prefix,tcpIDs in corpora[era_name].items(): 
            for tcpID in sorted(tcpIDs): 
                if tcpID not in already_adorned: 
                    adorn(tcpID)
    else: 
        for tcpID in sorted(corpora[era_name][selected_prefix]):
            if tcpID not in already_adorned: 
                adorn(tcpID)

    for tcpID in sorted(tcpIDs): 
        if tcpID not in already_adorned: 
            adorn(tcpID)

# Roman numerals are sometimes labeled as np (proper noun), e.g., from B31833
#     EZEK	EZEK	np1	EZEK	EZEK	0
#     .	.	.	.	.	1
#     XXII	XXII	np1	XXII	Xxii	0
#     .	.	.	.	.	1
#     XXX.XXXI	XXX.XXXI	np1	XXX.XXXI	XXX.XXXI	0
def bible(): 
    import pandas as pd 
    import sys,re 
    sys.path.append('../')
    data = pd.read_csv("../assets/bible/kjv.csv")
    doc_id = data['doc_id']
    text = data['text']
    plaintext = []
    for idx, d_id in enumerate(doc_id): 
        d_id = d_id.strip(" (KJV)")
        d_id = re.sub(":","-",d_id)
        d_id = "-".join(d_id.split(" "))
        d_id = f"VERSE-{d_id}"
        plaintext.append(f"{d_id} {text[idx]}")

    plaintext = " ".join(plaintext)
    with open("../assets/kjv.txt","w+") as file: 
        file.write(plaintext)

def adornbible(): 
    repo = '/Users/amycweng/DH/Early-Modern-Sermons' # github repo 
    os.chdir('/Users/amycweng/DH/morphadorner-2')
    subprocess.run(['./adornplainemetext', f"{repo}/assets", f"{repo}/assets/kjv.txt"])

# bible()
# adornbible()