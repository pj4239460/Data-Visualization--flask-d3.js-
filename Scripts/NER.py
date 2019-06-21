
import spacy
import re
import pandas as pd
from spacy.tokens import Span
from spacy import displacy
import dateparser


corpus=pd.read_pickle("sources/corpus")
# # Functions 

# In[2]:


def find_all(a_str, sub):
    """Find all occurences of word in a text"""
    
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches


# In[3]:


def NoAccent(string):
    """Remove accent inside word"""
    
    accent=["â","é","è","ô","ù"]
    res=["a","e","e","o","u"]
    for i in range(len(res)):
        string=string.replace(accent[i],res[i])
    return string


# In[4]:


def findDate(text):
    """Find the Date. We considered that this code will be use just until 2099"""
#     04111985
#----------For the cases 22 Janvier 2017 and Janvier 2017-----------
    x=re.findall(r'\d\d\s(?:janvier|fevrier|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|decembre)(?:\s(?:20\d{2}|19\d{2})|(?:20\d{2}|19\d{2}))', text)
    if x:
        for xs in x:
            text1=text.replace(xs,"")
    else:
        text1=text
    x1=re.findall(r'(?:janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)(?:\s(?:20\d{2}|19\d{2})|(?:20\d{2}|19\d{2}))', text1)
#----------For the cases 22[/.\-_\ ]01[/.\-_\ ]2017 and 22[/.\-_\ ]01[/.\-_\ ]17-----------
    y=re.findall(r"[1-2]\d[/.\-_\ ](?:[0][1-9]|[1][0-2])[/.\-_\ ](?:20\d{2}|19\d{2})|[3][0-1][/.\-_\ ](?:[0][1-9]|[1][0-2])[/.\-_\ ](?:20\d{2}|19\d{2})",text1)
    if y:
        for ys in y:
            text1=text1.replace(ys,"")
    y1=re.findall(r"[1-2]\d[/.\-_](?:[0][1-9]|[1][0-2])[/.\-_]\d{2}|[3][0-1][/.\-_](?:[0][1-9]|[1][0-2])[/.\-_]\d{2}",text1)
#----------For the cases 22012017 and 220117-----------
    z=re.findall(r"[1-2]\d[0][1-9](?:20\d{2}|19\d{2})|[1-2]\d[1][0-2](?:20\d{2}|19\d{2})|[3][0-1][0][1-9](?:20\d{2}|19\d{2})|[3][0-1][1][0-2](?:20\d{2}|19\d{2})",text1)
    if z:
        for zs in z:
            text1=text1.replace(zs,"")
    z1=re.findall(r"[1-2]\d[0][1-9]\d{2}|[1-2]\d[1][1-2]\d{2}|[3][0-1][0][1-9]\d{2}|[3][0-1][1][0-2]\d{2}",text1)
    #----------For the cases 05[/.\-_\ ]01[/.\-_\ ]2017 and 05[/.\-_\ ]01[/.\-_\ ]17-----------
    b=re.findall(r"0[1-9][/.\-_\ ](?:[0][1-9]|[1][0-2])[/.\-_\ ](?:20\d{2}|19\d{2})|[1-2]\d[/.\-_\ ][1][0-2][/.\-_\ ](?:20\d{2}|19\d{2})|[3][0-1][/.\-_\ ](?:[0][1-9]|[1][0-2])[/.\-_\ ](?:20\d{2}|19\d{2})",text1)
    if b:
        for bs in b:
            text1=text1.replace(bs,"")
    b1=re.findall(r"0[1-9][/.\-_](?:[0][1-9]|[1][0-2])[/.\-_]\d{2}|[1-2]\d[/.\-_][1][0-2][/.\-_]\d{2}|[3][0-1][/.\-_](?:[0][1-9]|[1][0-2])[/.\-_]\d{2}",text1)
    #----------For the cases 05012017 and 050117-----------
    c=re.findall(r"0[1-9](?:[0][1-9]|[1][0-2])(?:20\d{2}|19\d{2})|[1-2]\d[1][0-2](?:20\d{2}|19\d{2})|[3][0-1](?:[0][1-9]|[1][0-2])(?:20\d{2}|19\d{2})",text1)
    if c:
        for cs in c:
            text1=text1.replace(cs,"")
    c1=re.findall(r"0[1-9](?:[0][1-9]|[1][0-2])\d{2}|[1-2]\d[1][0-2]\d{2}|[3][0-1](?:[0][1-9]|[1][0-2])\d{2}",text1)
    
    k=z1+b1+c1
    temp=[]
    for a in k:#to eliminate 01-02-84-23
        index=text1.find(a)
        if(index+len(a)<len(text1)):
            s=text1[index+len(a)]
            if not(s=="-" or s.isdigit()):
                temp.append(a)
    k=temp
    return x+x1+y+y1+z+b+k+c


