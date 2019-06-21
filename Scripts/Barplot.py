import pandas as pd
from collections import Counter
import plotly
import colorlover as cl
from plotly.offline import download_plotlyjs, plot
import shutil
import os
import re

df = pd.read_pickle("sources/df2")

def graph(feature1, feature2):
    #if feature 1 equals feature2
    if (os.path.isfile("templates/Final/barplot.html")):
    	os.remove("templates/Final/barplot.html")
    	print(1)
    if feature1 == feature2:
        if type(df[feature1][0]) == str:
            values = df[feature1].tolist()
        else:
            values = []
            for liste in df[feature1]:
                values.extend(liste)
        dict_values = Counter(values)
        x = list(dict_values.keys())
        y = list(dict_values.values())
        data = [dict(type="bar", x = x, y = y, marker = dict(color=cl.scales['11']['div']['RdYlBu'][8]))]
        layout = dict(barmode='basic')
        plotly.offline.plot({"data": data, "layout": layout}, validate=False,auto_open=False,filename="templates/Final/barplot.html")
        return "Finish"
    
    #if feature1 different of feature
    dictionnary = {}
    
    #Get the different categories
    if type(df[feature1][0]) == str:
        keys = df[feature1].unique().tolist()
    else :
        temp = []
        for liste in df[feature1]:
            temp.extend(liste)
        keys = list(set(temp))
        
    #Create the dictionnary for doing the counting
    for key in keys:
        dictionnary[key] = []
        
    #Choose the colors for legends
    colors = {}
    
    if type(df[feature2][0]) == str:
        colors_keys = df[feature2].unique().tolist()
    else :
        temp = []
        for liste in df[feature2]:
            temp.extend(liste)
        colors_keys = list(set(temp))
        
    #Generate the color palet
    palet = []
    temp = []
    for key in list(cl.scales['9'].keys()):
        temp.extend(list(cl.scales['9'][key].values()))
    temp = [item for sublist in temp for item in sublist]

    for rgb in temp:
        r = re.findall("[0-9]+", rgb)[0]
        g = re.findall("[0-9]+", rgb)[1]
        b = re.findall("[0-9]+", rgb)[2]
        if (10 < int(r) < 220 and 10 < int(g) < 220 and 10 < int(b) < 220) and int(r) != int(g) != int(b):
            palet.append(rgb)

    #Generates the colors for each category
    for i, key in enumerate(colors_keys):
            colors[key] = palet[i-(i//len(palet))*len(palet)]
    
    #Fill the dictionnary
    for key in keys:
        for i in range(len(df)):
            if key in df[feature1][i]:
                if type(df[feature2][i]) == str:
                    dictionnary[key].append(df[feature2][i])
                else:
                    dictionnary[key].extend(df[feature2][i])
    
    #Count the different elements
    for key in keys:
        dictionnary[key] = Counter(dictionnary[key])
    
    #Create the data for the graph
    data = []
    for i,keys in enumerate(dictionnary):
        for j, value in enumerate(list(dictionnary[keys].values())):
            if i == 0:
                data.append(dict(type='bar', legendgroup ='group', marker=dict(color = colors[list(dictionnary[keys].keys())[j]]), x=[keys], y=[value], name=list(dictionnary[keys].keys())[j], transforms = [dict(type = 'filter', value=[keys])]))
            else:
                data.append(dict(type='bar', legendgroup ='group', marker=dict(color = colors[list(dictionnary[keys].keys())[j]]), showlegend=False, x=[keys], y=[value],name=list(dictionnary[keys].keys())[j], transforms = [dict(type = 'filter', value=[keys])]))
    layout = dict(barmode='stack')
    res=plotly.offline.plot({"data": data, "layout": layout},validate=False,auto_open=False,filename="templates/Final/barplot.html")
    return "finish"
