
# coding: utf-8

# In[1]:


import pandas as pd
import dateparser
import datetime


# In[2]:


product=pd.read_pickle("../DATA/df1")


# In[3]:


dates=product.copy()


# In[4]:


dates=dates.sort_values(by=["Date"]).reset_index(drop=True)


# In[5]:


for i, j  in enumerate(dates["Date"]):
    if j is not "":
        dates.loc[i,"Date"] = dateparser.parse(j).date()


# In[9]:


"""This script is for creating a js code for the timeline. You will below an example of one part of the js """

#  $(document).ready(function () {
# var myMappedObject = [
#                   {
#                       "isSelected": "true",
#                       "taskTitle": "My First Point 1",
#                       "taskSubTitle": "January 16th, 2014",
#                       "assignDate": "16/01/2014",
#                       "taskShortDate": "16 Jan",
#                       "taskDetails": "hi <span style=\"color:red\">my html content</span> other text"
length=dates.shape[0]
file1=open("../DATA/timeline.js","w")
#We want only the docs with date 
withdate=list(dates.loc[dates["Date"]!=""].index) #the indexes
truedate=[str(dates["Date"][i]) for i in withdate] #the dates
truedate=list(set(truedate)) #the unique dates
truedate=sorted(truedate)
onlydate=sorted(list(set([l.split("-")[0] for l in truedate])))
#dic with the dates (only the year) and the list of docs which are related to the date
doclist=[(date,[list(dates.loc[dates["Date"]==dateparser.parse(realdate).date(),"Name"]) for realdate in truedate if realdate.split("-")[0]==date ]) for date in onlydate]
docs=[]
for s in doclist:
    temp=[]
    for l in s[1]:
        temp+=l
    docs.append((s[0],temp))
doclist=docs
date=doclist[0][0] #open the timeline with the first date
string="$(document).ready(function () {\n var myMappedObject = [\n"
string+='{"isSelected": "true",\n "taskTitle": "Documents('+str(len(doclist[0][1]))+'/'+str(len(withdate))+')",\n'
string+='"taskSubTitle": "",\n "assignDate": "'+date+'/01/01'+'",\n "taskShortDate": "'+date+'",\n'
string2=""
for name in doclist[0][1]:
    string2+="<p>"+name+"</p>"
string+='"taskDetails": "'+string2+'"' #show all the docs which are related to the date inside a html paragraph
string+='},\n'
for info in doclist[1:]: #Do the same with this loop but for the other date
    date=info[0]
    string+='{"isSelected": "",\n "taskTitle": "Documents('+str(len(info[1]))+'/'+str(len(withdate))+')",\n'
    string+='"taskSubTitle": "",\n "assignDate": "'+date+'/01/01'+'",\n "taskShortDate": "'+date+'",\n'
    string2=""
    for name in info[1]:
        string2+="<p>"+name+"</p>"
    string+='"taskDetails": "'+string2+'"'
    string+='},\n'
string+='];'
string+="var jtLine = $('.myjtline').jTLine({\n callType: 'jsonObject',\n structureObj: myMappedObject,\n map: {\n"
string+='"dataRoot": "/",\n "title": "taskTitle",\n "subTitle": "taskSubTitle",\n "dateValue": "assignDate",\n'
string+='"pointCnt": "taskShortDate",\n "bodyCnt": "taskDetails"},}); });' #end of timeline.js file
file1.write(string)


# In[ ]:


"""Txt file for showing documents without date"""
names=list(product.loc[product['Date']==""]["Name"])
file=open("../DATA/withoutdate.txt","w")
string="<p style='font-size: 200%; text-align:center'>Documents without date:</p><br>\n"
file.write(string)
for name in names:
    string="<p>- "+name+"</p>\n"
    file.write(string)


# In[10]:


pippo=list(dates["Date"])


# In[11]:


minnie = [x for x in pippo if x is not ""]


# In[12]:


pluto = [(x-datetime.date(2000,1,1)).total_seconds() for x in minnie]


# In[13]:


duck = [x for x in pluto if x>0]


# In[14]:


donald = [x for x in pluto if x<0]


# In[15]:


len(donald)


# In[16]:


import matplotlib.pyplot as plt


# In[17]:


plt.hist(duck,bins=100)
plt.show()


# In[18]:


### date=list(dates["Date"])


# In[19]:


date=list(set(date))


# In[20]:


date=[str(d) for d in date if d!=""]


# In[21]:


base=min(date)
x=[]

