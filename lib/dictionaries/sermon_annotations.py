import pandas as pd

sermons = pd.read_csv("../assets/sermons.csv")
sermons = sermons.to_dict(orient='records')
sermons = {entry['id']: None for entry in sermons}

sermons_missing = pd.read_csv("../assets/sermons_missing.csv")
sermons_missing = sermons_missing.to_dict(orient='records')
sermons_missing = {s['id']:None for s in sermons_missing}

wanted_sections = [
    'text','treatise','part','tract','lecture','lectures','chapter','book',
    'discourse','commentary','doctrine','application','conclusion',
    'exposition','body_of_text','homily','memorial','funeral_sermon',
    'extracts_from_sermon','oration_and_sermon','collection_of_lectures',
    'collection_of_sermons_on_isaiah','collection_of_sermons_on_haggai',
    'whit_sunday_sermons','ordination_sermons','penitential_sermons_preached_at_wells',
    'sermon_extract','application_of_sermon','summary_of_sermons',
    'two_sermons','greek_text_bound_with_sermon','collection_of_sermons','visitation_sermon',
]
wanted_sections = {s:None for s in wanted_sections}
custom = {
        'A81042': 'letter',
        'A64811': 'class',
        'A03634': 'prefatory_letter',
        'A02189': 'address',
        'A09432': 'chapter',
        'A81871': 'section',
        'A14710': 'chapter', # (translation from German into English)
        'A35535': 'commentary_on_job',
        'A63996': 'lamentation',
        'A09434': 'verse',
        'A96523': 'decade',
        'A67068': 'religious_treatise',
        'A03628': 'funeral_oration',
        'A21269':'commentary_on_verse',
        'B03275':'colophon',
        'A60347':'funeral_sermon',
        'A89915':'commentary_on_colossians',
        'A09443':'chapter',
        'A03733':'extracts_from_sermon',
        'A02216':'oration_and_sermon',
        'A68568':'commentary_on_ruth',
        'A47013':'section',
        'A30249':'moral_treatise',
        'A36940':'section',
        'A84091':'essay', # as set forth in a sermon,
        'A34785':'catechism', # catechism adapted from a sermon
        'A17389':'biblical_commentary',
        'A02547':'panegyric',
        'A29933':'poem',
        'A64833':'class',
        'A50402':'chapter',
        'A54843':'homiletic_tract',
        'A62466':'funeral_speech',
        'A41888':'essay',
        'A14653':'chapter',
        'A61391':'chapter',
        'A46629':'speech', # Baptist speech at his trial
        'A87497':'speech', # a dissenting preacher's speech at his trial 
        'A45240':'exposition_of_job',
        'A88582':'scaffold_speech', # Christopher Love's own funeral sermon
        'B22909':'treatises',
        'A10650':'verse',
        'A46825':'funeral_sermon',
        'A43425':'theological_discourse',
        'B09423':'speech',
        'A01979':'exegesis',
        'A35389':'biblical_commentary',
        'A04154':'section',
        'A12524':'commentary_on_acts_8',
        'A33528':'polemic',
        'A01956':'biblical_commentary',
        'B27727':'chapter',
        'A04378':'section',
        'A81950':'preface', # 'chapter' is DIV2 under 'preface'
        'A18606':'book', 
        'A30167':'book', # Bunyan The Light for Those in Darkness
        'A65306':'consolatio',
        'A77994':'collection',
        'A60609':'religious_tract',
        'A12399':'religious_tract',
        'A12389':'religious_tract',
        'A12376':'religious_tract',
        'A68747':'book',
        'A80630':'book',
        'A00392':'book', # Erasmus!
        'A12369':'religious_tract',
        'A08586':'book',
        'A96415':'text', # "Manifested by letters from such as preacht to them there."   
        'A61300':'text',
        'A96951':'tract',
        'A49510': "tract", # "in a sermon preached"
        'A44593':'text', # "Delivered in a sermon"
        'A09055':'text', # 'begunne in a visitation sermon, whereunto are added the substance of divers other sermons and treatises'
        'A07647':'treatise', # "First deliuered in a sermon"
        'A28659':'treatise', # "delivered in severall sermons"
        'A19282':'treatise', # "Expressed in diuers profitable sermons"
        'A49701':'text', # collection of Hugh Latimer's sermons; subject heading 'Preaching'
        'A81043':'text', # "Being the summe and substance of certain sermons preached"
        'A16317':'text', # "deliuered in certaine sermons" 
        'A70858':'text', # "explained, confirmed, and applyed (very briefly) in one sermon"
        'A53271':['doctrine','application'], # "delivered in several sermons"
        'B18418':'discourse', # "repeated and improved in two sermons on Mat. 26. 26"
        'A16506':'text', # "Deliuered first in briefe, in a sermon preached at Paules-Crosse"
        'A07190':'text', # 'Deliuered in a sermon preached'
        'A32891':'tract', # "delivered in several sermons, and now published for publick benefit"
        'A04112':'tract', # "First deliuered in seuerall sermons"
        'B12497':'tract', # "deliuered in a sermon preached"
        'A26830':'text', # "asserted in a sermon preached"
        'A20528':'treatise', # 'preached in divers sermons, the substance whereof, is now published'
        'A61010':'text', # "delivered in a sermon at Truro in Cornwall at his primary visitation"
        'A05347':'treatise', # "The summe wherof was delivered in a sermon preached at Belfast, at the visitation of the diocese of Downe and Conner"
        'A09970':'treatise', # "The former delivered in sundry sermons in Cambridge, for the weekely fasts, 1625"
        'A21258':'text', # "deliuered in diuers sermons"
        'A58940':'text', # "in a sermon, preparatory to the Lord's-Supper"
        'A10929':'exposition', # "Deliuered in sundry sermons"; exclude the 'analysis' section 
        'A88806':'text', # "delivered in two sermons...in a third sermon at the same church"
        'A78088':'tract', # "delivered by him in a late sermon"
        'A81217':'text', # 'delivered in a funeral sermon'
        'A06732':'text', # "Delivered in sundry sermons"
        'A49757':'text', # "Preached in several sermons"
        'A01883':'part', # "First preached in a sermon"
        'A08482':'text', # 'in a sermon preached at the funerall'; ignore the 'elegy' and 'epitaph' sections by another D.D.
        'A04483':['text','treatise'], # "Both which he deliuered in diuers sermons"
        'A51907':'commentary', # "delivered in sundry sermons preacht in the church of St. James Garlick-hith London"
        'A73751':'tract', # "deliuered in certaine sermons"
        'A50410':'text', # "Certain sermons and letters"; ignore the two 'part' sections 
        'A15010':'tract', # "First preached in the parish church of Banbury in certaine sermons"
        'A13083':'text', # 'begunne in sermons, and now digested into a treatise'
        'A77775':'text', # "Preached in Concord in Nevv-England"
        'A96416':'text', # 'preached there, and elsewhere'
        'A48424':'tract', # 'Preached by"
        'A54347':'discourse', # 'first preached, and now published" 
        'A37030':'text', # "Preached at Reading" 
        'A03342':'part', # "CVIII lectures vpon the fourth of Iohn Preached at Ashby-Delazouch"
        'A06160':'part', # "First preached, and now published" 
        'A06161':'part', # "First preached, and now published"
        'B43800':'text', #  "First preached and afterwards printed"
        'A19614':'exposition', # 'First preached in his Parish Church'
        'A16166':'text', # "First preached, then penned"
        'A13209':'text', # "Preached by"
        'A66772':'part', # "warrantably proclaimed and preached by Geo. Wither"; subject heading "History"
        'A09465':'treatise', # "Framed and preached by M. Wil. Perkins."
        'A50026':'text', # "Since occasionally preached in part...and now presented to publick view,"
        'A29121':'text', # "By Thomas Bradley doctor of divinity, chaplaine to His late Majesty King Charles the First, and præbend of York. And there preached at Lent assizes holden there"
        'A62878':'treatise', # 'preached at Lemster'
        'A38609':['part','commandment'], # New observations upon the decalogue: or The second of the four parts of Christian doctrine, preached upon the catechism. 
        'A44674':'text', # "Preached to a country congregation, by J.H. And publish'd by one who wrote it from his mouth."
        'A10557':'text', # BOOK OF COMMON PRAYER! Edmund Reeve
        'A38608':'text', # "New observations upon the Creed, or, The first of the four parts of the doctrine of Christianity preached upon the catechism of the French churches"
        'A04626':'text', # "A treatise of patience in tribulation first, preached before..."; ignore the "part" and "epicedium" 
        'A09463':'text', # "A commentarie vpon the temptations of Christ: preached in Cambridge by that reuerend and iudicious diuine M. William Perkins"
        'A25215':'text', # "partly preached at Guild-hall Chappel"
        'A76324':'text', # A man's last words; "With a sermon made upon this text, preached at his funeral by a reverend divine, Mr. Thomas Palmer."
        'A81043':'text', # Being the summe and substance of certain sermons preached by Mr. Daniel Carwardine
        'A16317':'text', # deliuered in certaine sermons in Oxford, and at Pauls Crosse
        'A70858':'text', # applyed (very briefly) in one sermon to the satisfaction of some judicious hearers, for whose sake chiefly and at whose earnest request, it is made publick.
        'A53271':['doctrine','application'],
        'B18418':'discourse', # repeated and improved in two sermons on Mat. 26. 26
        'A16506':'text', # Deliuered first in briefe, in a sermon preached at Paules-Crosse
        'A07190':'text', # Deliuered in a sermon preached in the Greene yard at Norwich the third Sunday after Trinitie
        'A32891':'tract', # delivered in several sermons, and now published for publick benefit. 
        'A04112':'tract', # First deliuered in seuerall sermons, and now published to the glory of God, and for the further benefit of his church.
        'B12497':'tract', # The chiefe points whereof were deliuered in a sermon preached at Pauls Crosse
        'A26830':'text', # a sermon preached at St. Brides-Church
        'A20528':'treatise', # first preached in divers sermons, the substance whereof, is now published for the benefit of the church
        'A61010':'text', # delivered in a sermon at Truro in Cornwall at his primary visitation.
        'A05347':'treatise', # The summe wherof was delivered in a sermon preached at Belfast
        'A09970':'treatise', # delivered in sundry sermons
        'A13083':'text', # begunne in sermons, and now digested into a treatise.
        'A15010':'tract', # First preached in the parish church of Banbury in certaine sermons, and now published in this present treatise.
        'A73751':'tract', # deliuered in certaine sermons
        'A51907':'commentary', # delivered in sundry sermons preacht in the church of St. James Garlick-hith London
        'A04483':['text','treatise'], # Garband the editor; Jewel the preacher; Both which he deliuered in diuers sermons in his cathedral church of Salisburie, anno. 1570
        'A08482':'text', # Evidently declared in a sermon preached at the funerall
        'A01883':'part', # First preached in a sermon, since enlarged, reduced to the forme of a treatise,
        'A49757':'text', # Preached in several sermons
        'A06732':'text', # Delivered in sundry sermons
        'A81217':'text', # As it was delivered in a funeral sermon preached
        'A10929':'exposition', # Deliuered in sundry sermons
        'A21258':'text', # deliuered in diuers sermons
        'A58940':'text', # practically answered, in a sermon,
        'A96524':'treatise', # Being the substance of some sermons long since preached
        'B11278':'text', # The summe of certaine sermons 
        'A74688':'text', # Being the substance of several sermons delivered
        'A63500':'text', # A true copy of the Welch sermon; (sermon is in English)
        'A58782':'text', # An abstract (with remarks) of Dr. Scot's sermon
        'B20731':'treatise', # being the substance of sundry sermons
        'A09031':'text', # being the substance of neere foure yeeres weekedayes sermons
        'A54857':'part', # being the substance of several sermons, deliver'd at several times and places
        'A45680':'text', # being the substance of several sermons, on Isaiah XLV. 24, 25 
        'A04261':'text', # A sermon preached at Modbury in Devon
        'A65610':'text', # A sermon containing very good remedies
        'A12565':'text', # A sermon preached at White-Hall before the Kings most excellent Majestie
        'A65470':'text', # A sermon preached at the anniversary meeting of the Sons of Clergy-men
        'A12384':'text', # Certain notes of M. Henry Aynsworth his last sermon. Taken by pen in the publique delivery by one of his flock
        'A12350':'text', # A fruitfull sermon vpon part of the 5. chapter of the first epistle of Saint Paule to the Thessalonians
        'A19589':'part', # The sermon preached at the Crosse, Feb. xiiii. 1607. 
        'A66990':'text', # The substance of a sermon, being an incouragement for Protestants or a happy prospect of glorious success: with exhortations to be valiant against our enemies, in opposing the bloody principle of papists, and errors of popery, &c.
        'A76798':'treatise', # Expositions and sermons upon the ten first chapters of the Gospel of Jesus Christ, according to Matthew. 
        'A04870':'text', # A sermon preached at Canterbury in the Cathedral Church of Christ. 
        'A11602':'text', # A sermon preached at the last generall asise holden for the county of Sommerset at Taunton
        'A14381':'text', # Being the summe of divers sermons
        'A80869':'treatise', # Being the substance of several sermons preached in the town of Columpton in Devon. 
        'A41974':'part', # Being the substance of several sermons preached in a country congregation. 
        'A39910':'text', # Preached (for the substance of it) 
        'A04390':'text', # Irelands triumphals, with the congratulations of the English plantations, for the preseruation of their mother England, solemnized by publike sermons. 
        'A13216':'discourse', # 'twas first intended for the pulpit, and should have beene concluded in one or two sermons, but is extended since to a larger tract
        'B29152':'text', # Delivered in a wedding-sermon
        'A28344':'text', # whereunto is annexed a sermon preached at his funeral
        'A45330':'text', # an additional sermon on verse 6, by George Swinnock
        'A80739':'part', # delivered in several exercises before sermons, upon twenty and three texts of Scripture.
        'A41519':['part','doctrine'], # to which is added, a sermon
        'A26926':'text', # broadside of quotations/maxims; "Excellent memorables...gathered out of Mr. B's prepared (though not preached) farewel sermon"
        'A26953':'text', # Memorables of the life of faith taken out of Mr. B's sermon preached before the King at Whitehall
        'A76316':'treatise', # collected out of some lectures lately preached 
        'A30364':'text', # the substance of several sermons preached on that subject
        'A42057':'text', # Being the substance of several sermons preach'd by the author upon his recovery from a fit of sickenss
        'A76131':'text', # Being the summe of some sermons preached at Upton upon Seavern, in the county of Worcester. 
        'A28514':'text', # The svmme of a sermon upon Revelation 18 and the 6 preached at Knowle
        'A33723':'discourse', # preached at the Merchants-Lecture in Broad-Street by Thomas Cole
        'A43763':'text', # being the substance of several sermons preached by a person 
        'A33720':'part', # in sundry points preached at the merchants lecture in Broadstreet / by Thomas Cole 
        'A64178':'text', # a tub lecture, preached at Watford in Hartfordshire at a conventicle 
        'A00415':'part', # As they were preached, and afterwards more briefly penned by that vvorthy man of God
        'A76218':'text', # Preached, and now published for the use of those that are strangers to a true conversion
        'A30248':'text', # XXX lectures preached at Lawrence-Iury, London / by Anthony Burgess 
        'A19037':'text', # Preached, and now published, by Edmund Cobbes minister of the Word of God.
        'A66437':'text', # Preacht at Springfield lecture, August 25th. 1698. 
        'A19036':'text', # Preached and now published by Edmund Cobbes, master of the Word of God.
        'A95609':'treatise', # Being the summe of LXIV lecture sermons preached at Sudbury in Suffolk, on Cantic. 8.5. 
        'A77854':'text', # In XXIX. lectures, preached at Laurence-Jury, London. 
        'A09376':'commentary', # preached in Cambridge by that godly, and iudicious divine, M. William Perkins...published at the request of his executours...who heard him preach it, and wrote it from his mouth.
        'A13538':'text', # Preached and now published by T.T. late fellow of Christs Colledge in Cambridge.
        'A08552':'treatise', # Preached in the lecture of Kettering in the county of Northampton, and with some enlargement published by Ioseph Bentham, rector of the Church of Broughton in the same county. 
        'A11011':'lecture', # Preached by that faithfull seruant of God, Maister Robert Rollok, sometime rector of the Vniuersitie of Edenburgh
        'A11010':'part', #  preached by that faithfull seruant of God M. Robert Rollock, some-tyme minister of the Euangell of Iesus Christ, and rector of the Colledge in Edinburgh 
        'A11012':'lecture', # Preached by that reuerend and faithfull seruant of God, Mr. Robert Rollocke, sometime minister of the Euangell of Iesus Christ, and rector of the Colledge of Edinburgh. 
        'A11006':'lecture', #  Preached by the reuerend and faythfull seruant of God, M. Robert Rollok, minister of the Kirke (and rector of the Colledge) of Edinburgh. 
        'A50162':'discourse', # preached partly at Boston, partly at Charleston / by Cotton Mather
        'A13535':'part', # Preached in Cambridge by Thomas Taylor
        'A68733':'part', # Being the substance of divers sermons preached at Grayes Inne. By that reverend divine, Richard Sibbes, D.D. and sometimes preacher to that honourable society. -----------  Early works to 1800. -- Holy Spirit
        'A80317':'text', # <PB N="5" REF="3" MS="y"/> ;  Contains the substance of the sermon preached to them
        'A89104':'letter', # "A message from the Isle of Wight, brought by Major Cromwell...Also the chiefe heads of Bishop Ushers sermon"
        'B12473':'subpoena', # "A sub-poena from the star-chamber of heauen A sermon preached at Pauls Crosse"
        'A73832':'dialogue', #, "Taken, for the most part, out of the ten sermons of Mr I. Dod, and Mr. R. Cleaver"
        'A56791':'abstract', # "Jesus is God, or, The deity of Jesus Christ vindicated being an abstract of some sermons preach'd in the parish-church of St. James, Clerkenwell / by D. Pead."
        'A03696':'commentary_on_luke', # "Of the rich man and Lazarus Certaine sermons, by Robert Horne."
        'A60568':'life', # "The life and death of Mr. William Moore, late fellow of Caius Colledge, and keeper of the University-Library as it was delivered in a sermon preached at his funeral-solemnity"
        'A14927':'dialogue', # "The cure of a hard-heart First preached in diuers sermons, by Master Welsthed, resident at Bloxford in Dorcetshire. Since digested into questions and answers for the hungrie."
        'A81606':'letter', # Children's sermons; "A salutation and seasonable exhortation to children."
        'A26065':'document', # "Evangelium armatum, A specimen, or short collection of several doctrines and positions destructive to our government, both civil and ecclesiastical preached and vented by the known leaders and abetters of the pretended reformation such as Mr. Calamy, Mr. Jenkins, Mr. Case, Mr. Baxter, Mr. Caryll, Mr. Marshall, and others, &c."
        'A90476':'newsbook', # "with the chief heads of his Lordships funerall-sermon, preached by Mr. Bowles."
}

