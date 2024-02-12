import re
import sys 
sys.path.append('../')
from lib.standardization import * 
from lib.sentences import *

Text = Sentences('A41135')
# for idx, tuple in enumerate(Text.sentences): 
#     sermon_idx, start_page, sentence = tuple[:3]
#     argh = extract_citations(sentence)
#     if len(argh[0]) > 0: 
#         print(argh[0], argh[1], argh[-1])

print(extract_citations("2 Thes 3 4-6 & 24"))
    # print(sentence)
# Sentences('A00200')