import re
import sys 
sys.path.append('../')
from lib.dictionaries.abbreviations import * 
from lib.decomposition import * 
numBook_to_proper = {v:k for k,v in numBook.items()}

def extract_citations(n):
    citations, outliers = {}, {}
    n = clean_text(n)
    n,replaced = replaceBook(n)
    match = find_matches(n,replaced)
    text_str = n 
    fully_replaced = []
    if len(match) > 0 and len(replaced) > 0: 
        for ref, item in enumerate(match):
            text_str = re.sub(re.escape(item), f"<REF{ref}>",text_str, 1)
            item = re.sub(r"([^0-9a-z*\^])$","",item) # remove trailing characters 
            item = item.split(" ")
            if not re.search(r"[0-9\*\^]",item[1]): 
                continue
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

            fully_replaced.append(replaced[ref][0] + " " + " ".join(item[1:]))
            
            item = " ".join(item)
            decomposed = decompose(item)
            if len(decomposed[0]) > 0: 
                citations[ref] = decomposed[0]
            if len(decomposed[1]) > 0: 
                outliers[ref] = decomposed[1]
    return citations, outliers, text_str,fully_replaced

def clean_text(n): 
    # remove everything that is not an alphabetical character, integer, comma, ampersand, hyphen, asterisk, period, apostrophe or a single space
    n = re.sub(r'[^\w\d\,\&\-\—\*\(\)\^\.\'\"\: ]','',n)
    # strip out periods and colons 
    n = re.sub(r"\.|\:", " ",n)
    # strip away letters indicating verse or chapter, as well as the phrase 'of Sol' which follows 'Song' or 'Wisdom'
    n = re.sub(r"\b[cC]\b|\b[lL]\b|\b[vV]\b|\b[vV]erse\b|\b[vV]ers\b|\b[vV]er\b|\b[cC]ap\b|\b[Cc]hap\b|\b[cC]hapter\b|\bof Sol\b|\bof Solomon\b","",n)
    # normalize conjunctions 
    n = re.sub(r"\band\b|\bet\b",' & ', n)
    # replace all instances of multiple white spaces with a single space. 
    n = re.sub(r'\s+',' ',n)
    return n 

def clean_word(word): 
    word = word.lower()
    word = re.sub(r"[^A-Za-z\^]","",word)
    word = re.sub("v","u",word) # replace all v's with u's 
    word = re.sub(r"^i","j",word) # replace initial i's to j's 
    word = re.sub(r"(?<=\w)y(?=\w)","i",word) # replace y's that occur within words into i's
    return word 

# convert a roman numeral to its integer format 
# The longest book in the Bible is Psalms with 150 chapters, 
# and the longest chapter (Psalms 119) has 176 verses
roman_to_int = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
def convert_numeral(word):
    orig_word = word
    word = re.sub(r"[^\w]", "",word)
    if not re.search(r'^(c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$', word): 
        return orig_word 
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
        return orig_word 