# In[5]:


def blocf(df):
    """Build dictionnary with bloc fonctionnel and sous bloc fonctionnel"""
    
    bf={}
    #creation of list of "bloc fonctionnel"
    for l in list(df['Bloc fonctionnel']):
        if(type(l)!=float): #For deleting "NaN" which are in the dataframe
            l=NoAccent(l)
            bf[l.lower()]=[]
    df.index=list(range(len(df['Bloc fonctionnel'])))
    indexes=[i for i in df['Bloc fonctionnel'].index.values if type(df['Bloc fonctionnel'][i])!=float] #Only consider the non "NaN"
    #we are doing a loop on indexes to find the bf which is different to NaN
    #We analyse the structure of the excel file before created this kind of function
    for i in range(len(indexes)-1):
        l=df['Bloc fonctionnel'][indexes[i]].lower()
        l=NoAccent(l) #I used no accent because my corpus doesn't contains accent
        for j in range(indexes[i],indexes[i+1]):
            element=df['Sous bloc fonctionnel'][j].lower()
            element=NoAccent(element)
            bf[l].append(element.replace("\n"," "))
    #The last one bf
    l=df['Bloc fonctionnel'][indexes[-1]].lower()
    l=NoAccent(l)
    for j in range(indexes[-1],len(df['Bloc fonctionnel'])):
        element=df['Sous bloc fonctionnel'][j].lower()
        element=NoAccent(element)
        bf[l].append(element)
    return bf


# In[6]:


def taxonomy():
    """Build taxonomy for domain, bloc fonctionnel and sous bloc fonctionnel"""
    
    taxo={}
    xls = pd.ExcelFile('sources/Taxonomy For Domain bf and sbf.XLSX') #read excel file with multiple sheets
    sheet = xls.parse(2) #Go to the sheet which is important for us
    domaine=sheet.loc[(sheet["Domaine"].isnull()==False)]["Domaine"] #Delete NaN elements
    sn=xls.sheet_names #sheets name (1- signalisation 2-IFTE and so on)
    #creation of taxo domain
    for dom in domaine:
        dom1=dom[3:].lower()
        taxo[dom1]=[]
        if dom in sn:
            sheet=xls.parse(sn.index(dom))
            df=sheet.loc[(sheet["Sous bloc fonctionnel"].isnull()==False)]
            taxo[dom1].append(blocf(df))
    return taxo


# In[7]:


def nomenclatureTaxonomy():
    """Create taxonomy of nomenclature"""
    
    taxo={} #the returned dictionary
    xls1 = pd.ExcelFile('sources/Taxonomy for nomenclature and location.xlsx') #read excel file with multiple sheets
    sheet1 = xls1.parse(2) #Sheet Nomenclature
    groups=list(set(sheet1["Group"])) #the list of groups
    taxo={}
    for group in groups:
        nome={} #dictionary of nomenclature
        taxo[group]=[]
        nomen=list(set(sheet1["Nomenclature"][sheet1["Group"]==group])) #list of nomenclature which are part of the group
        color=list(set(sheet1["Color"][sheet1["Group"]==group]))
        for no in nomen:
            code=list(set(sheet1["Code"][sheet1["Nomenclature"]==no])) #list of code which are part of the nomnenclature
            nome[no.lower()]=[l.lower() for l in code]
        taxo[group].append(nome)
        taxo[group].append(color[0])
    return taxo


# In[74]:


