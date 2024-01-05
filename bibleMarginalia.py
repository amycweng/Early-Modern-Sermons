'''
@author Amy Weng 

This code extracts biblical citations from the marginal notes, i.e., marginalia, encoded in TCP XML files under the <note> tags. 

Takes in a single TCP XML file and outputs the following:
    1. A list of singular citations (i.e., "<book> <chapter> <line>"), 
    2. A list of citations that cannot be properly formatted by the current code, and 
    3. A list of possible citations, i.e., "<word> <int1> <int2>" where <word> is not found in the standardizer bible dictionary. The standardizer dict can then be updated accordingly. 
'''
import re 
from collections import Counter 
from bs4 import BeautifulSoup, SoupStrainer
from bible import *

'''Standardizes known abbreviations'''
def replaceBible(text):
    for book,variations in bible.items():
        for v in variations: 
            if re.search(rf'\b{v}\b|^{v}\b', text): 
                return True,re.sub(rf'\b{v}\b|^{v}\b', book, text)
    return False,text

'''Converts numbered books into a single string, e.g., '1 corinthians' to '1corinthians' for ease of processing'''
def replaceNumBook(text):
    for key,value in numBook.items():
        if key in text: 
            return re.sub(rf'{key}', value, text)
    return None

# Get all of the names of the Bible's books 
bibleBooks = [x for x in bible.values()]
bibleBooks.extend([x for x in numBook.values()])

'''Master function to extract all the citations from the marginalia of one file.''' 
def getMarginalia(filepath):
    # read the input XML file 
    with open(filepath,'r') as file: 
        data = file.read()
    # use soupstrainer to only parse the main text body (excluding dedicatory materials etc)
    # each xml file only has one of these, so there will only be one none-empty soup for each file 
    bodyText1 = SoupStrainer("div1",attrs={"type":"text"})
    bodyText2 = SoupStrainer("div1",attrs={"type":"part"})
    bodyText3 = SoupStrainer("div1",attrs={"type":"sermon"})
    bodyText4 = SoupStrainer("div1",attrs={"type":"exegesis"})
    # create a parsed tree, i.e., soup, of the body text using the html parser
    # (the file is an XML but the HTML parser is sufficient.)
    soup1 = BeautifulSoup(data,parse_only=bodyText1,features='html.parser')
    soup2 = BeautifulSoup(data,parse_only=bodyText2,features='html.parser')
    soup3 = BeautifulSoup(data,parse_only=bodyText3,features='html.parser')
    soup4 = BeautifulSoup(data,parse_only=bodyText4,features='html.parser')
    # only one of these soups will actually have content 
    soups = [soup1, soup2,soup3,soup4]
    # phrases with known scriptural abbreviations 
    citations = []
    # phrases with unknown abbreviations 
    unknown = []
    # iterate through every note tag of this file 
    for soup in soups: 
        for note in soup.find_all('note'):
            # find illegible parts  
            gaps,gapNote = [], str(note)
            foundGap = False
            for gap in note.find_all('gap'):
                gapNote = re.sub(str(gap),'*',gapNote)
                foundGap = True

            # we only care if the illegible characters are part of a number 
            if foundGap: 
                gapNote = gapNote.split(' ')
                for g in gapNote: 
                    if re.search('\d+\*|\*\d+',g): 
                        gaps.append(g)
            
            if 'place="marg"' not in str(note): 
                # skip all non-marginal notes 
                continue
            n = note.text
            # ensure that we preserve the illegible characters that are in numbers
            # to prevent getting false citations 
            for gap in gaps:
                noGap = re.sub('\*','',gap) 
                n = re.sub(noGap,gap,n)
            # replace all periods with spaces. This is to make sure that all citations are 
            # in the format of "<book> <chapter> <line>", i.e., "Ecclesiastes 9 4". 
            # Some citations are originally inconsistently formatted as "<book> <chapter>.<line>" at times 
            # and "<book> <chapter>. <line>." at other times, so replacing periods with spaces is the first step to standardizing all the citation formats 
            n = re.sub(r'(\.)',r' ',n).lower()
            # remove everything that is not an alphabetical character, integer, comma, ampersand, illegible char, or a single space
            n = re.sub(r'[^a-z0-9\,\&\-\—\* ]','',n)
            # replace all instances of "and" with ampersands 
            n = re.sub(r'\band\b','&', n)
            # next, replace all instances of two or more spaces with a single space. 
            n = re.sub(r'\s+',' ',n)

            # find instances of possible numbered books 
            pattern1 = re.findall(rf'([1|2|3] [a-z]+ [^a-z]+)',n)
            if len(pattern1) > 0: 
                for item in pattern1: 
                    if re.search(rf'\d+ \d+',item): 
                        found, standard = replaceBible(item)
                        # if there is a known abbreviation, standardize and append to appropriate list  
                        if found: 
                            standard = replaceNumBook(standard)
                            # delete the current instance from the entire string
                            # this prevents repeats when we process pattern2 citations below  
                            n = re.sub(item,' ',n) 
                            citations.append(standard)
                        else: 
                            # there is an unknown abbreviation
                            item = item.split(' ')
                            unknown.append(item[1])

            # find instances of other scriptural citations 
            pattern2 = re.findall(rf'([a-z]+ [^a-z]+)', n)
            if len(pattern2) > 0: 
                for item in pattern2: 
                    if re.search(rf'\d+ \d+',item): 
                        found, standard = replaceBible(item) 
                        # if there is a known abbreviation, standardize and append to appropriate list  
                        if found and standard:
                            citations.append(standard)
                        else: 
                            # there is an unknown abbreviation
                            item = item.split(' ')
                            unknown.append(item[0])
    # call another function to actually return a list of actual scriptural citations 
    citations = findCitations(citations)
    # return both the list of citations and unknown abbreviations
    return citations,Counter(unknown)

