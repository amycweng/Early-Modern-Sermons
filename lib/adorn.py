import os, subprocess 
# NUPOS: https://morphadorner.northwestern.edu/documentation/nupos/
def adorn(group): 
    repo = '/Users/amycweng/DH/Early-Modern-Sermons' # github repo 
    os.chdir('/Users/amycweng/DH/morphadorner-2')
    subprocess.run(['./adornplainemetext', f"{repo}/assets/adorned", f"{repo}/assets/plain/{group}*.txt"])
# adorn('A0')
# adorn('A1')
# adorn('A17698')
# adorn('A177')
# adorn('A178')
# adorn('A179')
# adorn('A18')
# adorn('A19')
# adorn('A2')
# adorn('A2547')
# adorn('A256')
# adorn('A257')
# adorn('A258')
# adorn('A259')
# for n in range(3,7+1): 
#     adorn(f'A{n}')
adorn("A8")
adorn("A9")
adorn('B')
# Notes: 
# My custom delimiters and placeholders: SERMON{#}, STARTNOTE{#}, ENDNOTE{#}, PAGE{#}, NONLATINALPHABET  


# Roman numerals are sometimes labeled as np (proper noun), e.g., from B31833
#     EZEK	EZEK	np1	EZEK	EZEK	0
#     .	.	.	.	.	1
#     XXII	XXII	np1	XXII	Xxii	0
#     .	.	.	.	.	1
#     XXX.XXXI	XXX.XXXI	np1	XXX.XXXI	XXX.XXXI	0
