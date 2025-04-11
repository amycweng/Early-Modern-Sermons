import re
import sys 
sys.path.append('../')
from lib.dictionaries.abbreviations import * 
from EEPS_citationHelper import * 
from EEPS_helper import * 
numBook_to_proper = {v:k for k,v in numBook.items()}

def extract_citations(n):
    citations, outliers = {}, {}
    n = clean_text(n)

    spans,replaced = identify_citation_candidates(n)
    # print(spans,replaced)
    
    count = 0 
    if len(spans) > 0: 
        for item in spans:
            if re.search(r"\bch \d+ v|\d+ \bch\b \d+|\&c", item): 
                item = re.sub(r"\bch\b|\bv\b|\&c", '',item)
                item = re.sub(r"\s+"," ",item)
            item = re.sub(r"([^\w\d\•|\◊])$","",item) 
            item = re.sub(r"\s+"," ", item).strip(" ").split(" ")
            
            if item[-1] == "ch": item[-1] = "" # philippians 3 1 ch case 
            if item[0][-1] == ",": 
                # case of Ecclus, 25.16 in A09053
                book, nums = item[0].strip(","), item[2:]
                item = [book]
                for num in nums: item.append(num) 
            if len(item) > 2 and re.search(r'^ch$',item[2]):
                # case of '1 K. 19. ch. 18.
                if len(item) < 4:
                    item = item[:3]
                else: 
                    chapter = item[3]
                    verse = item[1]
                    item[1],item[2],item[3] = chapter,verse,"" 
 
            item = " ".join(item)
            decomposed = decompose(item)
            # print(decomposed)
            if len(decomposed[0]) > 0: 
                citations[count] = decomposed[0]
            if len(decomposed[1]) > 0: 
                outliers[count] = decomposed[1]
            count += 1 
    return citations, outliers, replaced  


# The longest book in the Bible is Psalms with 150 chapters, 
# and the longest chapter (Psalms 119) has 176 verses

'''Standardize abbreviations'''
num_to_text = {'1':'one','2':'two','3':'three','4':'four'}
def identify_citation_candidates(text): 
    text = text.split(" ")
    spans = []
    replaced = []
    idx = 0
    for word in text:   
        if re.search(r"^'",word): continue
        if idx == len(text): 
            break
        word = clean_word(text[idx])

        if re.search(r"^js$|^ch$|^de$|^the$|^can$|^he$|^am$|^time$|$the\^|^tyme$|^ti\^|^i\^|^Apol$|^ne$|^te$|^ti$|^tb$|^ac$|^child|^chyld",word): continue # without capitalization and a period 
        # initial i's have been converted to j's       

        # identififed a valid abbreviation         
        if word in abbrev_to_book:
            if (idx+1) < len(text): 
                # must be followed by at least one number 
                next_isNum = isNumeral(text[idx+1])
                if next_isNum and re.match("I|\•",text[idx+1]): 
                    # the latter to prevent false positives caused by the conversion of the pronoun 'I' to 1 
                    idx += 1 
                    continue
                if text[idx][0].islower() and re.match(r'\•|\◊',text[idx+1]): 
                    # current word is lower case 
                    # AND next word starts with an illegible char/word
                    idx += 1 
                    continue
                if not next_isNum and len(text[idx+1]) >= 10: 
                    # next word is not a number 
                    # AND next word is a long word 
                    idx += 1 
                    continue
                if (idx+2) < len(text):
                    next2_isNum = isNumeral(text[idx+2])
                    # both succeeding words are not numbers 
                    if (not next_isNum) and (not next2_isNum):
                        if text[idx+1] != "of" and not re.search("^Sol",text[idx+2]): # Song of Solomon 
                            idx += 1 
                            continue
                elif not next_isNum: 
                    # at the end of the segment 
                    idx += 1 
                    continue  
            else: 
                # word must be a known abbreviation 
                idx += 1 
                continue


            # update term to the normalized version 
            word = abbrev_to_book[word]
            orig = text[idx]

            # deal with numbered books 
            if re.search(r'samuel|kings|chronicles|corinthians|thessalonians|timothy|peter|esdras|maccabees|john',word): 
                if idx > 0: 
                    # the case of "1, Kings" --> remove trailing punctuation
                    prev = re.sub(r"([^\w\d\•|\◊])$","",text[idx-1]) 
                    prev_isNum = isNumeral(prev)
                    
                    if prev_isNum: 
                        prev = convert_numeral(prev)
                        prev = str(prev)
                        if re.search(r'^[1-4•]{1}$',str(prev)):
                            if idx-2 >= 0:
                                if text[idx-2] not in abbrev: 
                                    # avoid taking the last number of a prior cited verse 
                                    text[idx-1] = prev
                                    if prev == "•":
                                        word = f" unknown{word}"
                                    elif f"{prev} {word}" in numBook: 
                                        word = f" {num_to_text[prev]}{word}"
                                    orig = text[idx-1] + " " + orig                               
                            else: 
                                if prev == "•":
                                    word = f" unknown{word}"
                                elif f"{prev} {word}" in numBook: 
                                    word = f" {num_to_text[prev]}{word}"
                                orig = text[idx-1] + " " + orig
                    # do not convert 'ch' or 'the' if it is not preceded and succeeded by a number or caret 
                    elif re.search(r"^[cC]h$|^[Tt]he$",orig): 
                        idx += 1 
                        continue
                # the case of "2Cor" at the beginning of a segment 
                elif re.search(r"^\d",orig): 
                    prev = re.findall(r"^\d|^•",text[idx])[0]
                    if prev == "•":
                        word = f" unknown{word}"
                    elif f"{prev} {word}" in numBook: 
                        word = f" {num_to_text[prev]}{word}"
                    if f"{prev} {word}" in numBook: 
                        word = f"{num_to_text[prev]}{word}"   
                # do not convert 'ch' or 'the' if it is not preceded and succeeded by a number or caret 
                elif re.search(r"^[cC]h$|^[Tt]he$",orig): 
                    idx += 1 
                    continue

            idx += 1 
            curr = [orig, text[idx]]
            span = [word,convert_numeral(text[idx])]
            if (idx+1) < len(text):
                if next2_isNum: 
                    idx += 1
                    curr.append(text[idx])
                    span.append(convert_numeral(text[idx]))
                    
            idx += 1 
            span, curr, idx = get_span(idx,text,span,curr)
            span = [str(w) for w in span]
            spans.append(" ".join(span))
            replaced.append(" ".join(curr))
        else: 
            idx += 1 
    return spans,replaced