custom_exceptions = {
        'A95937':{'vindication':[2]}, # <DIV1 TYPE="vindication"><PB N="21" REF="13"/> # the 3rd vindication
        'A50410':{'text':[0,1,2]}, # only the first THREE; IGNORE THE FOURTH (a letter)
        'A09462':{'part':[0]}, # only the FIRST part out of three 
        'A36312':{'text':[0]}, # only the FIRST of two; the second part contains the preacher's death-bed reflections 
        'A96995':{'text':[0]}, # only the FIRST of two; the second contains responses to counter-arguments 
        'A64635':{'part':[2]}, # the THIRD part is a sermon of Bishop Bedels
        'A38185':{'text':[0]}, # only the FIRST out of three; A recantation-sermon
        'A64135':{'text':[3]}, # only the FOURTH out of four; a sermon preached at Oxon. on the anniversary of the 5 of November 
        'A92163':{'speech':[1]}, # the SECOND speech; <DIV1 TYPE="speech">; "The ranters recantation; and their sermon"
        'A10242':{'text':[1]}, # the SECOND text of two; "together with a short meditation vpon 2. Sam. 24.15., preached at a weekely lecture in Deuon"
        'A77497':{'treatise':[1,2,3,4]}, # the SECOND to FIFTH treatises; with a sermon on Mark 10-16 "As it was some time since preached in the church of Great Yarmouth"; the first treatise may not have been preached
        'A69511':{'part':[1]}, # <P><PB N="13" REF="8"/> ; the SECOND part -- exclude the contents within the <LETTER></LETTER> and <LIST></LIST>. Begin with the following: <P><PB N="13" REF="8"/>
}