def locationTaxonomyNew():
    """Create taxonomy of location"""
    
    taxo={} #the returned dictionary
    xls1 = pd.ExcelFile('sources/Taxonomy for nomenclature and location.xlsx') #read excel file with multiple sheets
    sheet1 = xls1.parse(1) #Sheet Location (code and place)
    codes=list(sheet1["Code"]) #List of codes
    for code in codes:
        l=list(sheet1["Place"][sheet1["Code"]==code]) #List of place
        taxo[code.lower()]=l[0].lower()
        
    return taxo


# In[8]:


def locationTaxonomy():
    """Create taxonomy of location"""
    
    taxo=[] #the returned list
    xls1 = pd.ExcelFile('sources/Taxonomy for nomenclature and location.xlsx') #read excel file with multiple sheets
    sheet1 = xls1.parse(1) #Sheet Location (code and place)
    codes=list(set(sheet1["Code"])) #List of codes
    for code in codes:
        l=list(sheet1["Place"][sheet1["Code"]==code]) #List of place
        taxo.append(code.lower())
        taxo.append(l[0].lower())
    return list(set(taxo))

def sortListbylength(l):
    """Sort list by the length of its elements"""
    
    temp=""
    for i in range(len(l)):
        for j in range(i,len(l)):
            if(len(l[j])>=len(l[i])):
                temp=l[i]
                l[i]=l[j]
                l[j]=temp
    return l


# In[9]:


def tag_placing(doc,tag,string,sent):
    """Add tag to the word "string" in text "sent" """
    
#     time1 = time.time()
    doc.vocab.strings.add(tag)  #add the new tag to the list of pre-existed tags
    TAG = doc.vocab.strings[tag] #convert it to a spacy vocab
    indexes=list(find_all(sent,string))
    if len(indexes)>0:
        st=string.split()
        #Find the indexes of token of the words which have been found
        token_pos=[token.i for token in doc if ((token.text.lower()==st[0] or token.text.lower()==st[0]+"s"))]
        token_pos_real=[]
        numberoftoken=len(list(doc))
        for i in token_pos:
            if(i+len(st)<=numberoftoken):
                spantext=Span(doc, i, i+len(st)).text.lower()
                if(spantext==string or spantext==string+"s"):
                    token_pos_real.append(i)
        tag1=tag #copy f our tag
        for i in token_pos_real:
            tag=tag1
            fb_ent = Span(doc, i, i+len(st)) # create a Span for the new entity
            if (fb_ent in doc.ents): #This part is for word with a lot of tag Signalisation--BF Batiment--BF for example
                j=doc.ents.index(fb_ent)
                ent=doc.ents[j].label_
                if(not(tag in ent)): #pre-existed tag
                    if not(ent in ['PER','ORG','LOC','MISC']):
                        tag=ent+' '+tag
                    doc.vocab.strings.add(tag) 
                    TAG=doc.vocab.strings[tag]
                    fb_ent = Span(doc, i, i+len(st), label=TAG)
                    doc.ents=list(doc.ents)+[fb_ent]#update the NER tag list
                    
            else:
                fb_ent = Span(doc, i, i+len(st), label=TAG)
                doc.ents=list(doc.ents)+[fb_ent] #update the NER tag list
#         time2 = time.time()
#         print(time2-time1)
        return len(token_pos_real)
    return 0


# In[52]:


def tagging(text,model): #corpus is a file with text here
    """The end of the work: tagging, add tag, show sentences with tag, return dataframe. Text with tag and list of tag are returned"""
    
    final=taxonomy() #Domain-BF-SBF taxonomy
    nomenclature=nomenclatureTaxonomy() #Nomenclature taxonomy
    location=["paris rive gauche","paris saint lazare","paris saint-lazare","paris st lazare","paris gare du nord",
              "paris gare de l’est","paris gare de lyon","paris sud est","paris austerlitz","paca",
              "paris montparnasse"]
    loctaxo=locationTaxonomyNew()
    temploc=[]
    #Change abbreviation to real name of the place
    keys=loctaxo.keys()

    for code in keys:
        code=code.lower()
        if not(code in ["marseille","st charles","lille,flandres"]):
            temploc.append(code)
    location1=temploc+list(loctaxo.values())
    location=list(set(location+location1)) #Location taxonomy
    location=sortListbylength(location)
    #--------------------------------------begin----------------------------------------------------------
