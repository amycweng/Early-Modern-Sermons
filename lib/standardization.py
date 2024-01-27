'''Text cleaning and conversions'''
import re,csv
import sys 
sys.path.append('../')
from lib.abbreviations import * 
from lib.decomposition import * 

def extract_citations(n):
    citations, outliers = [], [] 
    n = clean_text(n)
    n = replaceBook(n)
    match,text_str = find_matches(n)
    # print(match)
    if len(match) > 0: 
        for item in match:
            item = re.sub(r"([^0-9a-z*])$","",item)
            item = item.split(" ")
            # accounting for case where the chapter number precedes the book's name 
            if re.search(r"\d+", item[0]):
                chapter = item[0]
                item[0] = item[1] # book 
                item[1] = chapter 
            # case of <book> ch <num> <num>  
            if re.search(r'^ch$',item[1]):
                item[1] = ""
            elif len(item) > 2 and re.search(r'^ch$',item[2]):
                # case of '1 K. 19. ch. 18.  
                chapter = item[3]
                verse = item[1]
                item[1],item[2],item[3] = chapter,verse,"" 
            item = " ".join(item)
            decomposed = decompose(item)
            citations.extend(decomposed[0])
            outliers.extend(decomposed[1])
    return citations, outliers, text_str 

def clean_text(n): 
    # remove foreign language indicators 
    n = re.sub(rf"〈 in non-Latin alphabet 〉", "",n)
    # replace all special characters with asterisks 
    n = re.sub('〈◊〉|•|▪','*',n)
    # remove everything that is not an alphabetical character, integer, comma, ampersand, hyphen, asterisk, period, apostrophe or a single space
    n = re.sub(r'[^\w\d\,\&\-\—\*\(\)\.\'\"\:\_ ]','',n)
    # strip away letters indicating verse or chapter, as well as the phrase 'of Sol' which follows 'Song' or 'Wisdom'
    n = re.sub(r"\bc\b|\bl\b|\bv\b|\bverse\b|\bver\b|\bcap\b|\bchap\b|\bchapter\b|\bof Sol\b","",n)
    # normalize ampersands and conjunctions 
    n = re.sub(r"\band\b|\&ampc\b|\&amp\b|\bet\b|&",' & ', n)
    # replace all instances of multiple white spaces with a single space. 
    n = re.sub(r'\s+',' ',n)
    return n 

def clean_word(word): 
    word = word.lower().strip(".")
    word = re.sub(r"([^\w\d\*])$","",word)
    word = re.sub("v","u",word) # replace all v's with u's 
    word = re.sub(r"^i","j",word) # replace initial i's to j's 
    word = re.sub(r"(?<=\w)y(?=\w)","i",word) # replace y's that occur within words into i's
    word = re.sub(r"[^\x00-\x7F]+","*",word) # replace all non-ASCII characters with asterisks 
    return word 

# convert a roman numeral to its integer format 
# The longest book in the Bible is Psalms with 150 chapters, 
# and the longest chapter (Psalms 119) has 176 verses
roman_to_int = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
def convert_numeral(word):
    if word == "civ": 
        return word 
    if not re.search(r'^(c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$', word.lower().strip(".")): 
        return word 
    num = 0
    word = word.lower().strip(".") # strip period if Roman numeral 
    for idx, n in enumerate(word):
        if idx > 0 and roman_to_int[n] > roman_to_int[word[idx - 1]]:
            # case where we are one less than a multiple of ten or five (e.g., IX or IV)
            num += roman_to_int[n] - 2 * roman_to_int[word[idx - 1]]
        else:
            num += roman_to_int[n] 
    if num > 0: 
        return str(num)
    else: 
        return word 

'''Standardize abbreviations'''
num_to_text = {'1':'one','2':'two','3':'three'}
def replaceBook(text): 
    text = text.split(" ")
    for idx, word in enumerate(text): 
        if idx+1 in range(len(text)): # must be followed by at least one number 
            if not re.match(r'^[0-9*\,\-\—\*\.\:]+$',text[idx+1]): 
                continue 
        text[idx] = convert_numeral(word)
        word = clean_word(word)
        # identififed a valid abbreviation         
        if word in abbrev_to_book:
            # update term to the normalized version 
            word = abbrev_to_book[word]
            # non-scriptural references to an epistle
            if word == 'epistle' and idx > 0:
                continue
            elif re.search('samuel|kings|chronicles|corinthians|thessalonians|timothy|peter',word): 
                # do not convert 'ch' or 'the' if it is not preceded and succeeded by a number or an asterisk 
                if idx > 0: 
                    # the case of "1, Kings"
                    prev = re.sub(r"([^\w\d\*])$","",text[idx-1])
                    if not re.search(r'^[1-3\*{1}]\.{0,}$',prev):
                        continue 
                    else: 
                        text[idx-1] = prev
                else: 
                    continue
            text[idx] = word  
    text = " ".join(text)
    numBooks = re.findall(r"([1-3\*{1}]) (samuel|kings|chronicles|corinthians|thessalonians|timothy|peter|john)",text)
    # convert all numbered books into a single token ("1 corinthians" --> "onecorinthians")
    for num, book in numBooks: 
        if num == "*": 
            text = re.sub(r"\* {book}",f"unknown{book}",text)
        elif f"{num} {book}" in numBook: 
            text = re.sub(f"{num} {book}",f"{num_to_text[num]}{book}",text)
    return text

