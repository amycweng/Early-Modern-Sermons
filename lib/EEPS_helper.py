import re 
import os 
TCP = '/Users/amycweng/DH/TCP'

def isSermon(section_name): 
    if re.search(r"^sermon",section_name): 
        return True 
    return False 

def findTextTCP(id):
    if re.match('B1|B4',id[0:2]):
        path = f'{TCP}/P2{id[0:2]}/{id}.P4.xml'
    else: 
        if f'{id}.P4.xml' in os.listdir(f'{TCP}/P1{id[0:2]}'):
            path = f'{TCP}/P1{id[0:2]}/{id}.P4.xml'
        elif f'{id}.P4.xml' in os.listdir(f'{TCP}/P2{id[0:2]}'): 
            path = f'{TCP}/P2{id[0:2]}/{id}.P4.xml'
    return path 

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
        return num
    else: 
        return orig_word 

def get_page_number(token): 
    if re.search(r"\bPAGEIMAGE[\d+\w+]",token): 
        token = token.split("PAGEIMAGE")[-1]
        page_type = "PAGEIMAGE"
    elif re.search(r"\bPAGE[\d+\w+]",token): 
        token = token.split("PAGE")[-1]
        page_type = "PAGE"
    num = convert_numeral(token)
    if token == num:
        return page_type,int(num),'' 
    return page_type,int(num),token 
    
# print(get_page_number("PAGEIMAGEXXVI"))
# print(get_page_number("PAGEXXVI"))
# print(re.search(r"\bPAGE[\d+\w+]","PAGEXXVI"))


def find_curr_page(idx, adorned):
    prev_page = None 
    prev_page_type = None 
    idx_to_find_page = idx
    while prev_page is None: 
        if idx_to_find_page >= 0: 
            temp = adorned[idx_to_find_page]
            temp = temp.strip("\n").split("\t")
            if len(temp) == 0: continue
            if re.search(r"\bPAGE[\d+\w+]",temp[0]):
                prev_page_type, prev_page, previsRoman = get_page_number(temp[0])
            else: 
                idx_to_find_page -= 1 
        else: 
            break
    next_page = None 
    next_page_type = None 
    idx_to_find_page = idx
    while next_page is None: 
        if idx_to_find_page < len(adorned): 
            temp = adorned[idx_to_find_page]
            temp = temp.strip("\n").split("\t")
            if len(temp) == 0: continue
            if re.search(r"\bPAGE[\d+\w+]",temp[0]):
                next_page_type, next_page, nextisRoman = get_page_number(temp[0])
            else: 
                idx_to_find_page -= 1
        else: 
            break
    
    # compare previously known page and next page to deduct current page number 
    if prev_page is None and next_page is not None: 
        # at the very beginning 
        curr_page = f"{next_page_type}{next_page-1}"
    elif next_page is not None and (prev_page + 1) != next_page: 
        # when the extracted sections are not consecutive
        curr_page = f"{next_page_type}{next_page-1}"
    else: 
        curr_page = f"{prev_page_type}{prev_page}{previsRoman}"
    return curr_page