'''Main function to actually extract all of the Biblical citations'''
def decompose(phrase): 
    # initialize lists to keep track of the properly formatted citations and possible formats that this code cannot currently account for 
    citations, outliers = [], []
    # only a chapter-level citation
    phrase = phrase.strip(" ")
    if re.search(r'^\w+ \d+$',phrase):
        citations.append(phrase.strip())
        citations = proper_title(citations)
    elif re.search(r"\w+ \•\◊+",phrase):
        outliers.append(phrase.strip())
    
    phrase = phrase.split(" ")
    book = phrase[0]
    
    phrase = " ".join(phrase[1:]).strip()

    if re.search('—|\,|\,$',phrase): 
        phrase = re.sub('—','-',phrase)
        phrase = re.sub('\,-','-',phrase)
        phrase = re.sub('\,$| \,$','',phrase)
    phrase = re.sub(r'\s*\,\s*',',',phrase)
    phrase = re.sub(r'\s*\.\s*','.',phrase)
    phrase = re.sub(r'\s*\:\s*','.',phrase)
    phrase = re.sub(r'\s*\&\s*','&',phrase)
    phrase = re.sub(r'\s*\-\s*','-',phrase)

    # if the text is simply a single citation, call simple() to append the citation to the list of citations 
    if re.search(r'^[\d\•|\◊]+[\s\.\:]{1}[\d\•|\◊]+$',phrase):
        c,o = simple(book,phrase)
        citations.extend(c)
        outliers.extend(o)
    # if there are ampersands in the text, split the text up by the ampersands 
    elif re.search('&',phrase): 
        passages = phrase.split('&')
        all_single = True 
        for p in passages: 
            if not re.match(r"^[\d\•|\◊]+$",p):
                all_single = False 
       
        for passage in passages:
            passage = passage.strip()
            if all_single: 
                if re.match(r"\•|\◊",passage):
                    outliers.append(f"{book} {passage}")
                else: 
                    citations.append(f"{book} {passage}")
            elif re.search('\,',passage): 
                c, o = comma(book,passage)
                citations.extend(c)
                outliers.extend(o)
            elif re.search('\-', passage):
                c, o = hyphen(book,passage)
                citations.extend(c)
                outliers.extend(o)            
            # call simple() to account for "<chapter> <line1>"
            elif re.search(r'^\d+[.: ]\d+$',passage): 
                c,o = simple(book,passage)
                citations.extend(c)
                outliers.extend(o)
            else:  
                outliers.append(f"{book} {passage}")
    
    # if there are no ampersands & hyphens but there are commas  
    elif re.search(',',phrase): 
        c, o = comma(book,phrase)
        citations.extend(c)
        outliers.extend(o)
    # if there are no ampersands but there are hyphens
    elif re.search('-', phrase):
        c, o = hyphen(book,phrase)
        citations.extend(c)
        outliers.extend(o)
 
    # else, there is a format that this code cannot account effectively for 
    else: 
        # special cases; see the othersimple function description for examples
        if re.search(r'[\d\•|\◊]+[\s\.\:]{1}[\d\•|\◊]+',phrase):  
            c,o = simple(book,phrase)
            citations.extend(c)
            outliers.extend(o)
        else: 
            outliers.append(f"{book} {phrase}")
    
    # pretty formatting 
    citations = proper_title(citations)
    outliers = proper_title(outliers)
    for item in outliers: 
        if item in citations: 
            outliers.remove(item)
    # return both citations and outliers  
    return citations, outliers
