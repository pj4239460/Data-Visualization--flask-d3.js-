#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, render_template, request
from Scripts.CreateFiles import *
from Scripts.Barplot import *
from Scripts.NER import *




app = Flask(__name__, static_folder='templates/Final')
dfDirectory="sources/df2"
res1=createMapfiles(dfDirectory)
res2=CreateTimelinefiles(dfDirectory)
nlp=spacy.load('fr_core_news_sm')
	

@app.route('/')
#@cache.cached(timeout=50)
def index():
    return render_template('Final/index.html')
@app.route('/markerclick', methods=['POST'])
def click():
	return FindListofDoc(request.form['title'])
@app.route('/graph', methods=['POST'])
def plot():
	return graph(request.form['sel1'],request.form['sel2'])
@app.route('/tag', methods=['POST'])
def ner():
	name=request.form['name']
	return showTextTagged(name,nlp)
@app.route('/screening', methods=['POST'])
def screen():
	df=pd.read_pickle("sources/df3")
	return screening(df)
@app.route('/editdataframe', methods=['POST'])
def editdataframe():
	result=request.form['result']
	directory="sources/df3"
	return editdf(result,directory)


if __name__ == '__main__':
    app.run(debug=True)
