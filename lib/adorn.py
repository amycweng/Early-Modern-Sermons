import os, subprocess 
# took around 5 hours 
# NUPOS: https://morphadorner.northwestern.edu/documentation/nupos/
def adorn(group): 
    repo = '/Users/amycweng/DH/Early-Modern-Sermons' # github repo 
    os.chdir('/Users/amycweng/DH/morphadorner-2')
    subprocess.run(['./adornplainemetext', f"{repo}/outputs/adorned", f"{repo}/assets/plain/{group}*.txt"])
# tried adorning all at once and ran out of Java memory at A13752.txt 
adorn('A138')
adorn('A14')
adorn('A15')
adorn('A16')
adorn('A17')
adorn('A18')
adorn('A19')
for n in range(2,9+1): 
    adorn(f'A{n}')
adorn('B')
# Notes: 
# My custom delimiters and placeholders: SERMON{#}, STARTNOTE{#}, ENDNOTE{#}, PAGE{#}, NONLATINALPHABET  


# Roman numerals are sometimes labeled as np (proper noun), e.g., from B31833
#     EZEK	EZEK	np1	EZEK	EZEK	0
#     .	.	.	.	.	1
#     XXII	XXII	np1	XXII	Xxii	0
#     .	.	.	.	.	1
#     XXX.XXXI	XXX.XXXI	np1	XXX.XXXI	XXX.XXXI	0

