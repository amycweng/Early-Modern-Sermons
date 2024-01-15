from bible import bible_dict, numBook 
import re,csv 

class Margins():
    def __init__(self,infile):
        with open(infile, 'r') as file:  
            self.notes = csv.reader(file, delimiter=',')

    def clean(self):
        for idx, entry in enumerate(self.notes):
            if idx == 80: break
            # get note text 
            n = entry[-1]
            # replace all periods with spaces and convert to lower case 
            n = re.sub(r'(\.)',r' ',n).lower()
            # replace all instances of two or more spaces with a single space. 
            n = re.sub(r'\s+',' ',n)
            # normalize conjunctions 
            n = re.sub(rf"\band\b|&ampc|&amp",'&', n)
            # normalize abbreviations  
            n = self.replaceBook(n)
            # find instances of possible numbered books 
            possible = re.findall(r'(\b[1|2|3]\b [a-z]+ [^a-z|^\b&\b|^〈]+)',n)
            for i, p in enumerate(possible):
                possible[i] = self.replaceNumBook(p)
            possible.extend(re.findall(rf'([a-z]+ [^a-z|^\b&\b]+)', n))
            if len(possible) > 0: 
                print(idx,possible)
        
        
    def replaceBook(self,note): 
        note = note.split(" ")
        for idx, word in enumerate(note): 
            word = re.sub("u|v","u",word)
            word = re.sub(r"^i","j",word)
            if word in self.bible_dict:
                note[idx] = self.bible_dict[word]
        return " ".join(note) 

    '''
    Converts numbered books into a single string, e.g., '1 corinthians' to '1corinthians' 
    '''
    def replaceNumBook(self,text):
        book = " ".join(text.split(" ")[0:2])
        if book in numBook:  
            text = re.sub(rf'{book}', numBook[book], text)
        return text