def find_matches(text): 
    text = text.split(" ")
    for idx, t in enumerate(text): 
        if not re.search(r"[A-Za-z]", t): 
            text[idx] = re.sub(r"[\.\:]"," ",t)
    text = re.sub(r"\s+"," "," ".join(text))
    text_str = text
    count = 0 
    text = text.split(" ")
    matches = []
    current = []
    for idx, t in enumerate(text): 
        if t in abbrev or t in numBook.values():
            if len(current) > 1 and current[1] != "": 
                matches.append(" ".join(current))
                text_str = re.sub(re.escape(" ".join(current)), f"(REF{count})",text_str)
                count += 1 
                current = []
            if idx > 0 and t not in numBook.values():
                if re.search(r"^[0-9*]+$", text[idx-1]): 
                    # check the next two numbers 
                    if (idx+1) < len(text) and (idx+2) < len(text):
                        if re.search(r"^[0-9]+$", text[idx+1]) and re.search(r"^[0-9]+$", text[idx+2]): 
                            current = [t]
                        else: 
                            current = [text[idx-1], t] 
                    else: 
                        current = [text[idx-1], t] 
                else: 
                    current = [t]
            else: 
                current = [t]
        elif len(current) > 0 and re.search(r"[0-9*]+", t): 
            if re.search(r"[A-Za-z]",t):
                continue
            current.append(t)
        elif len(current)>0 and re.search(r'^ch$',t): 
            current.append(t)
        elif len(current) > 1 and current[1] != "":
            # have reached the end of a relevant citation  
            matches.append(" ".join(current))
            text_str = re.sub(re.escape(" ".join(current)), f"(REF{count})",text_str)
            count += 1 
            current = []
    return matches, text_str
        

'''Main function to actually extract all of the Biblical citations'''
def decompose(phrase): 
    # initialize lists to keep track of the properly formatted citations and possible formats that this code cannot currently account for 
    citations, outliers = [], []
    # only a chapter-level citation
    if re.search(r'^[a-z]+ [0-9*]+$',phrase):
        citations.append(phrase.strip())
        citations = proper_title(citations)
        return citations, outliers 

    phrase = phrase.split(" ")
    book = phrase[0]
    phrase = " ".join(phrase[1:]).strip()
    if re.search('—|\,|\,$',phrase): 
        phrase = re.sub('—','-',phrase)
        phrase = re.sub('\,-','-',phrase)
        phrase = re.sub('\,$| \,$','',phrase)
    
    # if the text is simply a single citation, call simple() to append the citation to the list of citations 
    if re.search(r'^[0-9\*]+ [0-9\*]+$',phrase):  
        citations.append(simple(book, phrase))
    # if there are ampersands in the text, split the text up by the ampersands 
    elif re.search('&',phrase): 
        passages = phrase.split('&')
        for passage in passages:
            passage = passage.strip()
            if re.search('\-', passage):
                c, o = hyphen(book,passage)
                citations.extend(c)
                outliers.extend([f'{book} {item}' for item in o])
                # if len(o): print(orig_phrase)
            elif re.search('\,',passage): 
                citations.extend(comma(book,passage))
            # call othersimple() to account for the case of "<chapter> <line1> <line2>" 
            elif re.search(r'[0-9*]+ [0-9*]+ [0-9*]+$', passage): 
                citations.extend(othersimple(book, passage))
            # call simple() to account for "<chapter> <line1>"
            elif re.search(r'^[0-9*]+ [0-9*]+$',passage): 
                citations.append(simple(book, passage))
    
    # if there are no ampersands but there are hyphens
    elif re.search('-', phrase):
        c, o = hyphen(book,phrase)
        citations.extend(c)
        outliers.extend([f'{item}' for item in o])
        # if len(o): print(orig_phrase)
    # if there are no ampersands & hyphens but there are commas  
    elif re.search(',',phrase): 
        citations.extend(comma(book, phrase))
    # else, there is a format that this code cannot account effectively for 
    else: 
        # special cases; see the othersimple function description for examples
        if re.search(r'[0-9*]+ [0-9*]+ [0-9*]+$',phrase):  
            citations.extend(othersimple(book, phrase))
        # # hard coding some special cases for the charity sermons dataset
        # elif '119 5 10 32 57 93 106 173 40' == phrase and book == 'psalms': 
        #     # original is Psal 119.5 10.32.57.93.106 173.40.
        #     citations.extend(['psalms 119:5', 'psalms 10:32', 'psalms 10:57','psalms 10:93','psalms 10:106', 'psalms 173:40'])
        # elif '8 1 3 5 8 9' in phrase and 'romans' in book: 
        #     # original is Rm. 8.1.3 5.8.9
        #     citations.extend(['romans 8:1','romans 8:2', 'romans 8:3', 'romans 5:8', 'romans 5:9'])
        else: 
            outliers.append(f'{book} {phrase}')
            # print(orig_phrase)
    # pretty formatting 
    citations = proper_title(citations)
    # return both citations and outliers  
    return citations, outliers

'''Convert the numbered books back into their original formats, i.e., "Onecorinthians" to "1 Corinthians"'''
def proper_title(citations_list): 
    final_citations = []
    for citation in citations_list:
        citation = re.sub(f'\,','',citation)
        citation = citation.split(' ') 
        book = citation[0]

        if re.search('one',book):
            book = re.sub('one','',book)
            final_citations.append(f'1 {book.capitalize()} {citation[1]}')
        elif re.search('two',book):
            book = re.sub('two','',book)
            final_citations.append(f'2 {book.capitalize()} {citation[1]}')
        elif re.search('three',book):
            book = re.sub('three','',book)
            final_citations.append(f'3 {book.capitalize()} {citation[1]}')
        elif re.search('unknown',book):
            book = re.sub('unknown','',book)
            final_citations.append(f'* {book.capitalize()} {citation[1]}')
        else: 
            final_citations.append(f'{book.capitalize()} {citation[1]}')
    return final_citations 