#     file=open(corpus,"r")
#     sentences=file.readlines()
    keys=final.keys() #Take the domains
#--------------------------------------------Entitites color showing---------------------------------------
    ents=[] #entities list
    colors={} #colors of entities
    #-------------------------------------------Creation of result tables-------------------------------------------
    result={}
    data={"Date":0,"Refs":0,"Location":0,"Nomenclature":0}
    for dom in keys:
        data[dom]=0 #Number and the bf words for each domain
        data[dom+"--BF"]=0 #Number and the sbf words for each bf
        
#         data[dom]=[0,{}] #Number and the bf words for each domain
#         data[dom+"--BF"]=[0,{}] #Number and the sbf words for each bf

#--------------------------------------------Beginning of tagging-----------------------------------------------     

    text=NoAccent(text)
    text_raw=text
    doc = model(text) #Spacy nlp
    text=text.lower()
    for dom in keys: #each domain
        for doma in final[dom]: #domain dictionary
            keys1=doma.keys() #take the "bloc fonctionnel"
            tag=dom #tag for domain
            for bf in keys1: #each "bloc fonctionnel"
                for bf1 in doma[bf]: #each sbf
                    tag+=u"--BF--"+bf+"--SBF"
                    ents.append(tag.upper()) #Add the entity to the list "ents"
                    colors[tag.upper()]="#9DC19A" #"#1AFC0A" #color for "SBF" "#1AFC0A"
                    tagp=tag_placing(doc,tag.upper(),bf1,text) #add the tag  for "SBF"
                    data[dom+"--BF"]+=tagp
#                     if(tagp[0]>0):
#                         data[dom+"--BF"][1].append
                    tag=dom
                tag1=dom+"--BF"
                l=tag_placing(doc,tag1.upper(),bf,text) #place tag for "BF"
                if(l>0):
                    #Add more than one tag and specify the colors
                    m=[e.label_.split() for e in doc.ents]
                    for e in m:
                        s=" ".join(e)
                        if("SBF" in s):
                            continue
                        else:
                            if (len(e)>1): # and ("BF" in e)
                                ents.append(s.upper())
                                colors[s.upper()]="#A3A36D" #"#FFFF21"
                data[dom+"--BF"]+=l
                s=dom+"--BF"
                ents.append(s.upper())
                colors[s.upper()]="#A3A36D" #"#FFFF21"
        l=tag_placing(doc,u"DOMAINE",dom,text)#place tag for "Domain"
        data[dom]+=l
        ents.append(u"DOMAINE")
        colors[u"DOMAINE"]="#4D7A81" #"#06DFFF"
        ents=list(set(ents))
        doc.ents = [e for e in doc.ents if not e.text.isspace()]
        doc.ents=[e for e in doc.ents if not(e.label_ in ['PER','ORG','LOC','MISC'])] #final list of tag
    #-------------------------------Tag for location------------------------------------- 
    tag="LOCATION"
    ents.append(tag)
    colors[tag]="#815656" #"#FF0000"
    for loc in location:
        tagp=tag_placing(doc,tag,loc,text)
        data["Location"]+=tagp
    #------------------------------Tag for date----------------------------------
    tag="DATE"
    ents.append(tag)
    colors[tag]="#FFDFCA"#"#FFA500"
    refs=findDate(text)
    refs=list(set(refs))
    for ref in refs:
        tagp=tag_placing(doc,tag,ref,text)
        data["Date"]+=tagp
    #----------------------------------Tag for reference------------------------
    tag="REF"
    ents.append(tag)
    colors[tag]="#FFD7E9" #"#FF69B4" #Pink color
    refs=re.findall("[a-zA-Z]{2,3}\d{5}",text) #reference tagging
    refs=list(set(refs))
    for ref in refs:
        tagp=tag_placing(doc,tag,ref,text)
        data["Refs"]+=tagp
     #----------------------------------Tag for nomenclature------------------------
    groups=nomenclature.keys()
    for group in groups:
        color=nomenclature[group][1]
        tag="Nomenclature--"+group
        for nome_dic in nomenclature[group]: #0 is for the nomenclature and 1 for color of tagging for the group
            try:
                keys2=nome_dic.keys()
            except AttributeError: #Because color isn't placed like a dictionary but like an element in the nomenclature dataframe
                continue
            for nome in keys2:
                code=nome_dic[nome][0]
                tagp=tag_placing(doc,tag.upper(),code,text)
                data["Nomenclature"]+=tagp
        ents.append(tag.upper())
        colors[tag.upper()]=color
            