custom_pages = {
        'A80317':'PAGE5', # <PB N="5" REF="3" MS="y"/> ;  Contains the substance of the sermon preached to them
        'A69511':'PAGE13', # <P><PB N="13" REF="8"/> ; the SECOND part -- exclude the contents within the <LETTER></LETTER> and <LIST></LIST>. Begin with the following: <P><PB N="13" REF="8"/>
        'A90476':'PAGE2'
}

custom_subsections = {
        'A28857': {'DIV2':('section','5')},
        'A13078': {'DIV1':('book','1')}, # <DIV1 N="1" TYPE="book">; the second one is a discourse expanding on his sermon
        'A26951': {'DIV1':('part','1')}, # <DIV1 N="1" TYPE="part">; the first is a sermon on Heb. 11, 1, formerly preached before His Majesty, and published by his command, with another added for the fuller application
}

sermon_subsections = ['A00593', 'A01628', 'A02178', 'A02609', 'A02883', 'A03272', 'A03281', 'A03617', 'A04608', 
                      'A05185', 'A06325', 'A07572', 'A07836', 'A08444', 'A08445', 'A09950', 'A09965', 'A09990', 
                      'A09999', 'A10046', 'A10134', 'A10931', 'A12367', 'A12807', 'A13010', 'A13014', 'A13570', 
                      'A13755', 'A13835', 'A14350', 'A14709', 'A14711', 'A14753', 'A15343', 'A16525', 'A16526', 
                      'A16535', 'A16562', 'A17215', 'A17328', 'A17722', 'A18016', 'A18073', 'A20782', 'A21252', 
                      'A25383', 'A25395', 'A27619', 'A28171', 'A28173', 'A29372', 'A30238', 'A30579', 'A30609', 
                      'A31073', 'A33421', 'A34880', 'A34992', 'A35314', 'A35318', 'A35326', 'A35753', 'A36855', 
                      'A36905', 'A37028', 'A38823', 'A39268', 'A39399', 'A41017', 'A41106', 'A41125', 'A41135', 
                      'A44070', 'A47098', 'A47437', 'A47542', 'A47576', 'A48917', 'A49252', 'A49258', 'A49589', 
                      'A50114', 'A50403', 'A50529', 'A50799', 'A51837', 'A51838', 'A52035', 'A53504', 'A57735', 
                      'A59549', 'A60254', 'A61193', 'A61409', 'A62128', 'A62326', 'A63050', 'A65588', 'A65835', 
                      'A66106', 'A69130', 'A69147', 'A69777', 'A75925', 'A77355', 'A77486', 'A77853', 'A77996', 
                      'A78903', 'A80160', 'A80872', 'A84690', 'A85036', 'A85088', 'A85953', 'A86138', 'A88594', 
                      'A89597', 'A91808', 'A91897', 'A94353', 'A95762', 'A96093', 'A96871', 'B01658', 'B01867', 
                      'B02482', 'B03494', 'B03501', 'B05977', 'B08803', 'B14421', 'B18355', 'B18399', 'A67927', 
                      'A42583', 'A93063', 'A19986', 'A96278', 'A59582', 'A10394', 'A33980', 'A51443', 'A14032', 
                      'A77357', 'A77632', 'A76329', 'A50253', 'A16087', 'A30243', 'A77998', 'A18973', 'A12590', 
                      'A16333', 'A43632', 'A47044', 'A84421', 'A88281']
sermon_subsections = {s:None for s in sermon_subsections}


# {
#         'A67927': ['DIV2','DIV3'],
#         'A42583': ['DIV2'],
#         'A93063': ['DIV2'],
#         'A19986': ['DIV3'],
#         'A96278': ['DIV2'],
#         'A59582': ['DIV2','DIV3'],
#         'A10394': ['DIV2'],
#         'A33980': ['DIV2'],
#         'A51443': ['DIV3'],
#         'A51443': ['DIV2'],
#         'A14032': ['DIV2'],
#         'A77357': ['DIV3'],
#         'A77632': ['DIV2'],
#         'A76329': ['DIV2'],
#         'A50253': ['DIV2'], # there are 30 typological_category sections, which each contain a DIV2 sermon section 
#         'A16087': ['DIV2'],
#         'A30243': ['DIV3'],
#         'A77998': ['DIV2'], 
#         'A18973': ['DIV2']
# }