'''
Helper function to extract citations from a marginal note that contains commas 
e.g, "isaiah 1 2, 3, 4, 5 5" --> "isaiah 1:2", "isaiah 1:3", "isaiah 1:4", "Isaiah 5:5"
'''
def comma(book, passage): 
    phrases = []
    # make sure there is always at least one space after a comma
    passage = re.sub(',',', ',passage)
    # remove duplicate spaces 
    passage = re.sub('  ',' ',passage)  
    passage = re.sub(rf'{book}| ,','',passage).strip()
    nums = passage.split(' ')
    chapter,line = nums[0],0
    for num in nums[1:]: 
        if ',' in num or num == nums[-1]: 
            line = num.strip('\,') 
            phrases.append(f'{book} {chapter}:{line}')
        else: 
            chapter = num
    return phrases

'''
Helper function to extract citations from a marginal note that does not contain commas

Target format is "<book> <chapter> <line>" 
'''
def simple(book, passage): 
    # the simple case of just having "<book> <chapter> <line>" 
    nums = re.findall('\d+',passage)
    return f'{book} {nums[0]}:{nums[1]}'

'''
Helper function to extract citations from a marginal note that does not contain commas
Target format is "<book> <chapter> <line1> <line2>" or "<book> <chapter1> <line1> <chapter2> <line2>" 
    or "<book> <chapter> <line1> <line2> <line3> <line4>" 
'''
def othersimple(book, passage): 
    phrases = []
    if re.search('\d+ \d+ \d+ \d+ \d+', passage): 
        passage = re.findall('(\d+) (\d+) (\d+) (\d+) (\d+)',passage)[0]
        phrases.append(f'{book} {passage[0]}:{passage[1]}')
        phrases.append(f'{book} {passage[0]}:{passage[2]}')
        phrases.append(f'{book} {passage[0]}:{passage[3]}')
        phrases.append(f'{book} {passage[0]}:{passage[4]}')
    elif re.search('\d+ \d+ \d+ \d+', passage): 
        passage = re.findall('(\d+) (\d+) (\d+) (\d+)',passage)[0]
        phrases.append(f'{book} {passage[0]}:{passage[1]}')
        phrases.append(f'{book} {passage[2]}:{passage[3]}')
    else: 
        passage = re.findall('(\d+) (\d+) (\d+)',passage)[0]
        phrases.append(f'{book} {passage[0]}:{passage[1]}')
        phrases.append(f'{book} {passage[0]}:{passage[2]}')
    return phrases 