#     df=pd.DataFrame(data)
#     df.index=["Frequency"]
    keys=data.keys()
    tag_list=[(key,data[key]) for key in keys if data[key]!=0] #List of tags and their occurences
    options = {'ents': ents, 'colors': colors} #the options for future display
    doc_return=[doc,options]
    return doc_return #the doc is for search_tag function


# In[88]:


def ListofTagInsidedoc(text): #corpus is a file with text here
    """The final of the work: tagging, add tag, show sentences with tag, return dataframe. Text with tag and list of tag are returned"""
    
    final=taxonomy() #Domain-BF-SBF taxonomy
    nomenclature=nomenclatureTaxonomy() #Nomenclature taxonomy
    location=["paris rive gauche","paris saint lazare","paris saint-lazare","paris st lazare","paris gare du nord",
              "paris gare de l’est","paris gare de lyon","paris sud est","paris austerlitz","paca",
              "paris montparnasse"]
    loctaxo=locationTaxonomyNew()
    temploc=[]
    #Change abbreviation to real name of the place
    keys=loctaxo.keys()

    for code in keys:
        code=code.lower()
        if not(code in ["marseille","st charles","lille,flandres"]):
            temploc.append(code)
    location1=temploc+list(loctaxo.values())
    location=list(set(location+location1)) #Location taxonomy
    location=sortListbylength(location)
    #--------------------------------------begin----------------------------------------------------------
#     file=open(corpus,"r")
#     sentences=file.readlines()
    keys=final.keys() #Take the domains
    #-------------------------------------------Creation of result tables-------------------------------------------
    result={}
    data={"Date":0,"Reference":0,"Location":0,"Nomenclature":0}
    for dom in keys:
        data[dom]=0 #Number and the bf words for each domain
        data[dom+"--BF"]=0 #Number and the sbf words for each bf
        data[dom+"--SBF"]=0

#--------------------------------------------Beginning of tagging-----------------------------------------------     

    text=NoAccent(text)
    text=text.lower()
    for dom in keys: #each domain
        for doma in final[dom]: #domain dictionary
            keys1=doma.keys() #take the "bloc fonctionnel"
            for bf in keys1: #each "bloc fonctionnel"
                for bf1 in doma[bf]: #each sbf
                    indexes=list(find_all(text,bf1))
                    data[dom+"--SBF"]+=len(indexes)
                indexes=list(find_all(text,bf))
                data[dom+"--BF"]+=len(indexes)
        indexes=list(find_all(text,dom))
        data[dom]+=len(indexes)
    #-------------------------------Tag for location------------------------------------- 
    place=[]
    keys=loctaxo.keys()
    for loc in location:
        indexes=list(find_all(text,loc))
        if(indexes):
            text=text.replace(loc,"") #for avoiding counting lazare - saint lazare - paris saint lazare a lot of time
            if loc in keys: #For abbreviations
                check=(loctaxo[loc],len(indexes))
                temp=[l[0] for l in place]
                if (check[0] in temp): #Check if the real location is already detected
                    index=temp.index(check[0])
                    place[index]=(check[0],place[index][1]+len(indexes))
                else:
                    place.append(check)
            else:
                place.append((loc,len(indexes)))
            data["Location"]+=len(indexes)
    #------------------------------Tag for date----------------------------------
    refs=findDate(text)
    refs=list(set(refs))
    for ref in refs:
        indexes=list(find_all(text,ref))
        data["Date"]+=len(indexes)
    #----------------------------------Tag for reference------------------------
    for ref in refs:
        indexes=list(find_all(text,ref))
        data["Reference"]+=len(indexes)
     #----------------------------------Tag for nomenclature------------------------
    groups=nomenclature.keys()
    for group in groups:
        for nome_dic in nomenclature[group]: #0 is for the nomenclature and 1 for color of tagging for the group
            try:
                keys2=nome_dic.keys()
            except AttributeError: #Because color isn't placed like a dictionary but like an element in the nomenclature dataframe
                continue
            for nome in keys2:
                code=nome_dic[nome][0]
                indexes=list(find_all(text,code))
                data["Nomenclature"]+=len(indexes)
    keys=data.keys()
    tag_list=[[key,data[key]] for key in keys if data[key]!=0] #List of tags and their occurences
    print(place)
    return tag_list 


