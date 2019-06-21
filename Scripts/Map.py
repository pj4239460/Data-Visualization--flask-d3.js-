
# coding: utf-8

# # Packages

# In[1]:


get_ipython().system('pip install geopy')


# In[2]:


from geopy.geocoders import GoogleV3,OpenMapQuest,GeoNames
from geopy.exc import GeocoderQuotaExceeded
import pandas as pd


# # Functions

# In[3]:


def locationTaxonomyNew():
    """Create taxonomy of location"""
    
    taxo={} #the returned dictionary
    xls1 = pd.ExcelFile('../DATA/code1.xlsx') #read excel file with multiple sheets
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
    location=["paris rive gauche","paris saint lazare","paris saint-lazare","paris st lazare","paris gare du nord",
              "paris gare de l’est","paris gare de lyon","paris sud est","paris austerlitz","paca",
              "paris montparnasse"]
    loctaxo=locationTaxonomyNew() 
    temploc=[]
    keys=loctaxo.keys() #Change abbreviation to real name of the place
    for code in keys:
        code=code.lower()
        if not(code in ["marseille","st charles","lille","flandres"]):
            temploc.append(code)
    location1=temploc+list(loctaxo.values())
    location=list(set(location+location1))
    length=len(location)
#     data={"Place":[0]*length,"Documents":[0]*length}  
    data={"Place":[],"Documents":[]}  
    for m in range(length):    
        temp=[]
        event=location[m]
        if event in keys:
            locs=loctaxo[event] #change the abbreviation to the real place
        else:
            locs=event #Keep the real name of the place
        for j,i in zip(dataset["Name"],dataset["Place"]):
            if locs in i:
                temp.append(j)
        if not(locs in data["Place"]):
            data['Place'].append(locs)
            data["Documents"].append(temp)
    dataset=pd.DataFrame(data)
    #--------------------Beginning for locatalization--------------
    geolocator = OpenMapQuest(api_key='kNFyXsWRe50Q85tXM8szsWN0A3SS3X0T')
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
            geolocator1=GeoNames(username="gerard.daligou")
#             print(find_map_coordinates(place,geolocator1))
            data["Coordinate"][i]=[place,find_map_coordinates(place,geolocator1)]
        data["Count"][i]=len(data["Documents"][i])
    return pd.DataFrame(data)


# # Launching

# In[6]:


product=pd.read_pickle("../DATA/df1")


# In[7]:


df=PlaceToMap(product)


# In[8]:


"""Create the final dataframe for localisation"""

data={"paris saint-lazare":["paris saint lazare", "paris st lazare", "saint lazare", ],
     "gare de marseille saint charles":["gare de marseille st charles","paca"],
     "paris austerlitz":["paris tolbiac"]}
keys=data.keys()
for key in keys:
    pippo=list(df.loc[df["Place"]==key,"Documents"])
    exact_index=list(df["Documents"][df["Place"]==key].index)[0]
    for value in data[key]:
        other_index=list(df["Documents"][df["Place"]==value].index)[0]
        pippo[0]+=list(df.loc[df["Place"]==value,"Documents"])[0]
        df.drop(other_index, inplace=True)
    minnie=list(set(pippo[0]))
    df["Documents"][exact_index]=minnie
    df["Count"][exact_index]=len(minnie)
df.reset_index(drop=True,inplace=True)


# In[9]:


df.to_pickle("../DATA/coordinate")


# In[10]:


"""Create txt file for localisation on the html map"""

file=open("../DATA/coordinate.txt","w")
string="<script>"
file.write(string)
for i,j,k in zip(df["Coordinate"],df["Count"],df["Place"]):
    string="L.marker(["+str(i[1][0])+","+str(i[1][1])+"],{icon: new L.AwesomeNumberMarkers({number:"+str(j)+", markerColor: color})})"
    string+=".addTo(map).bindTooltip('"+k+"',{ permanent: true,direction:'center',offset:[0,60]});\n"
    file.write(string)
string="</script>"
file.write(string)


# In[19]:


names.loc[0,"Name"]


# In[34]:


"""Get the list of name of the documents to show it inside the demo """
df1=pd.read_pickle("../DATA/df1")
length=df1.shape[0]
file=open("../DATA/nameslist.txt","w")
file.write("<p style='font-size: 200%; text-align:center'>Documents:</p><br>\n")
for i in range(length):
    string="<p>- "+df1.loc[i,"Name"]+"</p>\n"
    file.write(string)

