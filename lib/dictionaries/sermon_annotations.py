import pandas as pd

sermons = pd.read_csv("../assets/sermons.csv")
sermons = sermons.to_dict(orient='records')
sermons = {entry['id']: None for entry in sermons}

sermons_missing = pd.read_csv("../assets/sermons_missing.csv")
sermons_missing = sermons_missing.to_dict(orient='records')
sermons_missing = {s['id']:None for s in sermons_missing}

# foreign texts
exclude_foreign = {'A95346': 'wel', 'B34542': 'fre', 'B10302': 'wel', 'B02801': 'fre', 
                   'B07519': 'wel', 'A87349': 'wel', 'A81783': 'fre', 'A81315': 'wel', 
                   'A91720': 'sco', 'A95629': 'fre', 'A91479': 'fre', 'A91847': 'fre', 
                   'A62564': 'fre', 'A52002': 'fre', 'A29335': 'fre', 'A29334': 'fre', 
                   'A31429': 'new', 'A64645': 'wel', 'A76482': 'wel', 'A72359': 'wel', 
                   'A00687': 'sco', 'A17050': 'sco', 'A95720': 'wel', 'B04329': 'wel', 
                   'B09870': 'fre', 'A60308': 'fre', 'A50422': 'wel', 'A59547': 'fre', 
                   'A29332': 'fre', 'A00164': 'lat', 'A00156': 'lat', 'A45574': 'lat', 
                   'A65588': 'lat', 'A07584': 'lat', 'A02379': 'lat', 'A06325': 'lat', 
                   'A19485': 'lat', 'A80884': 'lat', 'A09748': 'lat', 'A67819': 'lat', 
                   'A44316': 'lat', 'A19744': 'lat'}