# # Real work

# In[12]:


def getListofTag(dataset,nlp):
    """return dataframe with name and list of tag"""
    
#     nlp=spacy.load('fr_core_news_sm') #Load the pre-existed french model of spacy
    data={"Name":dataset["Name"],"Tag":[]}
    tags=[]
    for text in dataset["Text"]:
        tags.append(ListofTagInsidedoc(text))
    data["Tag"]=tags
    return pd.DataFrame(data)


# In[13]:


def getTextTagged(dataset):
    """return dataframe with name and text which is tagged and the options for visualization"""
    
#     nlp=spacy.load('fr_core_news_sm') #Load the pre-existed french model of spacy
    data={"Name":dataset["Name"],"TextTagged":[]}
    texttagged=[]
    for text in dataset["Text"]:
        ret=tagging(text,nlp)
        texttagged.append(ret[0])
    data["TextTagged"]=texttagged
    return pd.DataFrame(data)

def legendTag(text):
    """Legend for specific text tagged"""
    
    dic={"SBF":"SOUS BLOC FONCTIONNEL","BF":"BLOC FONCTIONNEL","REF":"REFERENCE"}
    keys=dic.keys()
    temp=re.findall(r"(?<=>).*(?=span>)",text) #find TAGS which are located between ">" and "</span>"
    tags=[res[:-2] for res in temp] #just to delete </ from the results
    temp=re.findall(r"(?<=background:\s).*(?=;)",text) #find colors which are located between "background: " and ";"
    colors=[res[:res.find(";")] for res in temp] #Just consider the first ; among the others which are found inside the last answers
    tempindexes=[colors.index(x) for x in set(colors)] #Find the first indexes of the occurences colors
    colors=[colors[i] for i in tempindexes] #Find the equivalent colors
    temptags=[tags[i] for i in tempindexes] #Find the equivalent tags
    temp1=[[temptags[i],colors[i]] for i in range(len(temptags)) if "NOMENCLATURE" in temptags[i]] #Find the [tags,colors] related to NOMENCLATURE
    temp2=[[temptags[i],colors[i]] for i in range(len(temptags)) if not([temptags[i],colors[i]] in temp1)] #Find the others
    temp2=[[l[0].split("--")[-1],l[1]] for l in temp2] #This part take place here because we want to show one tag for BF and not all the tags for it
    for i in range(len(temp2)):
        a=temp2[i][0]
        if a in keys:
            temp2[i][0]=dic[a]
    final=temp1+temp2 #list of [TAG,COLOR]
#     final=[list(item) for item in set(tuple(row) for row in final)] #set list of list
    
    return final

def showTextwithTag(l):
    """Use list l=[nlp doc, displacy options] to show the text tagged"""
    
    doc=l[0] #the nlp doc
    options=l[1] #displacy options
    return displacy.render(doc, style='ent', options=options)

	
def showTextTagged(name,nlp):
    """Show the texttagged just with giving the name of the document"""

    texts=list(corpus.loc[corpus["Name"]==name,"Text"])
    if(texts):
        l=tagging(texts[0],nlp)
        tags=showTextwithTag(l)
        legend=["".join(l) for l in legendTag(tags)]
        legends=";".join(legend)
        return tags+legends
    return "The file you asked is not inside the file system or it's a schema.  Try with another one."

def showTextTagged1(name,nlp):
	"""Show the texttagged just with giving the name of the document"""
	
	names=list(corpus.loc[corpus["Name"]==name,"Text"])
	if(names):
		l=tagging(names[0],nlp)
		return showTextwithTag(l)
	return "The file you asked is not inside the file system or it's a schema.  Try with another one."
	

