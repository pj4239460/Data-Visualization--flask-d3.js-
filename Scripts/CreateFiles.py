

#get_ipython().system('pip install geopy')
#get_ipython().system('pip install dateparser')
import pandas as pd
import dateparser
import datetime
from geopy.geocoders import GoogleV3,OpenMapQuest,GeoNames, Nominatim, Here
from geopy.exc import GeocoderQuotaExceeded

def locationTaxonomyNew():
    """Create taxonomy of location"""
    
    taxo={} #the returned dictionary
    xls1 = pd.ExcelFile('sources/code1.xlsx') #read excel file with multiple sheets
    sheet1 = xls1.parse(1) #Sheet Location (code and place)
    codes=list(sheet1["Code"]) #List of codes
    for code in codes:
        l=list(sheet1["Place"][sheet1["Code"]==code]) #List of place
        taxo[code.lower()]=l[0].lower()
    return taxo


# In[4]:


def find_map_coordinates(full_address, geolocator):
    """Function to find latitude and longtitude for the address."""
    
    # Create geocoder object
    location = geolocator.geocode(full_address)
    return location.latitude, location.longitude


# In[5]:


def PlaceToMap(dataset):
    """Build dataframe with place and the list of documents which are located there"""
    
    #-----------------------Group by location--------------------
    location=list(dataset["Place"])
    temp=[]
    for loc in location:
        temp+=loc
    location=list(set(temp))
    length=len(location)
#     data={"Place":[0]*length,"Documents":[0]*length}  
    data={"Place":[],"Documents":[]}  
    for m in range(length):    
        temp=[]
        event=location[m]
        locs=event
        for j,i in zip(dataset["Name"],dataset["Place"]):
        	if locs in i:
        		temp.append(j)
        if not(locs in data["Place"]):
            data['Place'].append(locs)
            temp=list(set(temp))
            data["Documents"].append(temp)
    dataset=pd.DataFrame(data)
    #--------------------Beginning for locatalization--------------
    geolocator = OpenMapQuest(api_key='kNFyXsWRe50Q85tXM8szsWN0A3SS3X0T',timeout=100)
    #geolocator=Here("Af9fc3JTNkg1N4IwwVEz","3_R3z-sJU6D1BEFE9HWy7Q")
#     geolocator=GeoNames(username="gerard.daligou")
    length=dataset.shape[0]
    data={"Place":dataset["Place"],"Documents":dataset["Documents"],"Coordinate":[0]*length,"Count":[0]*length}
    for i in range(length):
        place=dataset["Place"][i]
        try:
            data["Coordinate"][i]=[place,find_map_coordinates(place,geolocator)]
        except GeocoderQuotaExceeded:
            continue
        except AttributeError:
            geolocator1=GeoNames(username="gerard.daligou",timeout=100)
#             print(find_map_coordinates(place,geolocator1))
            data["Coordinate"][i]=[place,find_map_coordinates(place,geolocator1)]
        data["Count"][i]=len(data["Documents"][i])
    return pd.DataFrame(data)

def createMapfiles(dfDirectory):
	"""Create the file for coordinates from dataframe"""

	product=pd.read_pickle(dfDirectory) #"../DATA/df1"
	df=PlaceToMap(product)

	"""Create txt file for localisation on the html map"""

	file=open("templates/Final/coordinate.txt","w", encoding="utf-8")
	string="<script>\n"
	for i,j,k in zip(df["Coordinate"],df["Count"],df["Place"]):
	    string+="L.marker(["+str(i[1][0])+","+str(i[1][1])+"],{icon: new L.AwesomeNumberMarkers({number:"+str(j)+", markerColor: color}),"
	    string+="title:'"+k+"'})"
	    string+=".addTo(map).bindTooltip('"+k+"',{ permanent: true,direction:'center',offset:[0,60]}).on('click', showlist); \n"

	string+="function showlist(e){var title=this.options.title;\n"
	string+="$.post('/markerclick',{title:title},function(response){$('#docsname').html(response);})\n}"
	string+="</script>"
	file.write(string)
	df.to_pickle("sources/coordinate")

	"""Get the list of name of the documents to show it inside the demo """
	df1=pd.read_pickle(dfDirectory)
	length=df1.shape[0]
	names=list(df1["Name"])
	names=sorted(names)
	file=open("templates/Final/nameslist.txt","w", encoding="utf-8")
	file.write("<p style='font-size: 200%; text-align:center'>Documents:("+str(length)+")</p><br>\n")
	for name in names:
		name1=name
		name=name.replace("'","__1")
		string="<a href='#' style='text-decoration: none;color:black;' onclick=\"showTTagged('"+name+"')\">- "+name1+"</a><br>\n"
		file.write(string)

def FindListofDoc(place):
    """Return the list of document where we can find the place"""
    
    df=pd.read_pickle("sources/coordinate")
    docs=list(df.loc[df["Place"]==place,"Documents"])
    string="<p style='font-size: 200%; text-align:center'>Documents for "+place+":</p><br>\n"
    for name in docs[0]:
    	name1=name
    	name=name.replace("'","__1")
    	string+="<a href='#' style='text-decoration: none;color:black;' onclick=\"showTTagged('"+name+"')\">- "+name1+"</a><br>\n"
    return string

