import re 
import os 
TCP = '/Users/amycweng/DH/TCP'

def isSermon(section_name): 
    if re.search(r"^sermon",section_name): 
        return True 
    return False 

def is_page(item):
    if re.search(r"^PAGE\d+\b",item): 
        return True 
    return False 
    
def is_page_image(item):
    if re.search(r"^PAGEIMAGE\d+\b",item): 
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

    word = word.lower()
    word = re.sub("\.","",word) # strip period if Roman numeral 
    word = re.sub("j|J","i",word)
    # up to 4 because there are "iiii" and "xxxx"
    if not re.search(r'^(c{0,4})(xc|xl|l?x{0,4})(xi|x|ix|iv|vi|v?i{0,4})$', word): 
        if word == "lxc": 
            return 90
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

# print(convert_numeral('xlx'))
# print(convert_numeral("cxlvii"))
# print(convert_numeral("cxlxi"))
# print(convert_numeral("xci"))
# print(convert_numeral("lxc"))
# print(convert_numeral("lxxxix"))

def isNumeral(item):
    if re.match(r"[0-9\•]+",item): 
        return True 
    else: 
        num = convert_numeral(item)
        if isinstance(num,int): 
            return True
    return False


def get_page_number(token): 
    if is_page_image(token): 
        token = token.split("PAGEIMAGE")[-1]
        page_type = "PAGEIMAGE"
    elif is_page(token): 
        token = token.split("PAGE")[-1]
        page_type = "PAGE"
    num = convert_numeral(token)
    if token == num:
        return page_type,int(num),'' 
    return page_type,int(num),token 
    
# print(get_page_number("PAGEIMAGEXXVI"))
# print(get_page_number("PAGEXXVI"))
# print(re.search(r"\bPAGE[\d+\w+]","PAGEXXVI"))


def find_curr_page(idx, adorned, prev_page, isImage=False):
    prev_page_type = None 
    previsRoman = ''
    idx_to_find_page = idx
    while prev_page is None: 
        if idx_to_find_page >= 0: 
            temp = adorned[idx_to_find_page]
            temp = temp.strip("\n").split("\t")
            if len(temp) == 0: continue
            if is_page_image(temp[0]) and isImage:
                prev_page_type, prev_page, previsRoman = get_page_number(temp[0])
            elif is_page(temp[0]) and not isImage: 
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
            if is_page_image(temp[0]) and isImage:
                next_page_type, next_page, nextisRoman = get_page_number(temp[0])
            elif is_page(temp[0]) and not isImage: 
                next_page_type, next_page, nextisRoman = get_page_number(temp[0])
            else: 
                idx_to_find_page += 1
        else: 
            break
    # compare previously known page and next page to deduct current page number 
    if prev_page is None and next_page is not None: 
        # at the very beginning 
        curr_page = f"{next_page_type}{next_page-1}{previsRoman}"
    elif next_page is not None and (prev_page + 1) != next_page: 
        # when the extracted sections are not consecutive
        curr_page = f"{next_page_type}{next_page-1}{previsRoman}"
    else: 
        curr_page = f"{prev_page_type}{prev_page}{previsRoman}"
    return curr_page


conjunctions = ['After', 'Aftir', 'Albe', 'Albeit', 'Als', 'Also', 'Althogh', 'Althou', 'Although', 
                'And', 'Ande', 'As', 'Becaus', 'Because', 'Before', 'Beforn', 'Bicause', 'Bifore', 
                'But','Bycause', 'Ergo', 'Euen', 'Even', 'Euē','Except', 'Eyther', 'Finally', 
                'For', 'Forasmuch', 'Forasmuche', 'Howbeit', 'If', 'Nam', 'Ne', 'Nec', 'Neither', 
                'Neuer', 'Neuertheles', 'Neuerthelesse', 'Neyther', 'Nor', 'Or', 'Quapropter', 
                'Quare', 'Quia', 'Quoniam', 'Sed', 'Si', 'Sith', 'Sithe', 'Sithen', 'Sithence', 
                'So', 'Than', 'Thanne', 'That', 'Thatt', 'Then', 'Thenne', 'Then̄e', 'Therefore', 
                'Therfor', 'Therfore', 'Though', 'Thoughe', 'Thus', 'Til', 'Tille', 'Unde', 
                'Unless', 'Until', 'Unto', 'Ut', 'Vnde', 'Vt', 'Whan', 'Whanne', 'Whare', 'Wheither', 
                'When', 'Whenne', 'Wher', 'Wheras', 'Wherby', 'Where', 'Whereas', 'Whereby', 'Wherefore', 
                'Whereof', 'Wherfor', 'Wherfore', 'Wherof', 'Wherout', 'Whether', 'Whē', 'Whil', 'While', 
                'Whiles', 'Whilom', 'Yet', 'Yf',
                'Thyrdely', 'Thyrdly','Thirdly','Firstly','Fyrstely','Frystly','Secondely', 
                'Secondly', "Fourthly",'Forthly',"Fifthly",
                'Ferthermore','Forsothe', 'Forthermore', 'Further', 'Furthermore', 'Furthermore,',
                ]

