import re
from EEPS_helper import *
from dictionaries.abbreviations import * 
'''
Clean text
'''
def clean_text(n): 
    # remove everything that is not an alphabetical character, integer, comma, ampersand, hyphen, gap letter, gap word, period, apostrophe or a single space
    n = re.sub(r'[^\w\d\,\&\-\—\•\◊\(\)\.\'\"\: ]','',str(n))
    
    # normalize conjunctions 
    n = re.sub(r"\band\b|\bet\b|\b\&\b|\b& &\b",' & ', n)
    numAMP = re.findall(r"([\d])(&)",n)
    for instance in numAMP: # an ampersand stuck to a number 
        n = re.sub(f'{instance[0]}&', f"{instance[0]} &",n)
    
    # replace all instances of multiple white spaces with a single space. 
    n = re.sub(r'\s+',' ',n)
    return n 
'''
Clean word to see if it is a possible Bible book abbreviation 
'''
def clean_word(word): 
    word = word.lower()
    word = re.sub(r"[^\w\d\•\◊]+","",word) # 
    word = re.sub("v","u",word) # replace all v's with u's 
    word = re.sub("vv","w",word) # replace all vv's with w's 
    word = re.sub(r"^i","j",word) # replace initial i's to j's 
    word = re.sub(r"(?<=\w)y(?=\w)","i",word) # replace y's that occur within words into i's
    return word  
'''
Identify if a word should be added in a candidate citation span 
'''
def include_in_span(w,w2):
    w_clean = re.sub(r"[\.\,\&\-\—\:]","",w)
    w2 = re.sub(r"[\.\,\&\-\—\:]","",w2).lower()
    if isNumeral(w_clean):
        num = convert_numeral(w_clean)
        if re.match(r"[1-4\.]",str(num)) and w2 in abbrev_to_book:
            w2 = abbrev_to_book[w2]
            if f"{num} {w2}" in numBook: 
                return False 
        return True 
    if re.match(r'^[cvl]{1}$',w_clean.lower()):
        return True 
    if re.match(r"\bverse\b|\bvers\b|\bver\b|\bcap\b|\bchap\b|\bchapter\b|\bch\b|\bof\b|\bSol\b|\bSolomon\b",w_clean.lower()): 
        return True 
    if re.match(r"[\&\-\—\:]",w):
        return True 
    return False 
'''
Add words to candidate citation span 
'''  
def get_span(next_idx:int,text_list:list,span:list,curr:list):
    if next_idx == len(text_list): 
        return span, curr, next_idx
    next_word = text_list[next_idx]
    next_word2 = '' 
    if (next_idx + 1) < len(text_list):
        next_word2 = text_list[next_idx+1]

    while include_in_span(next_word,next_word2):
        curr.append(next_word)
        span.append(convert_numeral(next_word))
        next_idx += 1 
        if next_idx == len(text_list): 
            break
        next_word = text_list[next_idx]
        if (next_idx + 1) < len(text_list):
            next_word2 = text_list[next_idx+1]
    return (span, curr, next_idx)


'''Convert the numbered books back into their original formats, i.e., "Onecorinthians" to "1 Corinthians"'''
def proper_title(citations_list): 
    final_citations = []
    for citation in citations_list:

        citation = re.sub(f'\,','',citation)
        citation = citation.split(' ') 
        book = citation[0]
        citation = " ".join(citation[1:])
        if re.search('one',book):
            book = re.sub('one','',book).capitalize()
            final_citations.append(f'1 {book} {citation}')
        elif re.search('two',book):
            book = re.sub('two','',book).capitalize()
            final_citations.append(f'2 {book} {citation}')
        elif re.search('three',book):
            book = re.sub('three','',book).capitalize()
            final_citations.append(f'3 {book} {citation}')
        elif re.search('four',book):
            book = re.sub('four','',book).capitalize()
            final_citations.append(f'4 {book} {citation}')
        elif re.search('unknown',book):
            book = re.sub('unknown','',book).capitalize()
            final_citations.append(f'• {book} {citation}')
        else: 
            final_citations.append(f'{book.capitalize()} {citation}')
    return final_citations 

'''
Helper function to extract citations from a marginal note that contains commas 
e.g, "isaiah 1.2, 3, 4, 5.5" --> "isaiah 1.2", "isaiah 1.3", "isaiah 1.4", "Isaiah 5.5"
'''
def comma(book, passage): 
    phrases = []
    outliers = []
    # remove duplicate spaces 
    passage = re.sub('  ',' ',passage)  
    passage = re.sub(rf'{book}| ,','',passage).strip()

    items = passage.split(',')
    chapter = '' 
    verse = ''
    add_item = False 
    for w in items:
        if "." in w: 
            w = w.split(".")
            chapter = w[0] + "."
            for num in w[1:]: 
                phrases.append(f"{book} {chapter}{num}")
            continue 
        elif ":" in w: 
            w = w.split(":")
            chapter = w[0] + "."
            add_item = True
        else: 
            if "-" in w: 
                c, o = continuous(book, f"{chapter}{w}")
                phrases.extend(c)
                outliers.extend(o)
            else: 
                w = w.strip(" ").split(" ")
                add_item = True 
        
        if add_item: 
            if len(w) > 1: 
                verse = w[1].strip(" ")
            else: 
                verse = w[0]
            if not re.search(r"[^\d+]",verse):
                phrases.append(f'{book} {chapter}{verse}')
            else: 
                outliers.append(f'{book} {chapter}{verse}')

    return phrases,outliers