def CreateTimelinefiles(dfDirectory):
	"""Create file timeline.txt and timelinedoc.txt for showing timeline"""

	product=pd.read_pickle(dfDirectory)
	dates=product.copy()
	dates=dates.sort_values(by=["Date"]).reset_index(drop=True)
	#for i, j  in enumerate(dates["Date"]):
	 #   if j is not "":
	  #      dates.loc[i,"Date"] = dateparser.parse(j).date()

	"""This script is for creating a js code for the timeline. You will below an example of one part of the js """
	length=dates.shape[0]
	file1=open("templates/Final/js/timeline.js","w", encoding="utf-8")
	#We want only the docs with date 
	withdate=list(dates.loc[dates["Date"]!=""].index) #the indexes
	truedate=[dates["Date"][i] for i in withdate] #the dates
	truedate=list(set(truedate)) #the unique dates
	truedate=sorted(truedate)
	onlydate=sorted(list(set([l.split("-")[0] for l in truedate])))
	#dic with the dates (only the year) and the list of docs which are related to the date
	doclist=[(date,[list(dates.loc[dates["Date"]==realdate,"Name"]) for realdate in truedate if realdate.split("-")[0]==date ]) for date in onlydate]
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
		name1=name
		name=name.replace("'","__1")
		string2+="<a href='#' style='text-decoration: none;color:black;' onclick='showTTagged(\\\""+name+"\\\")'>"+name1+"</a><br>"
	string+='"taskDetails": "'+string2+'"' #show all the docs which are related to the date inside a html paragraph
	string+='},\n'
	for info in doclist[1:]: #Do the same with this loop but for the other date
	    date=info[0]
	    string+='{"isSelected": "",\n "taskTitle": "Documents('+str(len(info[1]))+'/'+str(len(withdate))+')",\n'
	    string+='"taskSubTitle": "",\n "assignDate": "'+date+'/01/01'+'",\n "taskShortDate": "'+date+'",\n'
	    string2=""
	    for name in info[1]:
	    	name1=name
	    	name=name.replace("'","__1")
	    	string2+="<a href='#' style='text-decoration: none;color:black;' onclick='showTTagged(\\\""+name+"\\\")'>"+name1+"</a><br>"
	    string+='"taskDetails": "'+string2+'"'
	    string+='},\n'
	string+='];'
	string+="var jtLine = $('.myjtline').jTLine({\n callType: 'jsonObject',\n structureObj: myMappedObject,\n map: {\n"
	string+='"dataRoot": "/",\n "title": "taskTitle",\n "subTitle": "taskSubTitle",\n "dateValue": "assignDate",\n'
	string+='"pointCnt": "taskShortDate",\n "bodyCnt": "taskDetails"},}); });' #end of timeline.js file
	file1.write(string)

	"""Txt file for showing documents without date"""
	length1=product.shape[0]
	names=list(product.loc[product['Date']==""]["Name"])
	names=sorted(names)
	file=open("templates/Final/withoutdate.txt","w", encoding="utf-8")
	string="<p style='font-size: 200%; text-align:center'>Documents without date("+str(len(names))+"/"+str(length1)+"):</p><br>\n"
	file.write(string)
	for name in names:
		name1=name
		name=name.replace("'","__1")
		string="<a href='#' style='text-decoration: none;color:black;' onclick=\"showTTagged('"+name+"')\">- "+name1+"</a><br>\n"
		file.write(string)

def screening(df):
    """Produce a html table for screening but without the text. Text will be found inside corpus dataframe during the processing"""
    
    #<div class='table-responsive'></div>
    string="<table id='screening' class='table table-striped table-bordered' style='border: solid black 2px;width:100%'><thead><tr><th>#</th>"
    length=df.shape[0]
    nbrecolumn=df.shape[1]
    columns=list(df.columns.values)
    #Give the different columns
    nameindex=columns.index("Name")
    actifs=columns.index("Actifs")
    place=columns.index("Place")
    date=columns.index("Date")
    for col in columns:
    	if col=="Date":
    		string+="<th style='font-weight:bold;text-align:center' class='col-lg-2'>"+col+"</th>"
    	else:
    		string+="<th style='font-weight:bold;text-align:center'>"+col+"</th>"
    string+="</tr></thead><tbody>"
    for i in range(length):
        values=list(df.loc[i])
        name=values[nameindex]
        name=name.replace("'","__1")
        string+="<tr ><td onclick='showTTagged(\""+name+"\")'><span>"+str(i+1)+"</span></td>"
        for val in values:
        	#if values.index(val) in [actifs,place]:
        	#	string+="<td style='text-align:center'><div style='overflow-y:auto;height:100px'>"+str(val)+"</div></td>"
        	#else:
        	string+="<td style='text-align:center'><span>"+str(val)+"</span></td>"
        string+="</tr>"
    string+="</tbody></table>"
    
    return string

def editdf(csv_string,directory):
    file=open("temp.csv","w", encoding="utf-8")
    rep=["&","<",">","\"","'"]
    esc=["&amp;","&lt;","&gt;","&quot;","&apos;"];
    for i in range(len(rep)):
        csv_string=csv_string.replace(esc[i],rep[i])
    file.write(csv_string)
    df=pd.read_csv("temp.csv",sep=";", na_filter=False)
    df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)
    df.to_pickle(directory)
    return str(df.shape)   #str(df.shape) 
