import os, subprocess,json 
import pandas as pd 
# NUPOS: https://morphadorner.northwestern.edu/documentation/nupos/
def adorn(group): 
    repo = '/Users/amycweng/DH/Early-Modern-Sermons' # github repo 
    os.chdir('/Users/amycweng/DH/morphadorner-2')
    subprocess.run(['./adornplainemetext', f"{repo}/assets/adorned", f"{repo}/assets/plain_body/{group}*.txt"])

# repo = '/Users/amycweng/DH/Early-Modern-Sermons' # github repo 
# os.chdir('/Users/amycweng/DH/morphadorner-2')
# subprocess.run(['./adornplainemetext', f"{repo}/lib", f"{repo}/lib/sample.txt"])

if __name__ == "__main__": 
    already_adorned = os.listdir('../assets/adorned')
    already_adorned = {k.split(".txt")[0]:None for k in already_adorned}
    
    sermons = pd.read_csv("../assets/sermons.csv")
    all_sermons = list(sermons['id'])
    sermons_missing = pd.read_csv("../assets/sermons_missing.csv")
    all_sermons.extend(list(sermons_missing['id']))
    tcpIDs = sorted(all_sermons) 

    prefix = input("Enter prefix: ")
    for tcpID in tcpIDs: 
        if prefix in tcpID:  # A0, B
            if tcpID not in already_adorned: 
                adorn(tcpID)


# Roman numerals are sometimes labeled as np (proper noun), e.g., from B31833
#     EZEK	EZEK	np1	EZEK	EZEK	0
#     .	.	.	.	.	1
#     XXII	XXII	np1	XXII	Xxii	0
#     .	.	.	.	.	1
#     XXX.XXXI	XXX.XXXI	np1	XXX.XXXI	XXX.XXXI	0
