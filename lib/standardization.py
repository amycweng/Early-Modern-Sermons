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
    # print(match,replaced,text_str)
    count = 0 
    if len(match) > 0 and len(replaced) > 0: 
        for item, ref in match:
            orig_item = item 

            if re.search(r"ch \d+ v|\d+ ch \d+|\&c", item): 
                item = re.sub(r"ch|v|\&c", '',item)
                item = re.sub(r"\s+"," ",item)
            item = re.sub(r"([^0-9a-z\*\^])+$","",item.lower()) # remove trailing characters

            item = item.split(" ")
            if len(item) == 1: continue
            if len(item) == 2 and item[1] == ",": continue
            
            for idx, w in enumerate(item):
                if w == "i" and re.search(r"[0-9]+",orig_item): 
                    w = ""
                item[idx] = convert_numeral(w)
            item = re.sub(r"\s+"," ", " ".join(item)).strip(" ").split(" ")
            if not re.search(r"[0-9\*\^]",item[-1]): 
                continue

            if item[-1] == "ch": item[-1] = "" # philippians 3 1 ch case 
            if item[1] == "," and len(item) > 2: 
                # case of Ecclus, 25.16 in A09053
                book, nums = item[0], item[2:]
                item = [book]
                for num in nums: item.append(num) 
            item = format_chapter(item)
            if not re.search(r"[0-9\*\^]",item[1]): 
                continue

            text_str = re.sub(re.escape(orig_item), f"<REF{count}>",text_str, 1)
            count += 1
            if len(item) > 2 and re.search(r'^ch$',item[2]):
                # case of '1 K. 19. ch. 18.
                if len(item) < 4:
                    item = item[:3]
                else: 
                    chapter = item[3]
                    verse = item[1]
                    item[1],item[2],item[3] = chapter,verse,"" 
            # print(ref)
            # print(replaced[ref])
            # print(item)  
            fully_replaced.append(replaced[ref][0] + " " + " ".join(item[1:]))
            # print(fully_replaced)
            item = " ".join(item)
            decomposed = decompose(item)
            # print(decomposed)
            if len(decomposed[0]) > 0: 
                citations[count-1] = decomposed[0]
            if len(decomposed[1]) > 0: 
                outliers[count-1] = decomposed[1]
    return citations, outliers,fully_replaced

def clean_text(n): 
    # remove everything that is not an alphabetical character, integer, comma, ampersand, hyphen, asterisk, period, apostrophe or a single space
    n = re.sub(r'[^\w\d\,\&\-\—\*\(\)\^\.\'\"\: ]','',n)
    # strip out periods and colons 
    n = re.sub(r"\.|\:", " ",n)
    # strip away letters indicating verse or chapter, as well as the phrase 'of Sol' which follows 'Song' or 'Wisdom'
    n = re.sub(r"\b[lL]\b|\b[vV]erse\b|\b[vV]ers\b|\b[vV]er\b|\b[cC]ap\b|\b[Cc]hap\b|\b[cC]hapter\b|\bof\b|\bSol\b|\bSolomon\b"," ",n)
    if re.search(r"[\w+]\b[vc]\b[\w+]",n): # not surrounded by numbers; less likely it means verse and more that it is a roman numeral
        n = re.sub(r"\b[vc]\b"," ",n)
    
    # normalize conjunctions 
    n = re.sub(r"\band\b|\bet\b|\b\&\b",' & ', n)
    # replace all instances of multiple white spaces with a single space. 
    n = re.sub(r'\s+',' ',n)
    return n 

def clean_word(word): 
    word = word.lower()
    word = re.sub(r"[^A-Za-z\^]","",word)
    word = re.sub("v","u",word) # replace all v's with u's 
    word = re.sub("vv","w",word) # replace all vv's with w's 
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
    
    word = word.lower().strip(".") # strip period if Roman numeral 
    if not re.search(r'^(c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$', word): 
        return orig_word 
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
        return orig_word 

