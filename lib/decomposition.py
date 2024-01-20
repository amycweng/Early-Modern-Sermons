
import re 
'''
Helper function to extract citations from a marginal note that contains commas 
e.g, "isaiah 1 2, 3, 4, 5 5" --> "isaiah 1.2", "isaiah 1.3", "isaiah 1.4", "Isaiah 5.5"
'''
def comma(book, passage): 
    phrases = []
    # make sure there is always at least one space after a comma
    passage = re.sub(',',', ',passage)
    # remove duplicate spaces 
    passage = re.sub('  ',' ',passage)  
    passage = re.sub(rf'{book}| ,','',passage).strip()
    nums = passage.split(' ')
    chapter = nums[0]
    for num in nums[1:]: 
        if ',' in num or num == nums[-1] or num == "*": 
            verse = num.strip('\,') 
            phrases.append(f'{book} {chapter}.{verse}')
        else: 
            chapter = num
    return phrases

'''
Helper function to extract citations from a marginal note that does not contain commas

Target format is "<book> <chapter> <verse>" 
'''
def simple(book, passage): 
    # the simple case of just having "<book> <chapter> <verse>" 
    nums = re.findall(r'[0-9\*]+',passage)
    return f'{book} {nums[0]}.{nums[1]}'

'''
Helper function to extract citations from a marginal note that does not contain commas
Target format is "<book> <chapter> <verse1> <verse2>" or "<book> <chapter1> <verse1> <chapter2> <verse2>" 
    or "<book> <chapter> <verse1> <verse2> <verse3> <verse4>" 
'''
def othersimple(book, passage): 
    phrases = []
    if re.search('[0-9\*]+ [0-9\*]+ [0-9\*]+ [0-9\*]+ [0-9\*]+', passage): 
        passage = re.findall('([0-9\*]+) ([0-9\*]+) ([0-9\*]+) ([0-9\*]+) ([0-9\*]+)',passage)[0]
        phrases.append(f'{book} {passage[0]}.{passage[1]}')
        phrases.append(f'{book} {passage[0]}.{passage[2]}')
        phrases.append(f'{book} {passage[0]}.{passage[3]}')
        phrases.append(f'{book} {passage[0]}.{passage[4]}')
    elif re.search('[0-9\*]+ [0-9\*]+ [0-9\*]+ [0-9\*]+', passage): 
        passage = re.findall('([0-9\*]+) ([0-9\*]+) ([0-9\*]+) ([0-9\*]+)',passage)[0]
        phrases.append(f'{book} {passage[0]}.{passage[1]}')
        phrases.append(f'{book} {passage[2]}.{passage[3]}')
    else: 
        passage = re.findall('([0-9\*]+) ([0-9\*]+) ([0-9\*]+)',passage)[0]
        phrases.append(f'{book} {passage[0]}.{passage[1]}')
        phrases.append(f'{book} {passage[0]}.{passage[2]}')
    return phrases 

'''
These are cases of continuous citation, 
e.g, "Genesis 3 9-14" --> "Genesis 3.9", "Genesis 3.10", etc. until "Genesis 3.14"
'''
def continuous(book, phrase):
    phrases = [] 
    nums = re.findall(r'[0-9\*]+',phrase)
    chapter, start, end = nums[0], int(nums[1]), int(nums[2])
    for idx in range(end-start+1): 
        phrases.append(f'{book} {chapter}.{start+idx}')
    return phrases

'''
These are cases in which hyphens divide discrete citations, 
e.g., "Acts 5 12, 14 -8 6 -9 35, 42" --> "Acts 5.12", "Acts 5.14", "Acts 8.6", "Acts 9.35" and "Acts 9.42" 
'''
def hyphen(book,passage): 
    citations, outliers = [], []
    passage = re.sub(r'\s{0,}-\s{0,}','-',passage)
    passage = passage.strip().strip('-')
    if len(re.findall(r'[0-9\*]+',passage)) == 3:
        # case of 'revelation 1, 13-16' or 'proverbs 8 18,-21' 
        # strip the commas out 
        passage = re.sub(",","",passage)
    if re.search('[0-9\*]+-[0-9\*]+-[0-9\*]+',passage) or re.search('[0-9\*]+ [0-9\*]+ [0-9\*]+-[0-9\*]+',passage): 
        # cases like psalms 2 4-4 4-4 9-5 19-6 14-13 14-22-29 in A85487 
        # and 'john 5 24 3-18'
        # which is just too difficult to interpret
        outliers.append(f'{book} {passage.strip()}')
        return citations, outliers 
    if re.search('^[0-9\*]+ [0-9\*]+, [0-9]+-[0-9]+$|^[0-9\*]+ [0-9\*]+, [0-9\*]+, [0-9]+-[0-9]+$',passage): 
        nums = re.findall('[0-9\*]+',passage)
        citations.extend(comma(book, ' '.join(nums[:-2])))
        citations.extend(continuous(book,f'{nums[0]} {nums[2]}-{nums[3]}'))
        return citations, outliers
    if re.search('^[0-9\*]+-[0-9\*]+$',passage):
        if "*" in passage: 
            outliers.append(f'{book} {passage.strip()}')
        else: 
            nums = re.findall('[0-9]+',passage)
            for num in range(int(nums[0]),int(nums[1])+1): 
                citations.append(f"{book} {num}")
        return citations, outliers
    
    parts = passage.split('-')
    idx = 0
    while idx < len(parts):
        p = parts[idx]
        if idx+1 < len(parts) and ' ' not in parts[idx+1].strip(): 
            # there are hyphens indicating a range of citations 
            actual = f'{parts[idx].strip()}-{parts[idx+1].strip()}'
            if re.search(r'^[0-9\*]+ [0-9]+-[0-9]+$',actual): 
                citations.extend(continuous(book, actual))
                idx += 2
            elif re.search('^[0-9]+-[0-9]+$',actual):
                idx += 1 
                citations.append(f'{book} {parts[idx].strip()}.{parts[idx+1].strip()}')
            else: 
                idx += 1
                outliers.append(actual)
        elif re.search('\,',p): 
            citations.extend(comma(book,p))
            idx += 1
        elif re.search(r'[0-9\*]+ [0-9\*]+ [0-9\*]+$', p): 
            citations.extend(othersimple(book, p))
            idx += 1
        elif re.search(r'[0-9\*]+ [0-9\*]+$',p): 
            citations.append(simple(book, p))
            idx += 1 
        else: 
            outliers.append(p)
            idx += 1 
    return citations, outliers 