'''
Helper function to extract citations from a marginal note that does not contain commas

Target format is "<book> <chapter>.<verse>" 
'''
def simple(book, passage): 
    # the simple case of just having "<book> <chapter>.<verse>"
    # sometimes an entirely missing verse reference becomes an illegible word --> Psalms 39.3 as Psalms * 
    passage = passage.strip(",")
    nums = re.findall(r'[\d\•|\◊]+',passage)
    if re.search(r"[^\d+]",nums[1]):
        if not re.search(r"[^\d+]",nums[0]):
            # chapter known 
            return [f'{book} {nums[0]}'],[f'{book} {passage}']
    else: 
        if not re.search(r"[^\d+]",nums[0]):
            return [f'{book} {nums[0]}.{nums[1]}'],[]
    return [],[f'{book} {passage}'] 


'''
'''
def extract_chapter_verse_pairs(phrase):
    # Match only digits and periods
    if re.fullmatch(r'[\d.]+', phrase):
        numbers = re.findall(r'\d+', phrase)
        n = len(numbers)

        if n == 3:
            # Special case: 3 digits → 1 chapter, 2 verses
            chapter = int(numbers[0])
            verse1 = int(numbers[1])
            verse2 = int(numbers[2])
            return [f"{chapter}.{verse1}", f"{chapter}.{verse2}"]

        elif n % 2 == 0:
            # Even number of digits → treat as chapter-verse pairs
            pairs = []
            for i in range(0, n, 2):
                chapter = int(numbers[i])
                verse = int(numbers[i+1])
                pairs.append(f"{chapter}.{verse}")
            return pairs

    return []  # Not valid

# print(extract_chapter_verse_pairs("1.2.3.4"))    # ['1.2', '3.4']
# print(extract_chapter_verse_pairs("2.5.8"))      # ['2.5', '2.8']


'''
These are cases of continuous citation, 
e.g, "Genesis 3.9-14" --> "Genesis 3.9", "Genesis 3.10", etc. until "Genesis 3.14"
'''
def continuous(book, w):
    passage = w 
    phrases = [] 
    outliers = []
    chapter = '' 
    
    if "." in w: 
        w = w.split(".")
        chapter = w[0] 
        w = "".join(w[1:])
    elif ":" in w: 
        w = w.split(":")
        chapter = w[0] 
        w = "".join(w[1:])
    
    w = w.split("-")
    if chapter != '': 
        chapter = f"{chapter}."
    
    if len(w) == 2: 
        start,end = w
        if len(end) < len(start): 
            # cases of 18-9
            end = "".join(start[:len(start)-len(end)]) + end
        if re.search(r"[^\d+]",start) or start == "": 
            if re.search(r"[^\d+]",end):
                if chapter != '': 
                    outliers.append(f'{book} {passage}') 
            else: 
                phrases.append(f"{book} {chapter}{end}")
                outliers.append(f'{book} {chapter}{start}')        
        else: 
            if re.search(r"[^\d+]",end) or end == "":
                phrases.append(f"{book} {chapter}{start}")
                outliers.append(f'{book} {chapter}{end}')  
            else: 
                start, end = int(start), int(end)
                for idx in range(end-start+1): 
                    phrases.append(f'{book} {chapter}{start+idx}')        
    return phrases, outliers


'''
These are cases in which hyphens divide discrete citations, 
'''
def hyphen(book,passage): 

    citations, outliers = [], []
    passage = passage.strip().strip('-')
    
    if re.search(r"[^\d+]",passage):
        outliers.append(f"{book} {passage}")

    if len(re.findall(r'[\d\•|\◊]+',passage)) == 3:
        # case of 'revelation 1, 13-16' or 'proverbs 8 18 , -21' or 'luke 11-31 , 32" 
        # strip the commas out 
        passage = re.sub(",","",passage)
        passage = re.sub(r"\s+"," ",passage)
    
    if re.search(r'^[\d\s\.\:]*[\d\•|\◊]+-[\d\•|\◊]+$',passage): 
        # '3.9-12' or '3.9 - 12'        
        c, o = continuous(book, passage)
        citations.extend(c)
        outliers.extend(o)
        
    return citations, outliers
    