'''Standardize abbreviations'''
num_to_text = {'1':'one','2':'two','3':'three','4':'four'}
def replaceBook(text): 
    text = text.split(" ")
    replaced = []
    for idx, word in enumerate(text):   
        if re.search(r"^'",word): continue
        word = clean_word(text[idx])
        # initial i's have been converted to j's       
        if re.search(r"^js$|^ch$|^de$|^the$|^can$",word): continue # without capitalization and a period 
        # print(word)
        # identififed a valid abbreviation         
        if word in abbrev_to_book:
            if idx+1 in range(len(text)): # must be followed by at least one number 
                follow = convert_numeral(re.sub(r"([^\w\d\*\^])$","",text[idx+1])) # remove trailing punctuation
                if idx + 2 < len(text):
                    follow2 = convert_numeral(re.sub(r"([^\w\d\*\^])$","",text[idx+2]))
                    if not re.match(r'^[0-9\*\^]+$',follow):
                        if not (text[idx+1] == "," and re.match(r'^[0-9\*\^]+$',follow2)):
                            continue
                elif not re.match(r'^[0-9\*\^]+$',follow): 
                    continue  

            # elif idx > 0: # or preceded by at least one number 
            #     preceding = convert_numeral(re.sub(r"([^\w\d\*\^])$","",text[idx-1]))
            #     if not re.match(r'^[0-9\*\^]+$',preceding): 
            #         continue 
            else: 
                continue
            # update term to the normalized version 
            word = abbrev_to_book[word]
            orig = text[idx]
            if re.search(r'samuel|kings|chronicles|corinthians|thessalonians|timothy|peter|esdras|maccabees|john',word): 
                # do not convert 'ch' or 'the' if it is not preceded and succeeded by a number or caret 
                if idx > 0: 
                    # the case of "1, Kings"
                    prev = re.sub(r"([^\w\d\*\^])$","",text[idx-1]) # remove trailing punctuation
                    prev = convert_numeral(prev)
                    if re.search(r'^[1-4\^{1}]\.{0,}$',prev):
                        if idx-2 >= 0:
                            if text[idx-2] not in abbrev: 
                                text[idx-1] = prev
                                orig = text[idx-1] + " " + orig                               
                        else: 
                            text[idx-1] = prev
                            orig = text[idx-1] + " " + orig
                    elif re.search(r"^\d",text[idx]): 
                        # case of 2Cor 
                        num = re.findall(r"^\d",text[idx])[0]
                        if f"{num} {word}" in numBook: 
                            word = f"{num_to_text[num]}{word}"
                        else: continue
                    elif re.search(r"^[cC]h$|^[Tt]he$",orig): 
                        continue
                    
                elif re.search(r"^\d",text[idx]): 
                    num = re.findall(r"^\d",text[idx])[0]
                    if f"{num} {word}" in numBook: 
                        word = f"{num_to_text[num]}{word}"
                    else: continue
                elif re.search(r"^[cC]h$|^[Tt]he$",orig): 
                    continue
                
            replaced.append((orig,text[idx+1]))
            text[idx] = word  
    text = " ".join(text)
    numBooks = re.findall(r"(.*?) ([1-4\^{1}]) (samuel|kings|chronicles|corinthians|thessalonians|timothy|peter|john|esdras|maccabees)",text)
    numBooks.extend(re.findall(r"^([1-4\^{1}]) (samuel|kings|chronicles|corinthians|thessalonians|timothy|peter|john|esdras|maccabees)",text))
    # convert all numbered books into a single token ("1 corinthians" --> "onecorinthians")
    # print(numBooks)
    for entry in numBooks: 
        # deal with John 3 John 3 case
        if len(entry) == 3:  
            if entry[0].split(" ")[-1] in abbrev: 
                continue
            else: 
                book,num = entry[2], entry[1]
        else: 
            book, num = entry[1], entry[0]
        if num == "^":
            text = re.sub(rf"^\^ {book}| \^ {book}",f" unknown{book}",text)
        elif f"{num} {book}" in numBook: 
            text = re.sub(rf"\b{num} {book}|^{num} {book}",f" {num_to_text[num]}{book}",text)
    text = re.sub(r"\s+"," ",text)
    return text, replaced

def format_chapter(item):
    # accounting for case where the chapter number precedes the book's name
    if len(item) < 2: return item  
    if re.search(r"\d+", item[0]):
        chapter = item[0]
        item[0] = item[1] # book 
        item[1] = chapter 
    # case of <book> ch <num> <num>  
    if re.search(r'^ch$',item[1]):
        item[1] = ""
    return item

