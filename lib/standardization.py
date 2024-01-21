'''Text cleaning and conversions'''
import re,csv
import sys 
sys.path.append('../')
from lib.abbreviations import * 
from lib.decomposition import * 

def clean_text(n): 
    # remove foreign language indicators 
    n = re.sub(rf"〈 in non-Latin alphabet 〉", "",n)
    # replace all periods with spaces and convert to lower case 
    n = re.sub(r'([\.:])',r' ',n).lower()
    # replace all special characters with asterisks 
    n = re.sub('〈◊〉|•|▪','*',n)
    # remove everything that is not an alphabetical character, integer, comma, ampersand, hyphen, illegible char, or a single space
    n = re.sub(r'[^a-z0-9\,\&\-\—\* ]','',n)
    # strip away letters indicating verse or chapter 
    n = re.sub(r"\bc\b|[^a-z*]l\b|[^a-z* ]v\b|\bverse\b|\bver\b|\bcap\b|\bchap\b|\bchapter\b","",n)
    # normalize ampersands and conjunctions 
    n = re.sub(r"\band\b|\&ampc\b|\&amp\b|\bet\b",'&', n)
    # replace all instances of multiple white spaces with a single space. 
    n = re.sub(r'\s+',' ',n)
    return n 

def clean_word(word): 
    word = word.lower().strip(".")
    if not re.match(r'^[0-9]+$',word): 
        # strip commas after non-numeric tokens 
        word = word.strip(",")
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
    if not re.search(r'^(c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$', word): 
        return word 
    num = 0
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
def replaceBook(note): 
    note = note.split(" ")
    for idx, word in enumerate(note): 
        if re.search(r"^de",word): 
            if idx+1 in range(len(note)): 
                # 'de' must be followed by at least one number to be considered an abbreviation  
                if not re.match(r'\b[0-9*]+\b',note[idx+1]): 
                    continue 
        note[idx] = convert_numeral(word)
        word = clean_word(word)
        # identififed a valid abbreviation         
        if word in abbrev_to_book:
            # update term to the normalized version 
            word = abbrev_to_book[word]
            # non-scriptural references to an epistle
            if word == 'epistle' and idx > 0:
                continue
            elif re.search('samuel|kings|chronicles|corinthians|thessalonians|timothy|peter',word): 
                # do not convert 'ch' or 'the' if it is not preceded by a number or an asterisk 
                if idx > 0: 
                    # the case of "1, Kings"
                    note[idx-1] = note[idx-1].strip(",")
                    if not re.search(r'^[1-3\*{1}]$',note[idx-1]):
                        continue 
                else: 
                    continue
            note[idx] = word  
    note = " ".join(note)
    numBooks = re.findall(r"([1-3\*{1}]) (samuel|kings|chronicles|corinthians|thessalonians|timothy|peter|john)",note)
    # convert all numbered books into a single token ("1 corinthians" --> "onecorinthians")
    for num, book in numBooks: 
        if num == "*": 
            note = re.sub(f"\* {book}",f"unknown{book}",note)
        elif f"{num} {book}" in numBook: 
            note = re.sub(f"{num} {book}",f"{num_to_text[num]}{book}",note)
    return note

'''Main function to actually extract all of the Biblical citations'''
def findCitations(phrase): 
    # initialize lists to keep track of the properly formatted citations and possible formats that this code cannot currently account for 
    citations, outliers = [], []
    # only a chapter-level citation
    if re.search(r'^[a-z]+ [0-9*]+$',phrase):
        citations.append(phrase.strip())
        citations = proper_title(citations)
        return citations, outliers 
     
    book = phrase.split(' ')[0]
    phrase = re.sub(book,'',phrase).strip()
    if re.search('—|\,|\,$',phrase): 
        phrase = re.sub('—','-',phrase)
        phrase = re.sub('\,-','-',phrase)
        phrase = re.sub('\,$| \,$','',phrase)
    
    # if the note is simply a single citation, call simple() to append the citation to the list of citations 
    if re.search(r'^[0-9\*]+ [0-9\*]+$',phrase):  
        citations.append(simple(book, phrase))
    # if there are ampersands in the note, split the note up by the ampersands 
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


def test(): 
    outputs = []
    with open('../assets/sermons_marginalia.csv', 'r') as file:          
        notes = csv.reader(file, delimiter=',')
        citations, outliers = [],[]
        for idx, entry in enumerate(notes):
            if idx > 491139: break
            if idx < 491139: continue
            # output dictionary 
            info_dict = {'idx':idx, 'tcpID':entry[0],'citations':None, 'outliers':None,'original':entry[-1]}
            # get note text 
            n = entry[-1]
            n = clean_text(n)
            # find possible citations 
            n = replaceBook(n)
            print(n)
            match = re.findall(r'([a-z*]+ [\d*\,\&\-\— ]+)', n)
            # print(match)
            c,o = [],[]
            if len(match) > 0: 
                for item in match:
                    item = item.strip(" ")
                    item = re.sub(r"([^0-9a-z*])$","",item)
                    item = item.split(" ")
                    book = item[0]
                    if len(item) == 2 and item[1] == "&":
                        continue # trivial case of "<word> &"
                    item = " ".join(item)
                    if book not in abbrev and book not in numBook.values():
                        o.append(item) 
                    else: 
                        print(item)
                        decomposed = findCitations(item)
                        print(idx, decomposed)
                        c.extend(decomposed[0])
                        o.extend(decomposed[1])
                info_dict['citations'] = "; ".join(c) 
                info_dict['outliers'] = "; ".join(o)
                outputs.append(info_dict)
                citations.extend(c)
                outliers.extend(o)
            if (idx+1) % 100000 == 0: 
                print(f"Processed {idx+1} entries")

# test()