conjunctions = {w:None for w in conjunctions}
start_words = ['A', 'Ad', 'Againe', 'Agayn', 'Agayne', 'Agaynst', 'Ageyne', 'Ah', 'Al', 'Alas', 'All', 
               'Amonge', 'An', 'Anone', 'Another', 'Are', 'Aske', 'At', 'Be', 'Behold', 'Beholde', 
               'Beleue', 'Besyde', 'Besydes', 'Beware', 'By', 'Come', 'Concerning', 
               'Consider', 'Consyder', 'Did', 'Do', 'Doest', 'Doeth', 'Doo', 'Dyd', 'Ecce', 'Ego', 
               'Est', 'Et', 'Euery', 'Farther', 'First', 'Flee', 
               'From', 'Frome', 'Geue', 'Go', 'Gyue', 'Haec', 'Hanc', 'Haue', 'He', 'Heare', 'Hec', 
               'Hee', 'Here', 'Hic', 'Hit', 'Hoc', 'How', 'Howe', 'I', 'In', 'It', 'Iam', 'Id', 'Ideo', 
               'Ille', 'In', 'Ipse', 'Is', 'Ista', 'It', 'Ita', 'Let', 'Lette', 'Likewise', 'Lo', 
               'Loke', 'Loo', 'Looke', 'Loue', 'Lyke', 'Lykewyse', 'Make', 'Many', 'Manye', 'Marke', 
               'More', 'Moreouer', 'My', 'Namely', 'Narracio.', 'Nay', 'Naye', 'Nether', 'No', 'Non', 
               'None', 'Nonne', 'Noo', 'Not', 'Now', 'Nowe', 'Nunc', 'Nunquid', 'Of', 'On', 'One', 
               'Open', 'Other', 'Ouer', 'Our', 'Oure', 'Out', 'Per', 'Post', 'Praye', 'Put', 'Quae', 
               'Quam', 'Qui', 'Quibus', 'Quicquid', 'Quid', 'Quis', 'Quo', 'Quod', 'Ryght', 'Se', 
               'See', 'Seest', 'Seing', 'Sequitur', 'Seynge', 'Shal', 'Shall', 
               'She', 'Shew', 'Shewe', 'Sic', 'Sicut', 'Sine', 'Some', 'Somtyme', 'Soo', 'Such', 
               'Suche', 'Suerly', 'Sunt', 'Surely', 'Surelye', 'Sustinet', 'Syr', 'THe', 'THere', 
               'Take', 'Tell', 'Thā', 'The', 'Thei', 'Their', 'Ther', 'There', 'These', 'They', 
               'Theyr', 'Thē', 'Thinke', 'This', 'Those', 'Thou', 'Thy',  
               'Thys', 'To', 'True', 'Truely', 'Truly', 'Tu', 'Upon', 'Vbi', 'Verely', 'Verum', 
               'Videtis', 'Vnto', 'Was', 'We', 'Wee', 'Wel', 'Well', 'Were', 'What', 'Whosoever', 
               'Which', 'Whiche', 'Who', 'Whose', 'Whosoeuer', 'Why', 'Whyche', 'Whye', 'With', 
               'Wo', 'Wyll', 'Wyth', 'Ye', 'Yea', 'Yea,', 'Yee', 'Yes', 'You', 'Your', 'Yt']
start_words = {word:None for word in start_words}