def find_matches(text,replaced):
    text = text.split(" ")
    matches = []
    current = []
    if len(replaced) == 0: 
        return []
    
    r_idx = 0
    for idx, t in enumerate(text): 
        if r_idx >= len(replaced): break
        check_crd_t = convert_numeral(t)
        if t in abbrev or t in numBook_to_proper:
            # print("at beginning",t, text[idx+1])

            adjacent_citation = False
            if len(current) > 1 and re.search(r"[0-9\*\^\,]",convert_numeral(format_chapter(current.copy())[1])):
                # print("added here",current)
                matches.append((" ".join(current),r_idx))
                r_idx += 1 
                current = []
                adjacent_citation = True 
            
            if r_idx >= len(replaced): break

            abbrev_t = re.sub(r"one|two|three|four|unknown","",t)
            if len(matches) >= len(replaced): 
                break
            
            rep = replaced[r_idx][0]
            if rep[0] == "^": rep = "".join(rep[1:])
            rep = clean_word(rep)
            if rep.strip(" ") not in abbrev_to_book: 
                continue
            if abbrev_t != abbrev_to_book[rep]:
                continue
            elif idx+1 >= len(text): 
                continue
            elif text[idx+1] != replaced[r_idx][1]:
                if text[idx+1] in numBook_to_proper or text[idx+1] in abbrev: 
                    r_idx += 1  
                continue

            if idx > 0 and t not in numBook_to_proper and len(current) == 0:
                if re.search(r"^[0-9]+$", text[idx-1]) and not adjacent_citation: 
                    # check the next two numbers 
                    if (idx+1) < len(text) and (idx+2) < len(text):
                        t1,t2 = convert_numeral(text[idx+1]), convert_numeral(text[idx+2])
                        if re.search(r"^[0-9]+$", t1) and re.search(r"^[0-9]+$", t2): 
                            current = [t]
                        else: 
                            current = [text[idx-1], t] 
                    else: 
                        current = [text[idx-1], t] 
                else: 
                    current = [t]
            else: 
                current = [t]
        
        elif len(current) > 0 and re.search(r"^[0-9\*\^\,\&\-\—]+$", check_crd_t): 
            # starts with a numeral, illegible character/word, or is punctuation 
            # print("a",t,current)
            current.append(t)
        elif len(current)>0 and re.search(r'^ch$',t): 
            # print("b",t)
            current.append(t)
        elif len(current) > 1 and re.search(r"[0-9\*\^\,]",convert_numeral(format_chapter(current.copy())[1])):
            # have reached the end of a relevant citation  
            matches.append((" ".join(current),r_idx))
            r_idx += 1 
            # print("added there",t)
            current = []

    if len(current) > 1 and re.search(r"[0-9\*\^\,]",convert_numeral(format_chapter(current.copy())[1])):
        # have reached the end of a relevant citation  
        matches.append((" ".join(current),r_idx))

    return matches
        

'''Main function to actually extract all of the Biblical citations'''
def decompose(phrase): 
    # initialize lists to keep track of the properly formatted citations and possible formats that this code cannot currently account for 
    citations, outliers = [], []
    # only a chapter-level citation
    phrase = phrase.strip(" ")
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
    if re.search(r'^[0-9\^\*]+ [0-9\*\^]+$',phrase):  
        citations.append(simple(book, phrase))
    # if there are ampersands in the text, split the text up by the ampersands 
    elif re.search('&',phrase): 
        passages = phrase.split(' & ')
        has_chapter = None 
        for passage in passages:
            passage = passage.strip()
            if re.search('\-', passage):
                c, o = hyphen(book,passage)
                citations.extend(c)
                outliers.extend([f'{book} {item}' for item in o])
                # if len(o): # # print(orig_phrase)
            elif re.search('\,',passage): 
                citations.extend(comma(book,passage))
            # call othersimple() to account for the case of "<chapter> <line1> <line2>" 
            elif re.search(r'[0-9\^\*]+ [0-9\^\*]+ [0-9\^\*]+$', passage): 
                citations.extend(othersimple(book, passage))
            # call simple() to account for "<chapter> <line1>"
            elif re.search(r'^[0-9\^\*]+ [0-9\^\*]+$',passage): 
                citations.append(simple(book, passage))
                has_chapter = passage.split(" ")[0]
            elif len(passage.split(" ")) == 1: 
                if has_chapter is None:
                    # deal with the John 8 & 1 or Psalms 33 & 35 & 45 case 
                    citations.append(f"{book} {passage}")
                else: 
                    citations.append(f"{book} {has_chapter}.{passage}")
            else:  
                outliers.append(f"{book}: {passage}")
    
    # if there are no ampersands but there are hyphens
    elif re.search('-', phrase):
        c, o = hyphen(book,phrase)
        citations.extend(c)
        outliers.extend([f'{item}' for item in o])
        # if len(o): # # print(orig_phrase)
    # if there are no ampersands & hyphens but there are commas  
    elif re.search(',',phrase): 
        citations.extend(comma(book, phrase))
    # else, there is a format that this code cannot account effectively for 
    else: 
        # special cases; see the othersimple function description for examples
        if re.search(r'[0-9\^\*]+ [0-9\^\*]+ [0-9\^\*]+$',phrase):  
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
            # # # print(orig_phrase)
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