exclude_annotated = [
    'A96361', # commentary on the Sermon on the Mount 
    'A16204', # only a title page & colophon of a 16th cent. sermon
    'A53661', # remarks on a sermon 
    'A42786', # remarks on remarks on a sermon
    'A43674', # discourses upon a funeral sermon
    'A17423', # musical compositions (even tho title mentions a sermon)
    'B03994', # letter w/ an account of some preacher w/ hymns that they sing
    'A76964', # catechism; does not contain the sermon promised in the title
    'A68730', # does not actually contain the sermon promised in the title 
    'B03688', # narrative account
    'A31468', # censure
    'A15864', # guide to hearing sermons first written in Latin
    'A34897', # reply to sermon
    'B17774', # Psalms 
    'A13551', # chapter 
    'A52900', # response to sermon
    'A52284', # letters & hymns sung at a funeral sermon
    'A50287', # petition, embassage
    'A96439', # Quaker letters & remarks 
    'A39120', # reply to sermon
    'A53461', # broadside mock sermon
    'A22477', # royal proclamation
    'A33382', # book catalogue 
    'A62876', # dissenting polemic
    'A86098', # speech against a sermon
    'A83515', # Tho. Edwards' Gangraena 
    'A53708', # meditations & discourses 
    'A34396', # mock sermon
    'A40761', # Quaker testimony 
    'A03927', # reasons & answers about the book of common prayer 
    'A10581', # dialogue
    'A49230', # reply to a treatise 
    'A35266', # catalogue of writers 
    'A32938', # articles of enquiry in Diocese of Carlisle; visitation sermon
    'A86442', # Quaker reply to sermon
    'A01012', # response to an accident that occurred at a Catholic sermon 
    'A35017', # criticism of Scotch sermons
    'A83979', # monsters & accounts of portentous events; brief relation of her funeral sermon
    'A82859', # parliamentary_declaration
    'A14186', # Psalms
    'A07105', # treatise about the schism
    'A26870', # actual funeral sermon is missing from the microfilm 
    'A09426', # William Perkins' The foundation of Christian religion; 'religious_tract', not labeled as a sermon & no place of preaching 
    'A20733', # Downame's defense of his sermon
    'A10341', # reply to Downame's defense 
    'A68172', # critique of a 'wicked sermon',
    'A44239', # discourse referring back to an earlier printed sermon
    'A52641', # primarily narrative of death & burial; funeral sermon hard to extract and identify 
    'A74862', # letter exposing how a writer contradicted with his past sermons 
    'A97284', # primarily a narrative & history about the Dutch fleet for the Commonwealth 
    'A84987', # mineral waters in Germany 
    'A61076', # response to 'a late scurrilous libel, prefix'd to a sermon preach'd nine and thirty years ago'
    'A25580', # "An ansvver to" sermons
    'A67000', # "Against the doctrine of" a preacher in his sermons 
    'A41398', # Letter "modestly accepting the challenge by him made in his sermon of repentance preached"
    'A37425', # narrative account w/ "divers familiar letters, both Latin and English sermons, poems, essays"; pilgrimage
    'B29264', # dissertation upon water-baptism 
    'A60334', # response to a sermon  
    'A36211', # response to a sermon  
    'A53674', # response to a sermon  
    'A16999', # response to a sermon 
    'A71053', # response to a sermon 
    'A27407', # response to a sermon 
    'A32910', # response to a sermon; "The female advocate...Being reflections on a late rude and disingenuous discourse, delivered by Mr. John Sprint, in a sermon at a wedding"
    'A80756', # the promised "annexed sermon" is not found in the text; conversation between a minister and a converted recusant  
    'A68566', # response to a sermon; "A briefe discouery of the vntruthes and slanders...contained in a sermon"
    'A26579', # response to a sermon 
    'A76800', # contains a response to a sermon 
    'A79931', # response to a sermon; biblical commentary responding to certain writers 
    'A68078', # includes a response to a sermon
    'A04207', # responses to divines 
    'A56659', # response to a sermon
    'A53040', # response to a slanderous sermon 
    'A42574', # answer to a text 
    'A01006', # response to W. Crashawe's sermon 
    'A19895', # response to a sermon 
    'A60334', # defense of Catholicism against several books 
    'A36211', # remarks on a sermon
    'A53674', # defense of non-conformists against a sermon 
    'A76800', # huge volume containing a reply to a sermon 
    'A79931', # defense of some preacher's proof-text 
    'A26579', # includes a reply to a sermon 
    'A68566', # response to a sermon
    'A80756', # response to a sermon 
    'A32910', # a lady of quality's response to rude remarks in a sermon
    'A27407', # reply to a sermon 
    'A71053', # response to a sermon 
    'A78088', # response to a sermon 
    'A88806', # preacher's protests againsts responses to his sermons 
    'A16999', # response to a sermon
    'A04214', # response to another preacher's writings 
    'A27593', # responses to two preachers' sermons 
    'A91807', # response to a sermon 
    'A38139', # remarks on a response to a sermon 
    'A54794', # commentary on preaching  
    'A36116', # response to a sermon 
    'A54793', # response to several sermons 
    'A77374', # response to a preacher's book; does not contain the three sermons which the title mentions 
    'A69662', # remarks on Laud's final sermon
    'A81905', # commentary on "ministers medling with state matters in or out of their sermons"
    'A66436', # vindication of two preachers' sermons 
    'A61415', # contains a letter that comments on sermons 
    'A45400', # letters & excerpts from letters; does not contain the two added sermons 
    'A41330', # contains observations upon a sermon 
    'A44665', # response to a letter that remarked upon a sermon 
    'A64572', # household manual of piety (contains a section on the "repeating of sermons")
    'A28590', # response to a sermon 
    'A51087', # respnose to a sermon 
    'A25563', # response to a sermon by the "gentleman who took the said sermon in short-hand"
    'A51787', # contains reflections upon a sermon
    'A10320', # response to a sermon 
    'A09101', # contains a reproof of a sermon 
    'A49336', # contains a letter & reflections upon letters regarding sermons 
    'A47737', # reflections upon a preacher's sermons 
    'A49256', # Christopher Love's replies to William Dell's sermons 
    'A94741', # contains remarks on a sermon 
    'A36257', # a vindication of a sermon regarding organ music in churches 
    'A58375', # reflections on a sermon by a "gentleman who took the said sermon in short-hand"
    'A00514', # contains a commentary on St. Bernard's sermon 
    'A34868', # history of Biblical events 
    'A49667', # a testament "taken in short-hand by a zealous scribe who used to take sermon notes"
    'A27592', # discourse upon a preacher's sermon 
    'A30987', # a treatise of fornication; does not contain the added "penitentiary sermon upon John viii. II" 
    'A06202', # "Sundry Christian passions contained in two hundred sonnets."
    'A47758', # "Remarks on some late sermons, and in particular on Dr. Sherlock's sermon"
    'A44658', # contains remarks on a sermon; mostly a vindication 
    'A92420', # contains remarks on a sermon 
    'A31766', # remarks on a sermon 
    'A60515', # "In opposition to a counterfeit sermon pretended to be preached before the people called Quakers"
    'A76517', # remarks on two sermons 
    'A33070', # remarks on a sermon 
    'A57569', # remarks upon a sermon 
    'A41625', # reply to an answer 
    'A65714', # "A reply to what S.C. (or Serenus Cressy) a Roman Catholick hath returned to Dr. Pierces sermon"
    'A21332', # translation of a French text by Portugal's prince 
    'A31518', # queries upon a sermon 
    'A30410', # reflections on a pamphlet that responds to a sermon 
    'A84572', # a request to a preacher in response to his sermon  
    'A97256', # a text on the preaching and hearing of sermons 
    'A77003', # response to a sermon falsely published on the author's name 
    'A93805', # commentary on Laud's last sermon 
    'A55506', # "The Pourtraicture of K. Charles I illuminated with several of his memorable actions, very proper to be read on the 30th of January, before sermon"
    'A59248', # animadversions on a sermon
    'A69663', # commentary on Laud's last sermon 
    'A64152', # commentary on separatists who made a scene at a sermon 
    'A59589', # response to another minister's writings 
    'A62867', # remarks on a sermon 
    'A47892', # "No blinde guides, in answer to a seditious pamphlet of J. Milton's"
    'A85385', # "Delivered by way of prologue before a sermon the last publique fast-day"
    'A93736', # treatise on the judgment of God that differs from "any other books or sermons upon this subject."
    'A64355', # "A defence of Dr. Tenison's sermon of discretion in giving alms"
    'A56654', # "A discourse of profiting by sermons"
    'A10173', # "Protestants demonstrations, for Catholiks recusance All taken from such English Protestant bishops, doctors, ministers, parlaments, lawes, decrees, and proceedings"
    'A44682', # "A letter written out of the countrey to a person of quality in the city who took offence at the late sermon of Dr. Stillingfleet"
    'A43648', # remarks on a farewell sermon 
    'A15195', # the whole book of Psalms 
    'B09664', # broadside for the University of Oxford advertising a sermon for coronation 
    'A64159', # remarks on separatists gathering to hear a sermon 
    'A32109', # "His Maiesties speciall command under the great seale of England to the Lord Major of the honourable city of London"
    'A38590', # "Catechistical discovrses"
    'A89171', # "Occasioned by a seditious sermon lately preached."
    'A28185', # "Some animadversions upon his sermon"
    'A11933', # commentaries on Ecclesiastes 
    'A53902', # Maxims, aphorisms and apothegms for prayers before or after his sermons 
    'A65863', # contains remarks on a sermon preached by Edward Stillingfleet before the king 
    'A34032', # "some considerations upon the sermons of a divine" 
    'A90551', # remarks "upon the publishing a pretended sermon"
    'A47223', # a letter in response to a sermon  
    'A08483', # an exposition adapted from "the catechising sermons of Gasper Oleuvian Treuir, and now translated out of the Latine tongue into the English"
    'A69915', # contains a letter that responds to a sermon 
    'A81846', # propositions addressed to Oliver Cromwell 
    'A10686', # an elegy on the death of a hundred persons "who were lamentably slaine by the fall of a house in the Blacke-Fryers being all assembled there (after the manner of their deuotions) to heare a sermon on Sunday night"
    'A35016', # responses to sermons 
    'A68106', # "A declaration of Henry Marc de Gouffier Marquise of Boniuet, Lord of Creuecœur, &c. Made in the consistorie of Rochell, in the presence of the pastors and elders of the said towne"
    'B22921', # "with an appendix in vindication of a sermon"
    'A10724', # "The true report of a late practise enterprised by a papist with a yong maiden in Wales"
    'B04689', # catechism 
    'A81375', # Message from the Isle of Wight, brought by Major Cromwell.
    'A52918', # treatise on dissenters; "Vox clamantis, or, A cry to Protestant dissenters calling them from some unwarrantable ways, with which they are vulgarly, and perhaps too truly charged"
    'A18948', # "The recantation of Thomas Clarke (sometime a Seminarie Priest of the English Colledge in Rhemes; and nowe by the great mercy of God conuerted vnto the profession of the gospell of Iesus Christ) made at Paules Crosse, after the sermon made by Master Buckeridge preacher"
    'A90877', # "The Portraiture of Mr. George Keith the Quaker, in opposition to Mr. George Keith the parson."
    'A87716', # letter 
    'A10442', # "A confutation of a sermon"
    'A10443', # "Confutation of a sermon, pronounced by M. Juell, at Paules crosse"
    'A44801', # an answer to a sermon
    'A90899', # three dialogues; does not contain the two added sermons mentioned in the title 
    'A27029', # breviate about controversies regarding justification, antinomianism, the reprinting of a preacher's sermons 
    'A34230', # does not contain the "brief notes of two sermons", only a narrative 
    'A93510', # "Some plain directions for the more profitable hearing of the vvord preached"
    'A52614', # only contains a life; does not contain the "sermon on Luke X. 36, 37 preach'd on the occasion of his death"
    'A85774', # an exposition; does not contain the "two sermons preached before the University at Oxford, some years since"
    'A56520', # narrative about infanticide; does not contain the appendixed sermon 
    'A76180', # list of advice to Parliament from Richard Baxter at the end of his sermon 
    'A17683', # translation out of Latin of Calvin's lectures  
    'A27494', # does not contain the added "sermon of regal power" 
    'A86886', # "The foure wishes of Mr. John Humphrey, in conclusion of his sermons printed 1653."
    'A67822', # several poems, including a poetical translation of a Latin sermon by Edward Young
    'A81581', # "Queries upon queries: or Enquiries into Certain queries upon Dr. Pierce's sermon at Whitehall, Feb. 1"
    'A71091', # Refutation of a sermon preached by Stephen Marshall before the House of Commons (Meroz Cursed)
    'A28579', # contains a list of "Choyce Occasional Sermons"
    'A50799', # contains a list of recommended sermons 
    'A13812', # answer to remarks on a sermon 
    'A21069', # treatise proving "it to be absolutely sinfull to heare the word preached in any false state"
    'A43399', # "A reply in the defence of Oxford Petition"
    'A44308', # reply to a sermon 
    'A44843', # "The record of sufferings for tythes in England"
    'A46371', # reflections of a learned man on the "strange and miraculous exstasies" of a woman 
    'A48172',  # a letter reply to a sermon 
    'A58328', # response to a sermon 
    'B01388', # "An answer to Clemens Alexandrinus's sermon"
    'A89416', # "A true relation of the proceedings from York and Beverley."
    'B03839', # "The Jacobite's new creed, containing the articles of their faith, and doctrine of salvation, as now preach'd and practised, &c. Licensed according to order."
    'B06138', # "To the Reverend Dr. Beveridge, an eucharisticon, occasion'd by his seasonable and excellent sermon"
    'B09463', # "In a letter, which impartially discovers the manifold haeresies and blasphemies, and the strong delusions of even the most refined Quakerism"
    'A81906', # "A case of conscience resolved: concerning ministers medling with state matters in their sermons"
    'A88596', # "The true and perfect speec [sic] of Mr. Christopher Love on the scaffold on Tower-Hill"
    'A81417', # "A dialogue; between George Keith, and an eminent Quaker relating to his coming over to the Church of England. With some modest reflections on Mr. Keith's two first sermons" 
    'A85341', # "The good Catholick no bad subject. Or, A letter from a Catholick gentleman to Mr. Richard Baxter. Modestly accepting the challenge by him made in his Sermon of repentance"
    'A96864', # "Divine poems being meditations upon several sermons"
    'A93332', # "A reply to a pamphlet called, Oaths no gospel-ordinance"
    'A95939', # "...Occasioned, by their attesting his delivering of certain positions, in a sermon at the leaguer"
    'A79568', # "The church defended, against Mr. Skingle's assize-sermon at Hertford In a letter to a friend. By a true lover of the orthodox clergie."
    'A77100', # "Paideia Thriamous. The triumph of learning over ignorance, and of truth over faleshood. Being an answer to foure quæries. Whether there be any need of universities? Who is to be accounted an hæretick? Whether it be lawfull to use coventicles? Whether a lay-man may preach? VVhich were lately proposed by a zelot, in the parish church at Swacie neere Cambridge, after the second sermon..."
    'A63877', # "A letter to the clergy of the diœcess of Ely from the Bishop of Ely ; before, and preparatory to his visitation."
    'A62992', # reply to a sermon 
    'A60864', # remarks on an answer to a sermon
    'A64639', # a letter with remarks on a sermon 
    'A64197', # "a soft answer to an angry sermon" 
    'A61683', # a letter with refllections on a book 
    'A48191', # a letter occasioned by a sermon 
    'A43685', # a vindication occasioned by a sermon 
    'A43806', # a letter and an answer 
    'A46883', # letters on Turkey, Jews, and Ethnic relations 
    'A40538', # an account of the Popish Plot, 1678 
    'A41496', # a letter occasioned by a sermon
    'A45149', # remarks occasioned  by a sermon
    'A48968', # answer to a late farewell sermon 
    'A55289', # poems occasioned by other poems and sermons upon the queen's death 
    'A54939', # a letter occasioned by a sermon 
    'A57258', # a letter concerning passages of a sermon 
    'A56278', # prayers used by preachers before or after sermons 
    'A58892', # a letter remarking to a sermon
    'A16497', # catechism regarding piety, including how "to heare sermons with profit"
    'A18267', # a dictionary of words borrowed from other languages 
    'A06013', # defence of a sermon 
    'A31039', # defence against a sermon 
    'A64394', # Terence's Latin dramas 
    'A77638', # a letter occasioned by a sermon
    'A78013', # a letter occasioned by Christopher Love's sermon 
    'A42577', # a letter examining a sermon 
    'A47973', # "A letter from a clergy-man in the country, to a minister in the city, concerning ministers intermedling with state-affairs in their sermons & discourse"
    'A42539', # "Upon the meeting of the sons of the clergy at a sermon preached before them in Saint Pauls church"
    'A09418', # how to "hear sermons with profit" 
    'A13299', # contains the preface and postscript before and after a sermon 
    'A30903', # apology for Quakerism 
    'A36190', # "Queries upon queries" regarding a sermon 
    'A31459', # the life of a minister 
    'A26859', # an answer to a sermon 
    'B28836', # a letter claiming inspiration from the Holy Spirit; labeled as "Astrology -- Sermons." and "Sermons, English" in subject headings,
    'A83012', # "The confident questionist questioned: or, the examination of the doctrine delivered by Mr. Thomas Willes in certain queries."
    'A84063', # Pastoral letters and charges; does not actually contain a sermon despite having the subject of "Sermons, English"
    'A90702', # does not actually contain the sermon text
    'A67411', # only contains two letters; "Theological discourses, in two parts the first containing VIII letters and III sermons concerning the blessed Trinity : the second, discourses & sermons on several occasions / by John Wallis ...",
    'A68546', # contains only the second half of the title, i.e., prayers of thanksgiving; "God be thanked A sermon of thanksgiuing for the happy successe of the English fleetes, sent forth by the honourable company of aduenturers to the East Indies. Preached to the honourable gouernors and committees, and the whole company, of their good ship, the Hope Marchant happily returened: at Deptford on Maundy Thursday last being the 29th of March. 1616. Hereunto are added sundry necessary and vseful formes of prayer and thankes-giuing for the helpe of all such as trauell by sea, fitted to their seruerall occasions. By Samuel Page Dr. in Diuinitie."
    'A65419', # letters occasioned by a sermon 
    'A11848', # only contains the title page; "Fury fiered, or, Crueltie scourged preached at S. Buttolphs without Bishops-gate, Nouem. 18. 1623 / by Iohn Sedguuick ..."
    'A18019', # only contains the title page; "Achitophel, or, The picture of a wicked politician devided into three parts : a treatise presented heretofore in three sermons to the Vniversitie of Oxford and now published / by Nathanael Carpent[er]."
    'A26426', # "Advertisement be [sic] Agnes Campbel relict of the deceast Master William Guthrie, minister of the Gospel, unto whose hands some printed papers called sermons, bearing the said Master William his name, may come."
    'B26622', # only contains a decree from a council 
    'A02216', # poem; "An Oration or funerall sermon vttered at Roome...faithfully translated out of the French copie"
]

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
        'A01956':'biblical_commentary', # being the summe of diuerse sermons preached in S. Gregories London 
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
        'A03634':{'prefatory_letter':[1]} # <DIV1 TYPE="prefatory letter">; [An homelye to be read in the tyme of pestylence]
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