'''Standardize abbreviations'''
num_to_text = {'1':'one','2':'two','3':'three','4':'four'}
def replaceBook(text): 
    text = text.split(" ")
    replaced = []
    for idx, word in enumerate(text): 
        if idx+1 in range(len(text)): # must be followed by at least one number 
            follow = convert_numeral(re.sub(r"([^\w\d\*\^])$","",text[idx+1])) # remove trailing punctuation
            if not re.match(r'^[0-9\*\^]+$',follow): 
                continue 
       
        word = clean_word(text[idx])
        # identififed a valid abbreviation         
        if word in abbrev_to_book:

            # update term to the normalized version 
            word = abbrev_to_book[word]
            orig = text[idx]
            if re.search('samuel|kings|chronicles|corinthians|thessalonians|timothy|peter|esdras|maccabees',word): 
                # do not convert 'ch' or 'the' if it is not preceded and succeeded by a number or an asterisk 
                if idx > 0: 
                    # the case of "1, Kings"
                    prev = re.sub(r"([^\w\d\*\^])$","",text[idx-1]) # remove trailing punctuation
                    prev = convert_numeral(prev)
                    if re.search(r'^[1-4\^{1}]\.{0,}$',prev):
                        text[idx-1] = prev
                        orig = prev + " " + orig
                    elif re.search(r"^\d",text[idx]): 
                        num = re.findall(r"^\d",text[idx])[0]
                        if f"{num} {word}" in numBook: 
                            word = f"{num_to_text[num]}{word}"
                        else: continue
                    else: continue
                elif re.search(r"^\d",text[idx]): 
                    num = re.findall(r"^\d",text[idx])[0]
                    if f"{num} {word}" in numBook: 
                        word = f"{num_to_text[num]}{word}"
                    else: continue
                else: continue
            replaced.append((orig,text[idx+1]))
            text[idx] = word  
    text = " ".join(text)
    numBooks = re.findall(r"([1-4\^{1}]) (samuel|kings|chronicles|corinthians|thessalonians|timothy|peter|john|esdras|maccabees)",text)

    # case of a marginal note containing a single citation, e.g., "Sam. 15. 22."
    numBooks.extend(re.findall(r"^(samuel|kings|chronicles|corinthians|thessalonians|timothy|peter|john|esdras|maccabees)",text))
    # convert all numbered books into a single token ("1 corinthians" --> "onecorinthians")
    for entry in numBooks: 
        if len(entry) == 1:
            book = entry[0]
            text = re.sub(rf"\^ {book}",f"unknown{book}",text)
        else:
            book = entry[1]
            if entry[0] == "^": 
                text = re.sub(rf"\^ {book}",f"unknown{book}",text)
            elif f"{entry[0]} {book}" in numBook: 
                text = re.sub(f"{entry[0]} {book}",f"{num_to_text[entry[0]]}{book}",text)
    return text, replaced

def find_matches(text,replaced):
    text = text.split(" ")
    count = 0 
    matches = []
    current = []
    if len(replaced) == 0: 
        return []
    for idx, t in enumerate(text): 
        if t in abbrev or t in numBook_to_proper:
            t = re.sub(r"one|two|three|four|\^","",t)
            if len(matches) >= len(replaced): 
                break
            if t != abbrev_to_book[clean_word(replaced[len(matches)][0])]: 
                continue
            elif idx+1 >= len(text): 
                continue
            elif text[idx+1] != replaced[len(matches)][1]: 
                continue

            if len(current) > 1 and re.search(r"[0-9\*\^]",current[1]): 
                matches.append(" ".join(current))
                count += 1 
            if idx > 0 and t not in numBook_to_proper and len(current) == 0:
                if re.search(r"^[0-9*\^]+$", text[idx-1]): 
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
        elif len(current) > 0 and re.search(r"[0-9\*\^\,\&\-\—]+", t): 
            if re.search(r"[A-Za-z]",t):
                continue
            current.append(t)
        elif len(current)>0 and re.search(r'^ch$',t): 
            current.append(t)
        elif len(current) > 1 and re.search(r"[0-9\*\^]",current[1]):
            # have reached the end of a relevant citation  
            matches.append(" ".join(current))
            count += 1 
            current = []

    if len(current) > 1 and re.search(r"[0-9\*\^]",current[1]):
        # have reached the end of a relevant citation  
        matches.append(" ".join(current))

    return matches
        

'''Main function to actually extract all of the Biblical citations'''
def decompose(phrase): 
    # initialize lists to keep track of the properly formatted citations and possible formats that this code cannot currently account for 
    citations, outliers = [], []
    # only a chapter-level citation
    if re.search(r'^[a-z]+ [0-9\*\^]+$',phrase):
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
    if re.search(r'^[0-9\^]+ [0-9\*\^]+$',phrase):  
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
            elif re.search(r'[0-9\^]+ [0-9\^]+ [0-9\^]+$', passage): 
                citations.extend(othersimple(book, passage))
            # call simple() to account for "<chapter> <line1>"
            elif re.search(r'^[0-9\^]+ [0-9\^]+$',passage): 
                citations.append(simple(book, passage))
            else: 
                outliers.append(passage)
    
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
        if re.search(r'[0-9\^]+ [0-9\^]+ [0-9\^]+$',phrase):  
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
        elif re.search('four',book):
            book = re.sub('four','',book)
            final_citations.append(f'4 {book.capitalize()} {citation[1]}')
        elif re.search('unknown',book):
            book = re.sub('unknown','',book)
            final_citations.append(f'^ {book.capitalize()} {citation[1]}')
        else: 
            final_citations.append(f'{book.capitalize()} {citation[1]}')
    return final_citations 