'''
These are cases of continuous citation, 
e.g, "Genesis 3 9-14" --> "Genesis 3:9", "Genesis 3:10", etc. until "Genesis 3:14"
'''
def continuous(book, phrase):
    phrases = [] 
    nums = re.findall(r'\d+',phrase)
    chapter, start, end = nums[0], int(nums[1]), int(nums[2])
    for idx in range(end-start+1): 
        phrases.append(f'{book} {chapter}:{start+idx}')
    return phrases

'''
These are cases in which hyphens divide discrete citations, 
e.g., "Acts 5 12, 14 -8 6 -9 35, 42" --> "Acts 5:12", "Acts 5:14", "Acts 8:6", "Acts 9:35" and "Acts 9:42" 
'''
def hyphen(book,passage): 
    citations, outliers = [], []
    passage = re.sub(' -|- | - ','-',passage)
    passage = passage.strip().strip('-')
    if re.search('\d+-\d+-\d+',passage): 
        # cases like psalms 2 4-4 4-4 9-5 19-6 14-13 14-22-29 in A85487 
        # which is just too difficult to interpret
        outliers.append(f'{book} {passage.strip()}')
        return citations, outliers 
    if re.search('^\d+ \d+, \d+-\d+$|^\d+ \d+, \d+, \d+-\d+$',passage): 
        nums = re.findall('\d+',passage)
        citations.extend(comma(book, ' '.join(nums[:-2])))
        citations.extend(continuous(book,f'{nums[0]} {nums[2]}-{nums[3]}'))
        return citations, outliers
    parts = passage.split('-')
    idx = 0
    while idx < len(parts):
        p = parts[idx]
        if idx+1 < len(parts) and ' ' not in parts[idx+1].strip(): 
            # there are hyphens indicating a range of citations 
            actual = f'{parts[idx].strip()}-{parts[idx+1].strip()}'
            if re.search(r'^\d+ \d+-\d+$',actual): 
                citations.extend(continuous(book, actual))
                idx += 2
            elif re.search('^\d+-\d+$',actual):
                idx += 1 
                citations.append(f'{book} {parts[idx].strip()}:{parts[idx+1].strip()}')
            else: 
                idx += 1
                outliers.append(actual)
        elif re.search('\,',p): 
            citations.extend(comma(book,p))
            idx += 1
        elif re.search(r'\d+ \d+ \d+$', p): 
            citations.extend(othersimple(book, p))
            idx += 1
        elif re.search(r'\d+ \d+$',p): 
            citations.append(simple(book, p))
            idx += 1 
        else: 
            outliers.append(p)
            idx += 1 
    return citations, outliers 

'''Main function to actually extract all of the Biblical citations'''
def findCitations(notes_list): 
    # initialize lists to keep track of the properly formatted citations and possible formats that this code cannot currently account for 
    citations, outliers = [], []

    # iterate through every single item of the notes_list
    for phrase in notes_list: 
        if phrase == None: continue
        # if there is no instance of the book followed by at least two decimals, skip to the next instance   
        if not re.search(r'[a-z]+ \d+ \d+',phrase): continue
        book = phrase.split(' ')[0]
        phrase = re.sub(book,'',phrase).strip()
        if re.search('—|\,|\,$',phrase): 
            phrase = re.sub('—','-',phrase)
            phrase = re.sub('\,-','-',phrase)
            phrase = re.sub('\,$| \,$','',phrase)
        
        orig_phrase = phrase
        # if the note is simply a single citation, call simple() to append the citation to the list of citations 
        if re.search(r'^\d+ \d+$',phrase):  
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
                elif re.search(r'\d+ \d+ \d+$', passage): 
                    citations.extend(othersimple(book, passage))
                # call simple() to account for "<chapter> <line1>"
                elif re.search(r'^\d+ \d+$',passage): 
                    citations.append(simple(book, passage))
        
        # if there are ampersands but there are hyphens
        elif re.search('-', phrase):
            c, o = hyphen(book,phrase)
            citations.extend(c)
            outliers.extend([f'{book} {item}' for item in o])
            # if len(o): print(orig_phrase)
        # if there are no ampersands & hyphens but there are commas  
        elif re.search(',',phrase): 
            citations.extend(comma(book, phrase))
        # else, there is a format that this code cannot account effectively for 
        else: 
            # special cases; see the othersimple function description for examples
            if re.search(r'\d+ \d+ \d+$',phrase):  
                citations.extend(othersimple(book, phrase))
            # hard coding some special cases for the charity sermons dataset
            elif '119 5 10 32 57 93 106 173 40' == phrase and book == 'psalms': 
                # original is Psal 119.5 10.32.57.93.106 173.40.
                citations.extend(['psalms 119:5', 'psalms 10:32', 'psalms 10:57','psalms 10:93','psalms 10:106', 'psalms 173:40'])
            elif '8 1 3 5 8 9' in phrase and 'romans' in book: 
                # original is Rm. 8.1.3 5.8.9
                citations.extend(['romans 8:1','romans 8:2', 'romans 8:3', 'romans 5:8', 'romans 5:9'])
            else: 
                outliers.append(f'{book} {phrase}')
                # print(orig_phrase)
    # pretty formatting 
    citations, outliers = proper_title(citations, outliers)
    # return both citations and outliers  
    return citations, outliers

'''Convert the numbered books back into their original formats, i.e., "Onecorinthians" to "1 Corinthians"'''
def proper_title(citations_list, pesky_list): 
    final_citations = []
    final_pesky = []
    for citation in citations_list:
        citation = re.sub(f'\,','',citation)
        if re.search('\*',citation): 
            pesky_list.append(citation)
            continue
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
        else: 
            final_citations.append(f'{book.capitalize()} {citation[1]}')

    for citation in pesky_list: 
        citation = re.sub(f'\,','',citation)
        book = citation.split(' ')[0] 
        citation = re.sub(book,'',citation)
        if re.search('one',book):
            book = re.sub('one','',book)
            final_pesky.append(f'1 {book.capitalize()} {citation}')
        elif re.search('two',book):
            book = re.sub('two','',book)
            final_pesky.append(f'2 {book.capitalize()} {citation}')
        elif re.search('three',book):
            book = re.sub('three','',book)
            final_pesky.append(f'3 {book.capitalize()} {citation}')
        else: 
            final_pesky.append(f'{book.capitalize()} {citation}')
    return final_citations, final_pesky 

# ignore the HTML warning from BeautifulSoup 
import warnings
warnings.simplefilter("ignore", UserWarning)

# # main function to take a single input file and print out each citation & its count, the citations that cannot be properly formatted, and the outliers 
# if __name__ == '__main__': 
#     # sample filepath: /Users/amycweng/Digital Humanities/TCP/P1A6/A68088.P4.xml
#     # /Users/amycweng/Digital Humanities/TCP/P2A7/A72143.P4.xml
#     # /Users/amycweng/Digital Humanities/TCP/P1A0/A01523.P4.xml
#     # /Users/amycweng/Digital Humanities/TCP/P2A8/A85487.P4.xml
#     # /Users/amycweng/Digital Humanities/TCP/P1A0/A01554.P4.xml
#     filepath = input('Enter the path of a TCP XML file: ')
#     citations, unknown = getMarginalia(filepath)
#     print(f'Here are the biblical passages cited in the margins of this book and formatted as singular lines: {Counter(citations[0])}\n')
#     print(f'Here are the citations that cannot be formatted at the moment: {citations[1]}\n')
#     print(f'Here are unknown abbreviations that are followed by at least two numbers: {unknown}. Please update the standardizer dictionary accordingly.')