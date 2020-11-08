import urllib.request as urequest
from bs4 import BeautifulSoup
from collections import Counter
import time
import matplotlib.pyplot as plt
import time
from matplotlib.backends.backend_pdf import PdfPages
import urllib.parse
import unidecode
import seaborn as sns
from collections import Counter
from numpy import percentile
from journal_name_dictionary import journal_name_dict
import dill
from flask import Flask, request, render_template, Response, make_response
import itertools
from wordcloud import WordCloud, STOPWORDS 
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import random
import io
from matplotlib.pyplot import subplots
import os
import re
import numpy as np

app = Flask(__name__)
PEOPLE_FOLDER = os.path.join('static','folder')
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER


@app.route('/',methods=['GET','POST'])
def index2():
	print('***')
	errors = []
	results = {}
	if request.method == 'POST':
		year1 = request.form['number1']
		year2 = request.form['number2']
#		print(year1,year2)
		year1_file = year1 + '_title_research_area.pkd'
		year2_file = year2 + '_title_research_area.pkd'

		year1_results = dill.load(open(year1_file, 'rb'))
		year2_results = dill.load(open(year2_file, 'rb'))

	wordcloud1,researcharea1 = word_process_func(year1_results)
	wordcloud2,researcharea2 = word_process_func(year2_results)
	filename11 = print_wordcloud(wordcloud1)
	filename12 = print_wordcloud(wordcloud2)
	keys1,values1=list_flattener(researcharea1)
	filename21 = research_areas_bar(keys1,values1)
	keys2,values2=list_flattener(researcharea2)
	filename22 = research_areas_bar(keys2,values2)

	print('***')
	return render_template('tab.html', plot = [filename11,filename12,filename21,filename22])
#	return redirect(url_for('tab'), plot = [filename11,filename12,filename21,filename22])

def list_flattener(research_areas):
	research_areas = list(itertools.chain.from_iterable(research_areas))
	most_popular_areas = {key:value for key,value in sorted(Counter(research_areas).items(),reverse=True,key = lambda item:item[1])}
	keys = []
	values = []
	for key,value in most_popular_areas.items():
		keys.append(key)
		values.append(most_popular_areas[key])	
	return keys,values

def research_areas_bar(keys,values):
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.barh([re.sub('\s\(.+\)','',k) for k in keys[0:10]],values[0:10])
	canvas = FigureCanvas(fig)
	canvas.draw()
	millis = int(round(time.time() * 1000))
	filename = os.path.join(app.config['UPLOAD_FOLDER'], 'research_areas_' + str(millis) + '.jpg')
	fig.savefig(filename, bbox_inches='tight',format='jpg')
	return filename

def word_process_func(results):
    research_areas = []
    titles = []
    for ent in results:
      for title in ent[0]:
        titles.append(title)
      for area in ent[1]:
        research_areas.append(area)
    key_words = ''
    stopwords = set(STOPWORDS)

    more_stopwords = ['improving','origin','application','Influence','determination','quantification','robustness','calculate','Characteristics','region','generalization','enhance','Implications','creep','impact','predicting','point','zigzag','reconstruction','validation','studies','art','ground','analytic treatment','based simulations','related effects',
'using','based','effect','system','method',
                 'analysis','model']

    for title in titles:
            key_words += ' ' + title

    for words in more_stopwords:
            stopwords.add(words)

    wordcloud = WordCloud(width = 800, height = 800, background_color ='white', stopwords = stopwords, min_font_size = 10).generate(key_words)
#    print(wordcloud.words_)

    return wordcloud,research_areas

def print_wordcloud(wordcloud):
        fig = Figure(figsize = (8, 8), facecolor = None)
        ax = fig.add_subplot(1, 1, 1)
        ax.imshow(wordcloud)
        ax.axis("off")
        canvas = FigureCanvas(fig)
        canvas.draw()
        #TODO  generate filename randomly
        millis = int(round(time.time() * 1000))
        filename = os.path.join(app.config['UPLOAD_FOLDER'], 'wordcloud_' + str(millis) + '.jpg')
        #filename = os.getcwd() + '/test.jpg'
#        print(filename)
        fig.savefig(filename, format='jpg')
        return filename

@app.route('/tab')
def tab():
	return render_template('tab.html')
@app.route('/about')
def about():
       return render_template('about.html')
@app.route('/index')
def fig():
       return render_template('index.html')
@app.route('/trends')
def trends():
	filename11 = trends_fig([14, 28, 70, 146, 237, 271]
,np.arange(2015,2021),
'Neural Network','Total frequency')

	filename12 = trends_fig([100, 150, 108, 62, 14],np.arange(2016,2021),
'Neural Network','% increase from last year')

	filename21 = trends_fig([17, 26, 19, 28, 42, 42, 46, 15]
,np.arange(2013,2021),
'Black Hole','Total frequency')

	filename22 = trends_fig([52, -26, 47, 50, 0, 9, -67],np.arange(2014,2021),
'Black Hole','% increase from last year')
	

	return render_template('trends.html',trend_plots=[filename11,filename12,filename21,filename22])

def trends_fig(y,x,plot_title,ylabel):
        rise = y
        fig = Figure()
        x_range = x
        divs = int(abs(min(rise)-5 - max(rise)-20)/6.)
        y_range = np.arange(min(rise)-5,max(rise)+20,divs)
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(x_range,rise,marker='o',lw=2,markersize=12)
        ax.set_xticks(x_range)
        ax.set_yticks(y_range)
        ax.set_xticklabels(x_range,fontsize=12)
        ax.set_yticklabels(y_range,fontsize=12)
        ax.set_title(plot_title,fontsize=18)
        ax.set_ylabel(ylabel,fontsize=14)
        ax.set_xlabel('Year',fontsize=14)
        ax.axhline(0,color='k')

        canvas = FigureCanvas(fig)
        canvas.draw()
        millis = int(round(time.time() * 1000))
        filename = os.path.join(app.config['UPLOAD_FOLDER'], 'trend_' + str(millis) + '.jpg')
        fig.savefig(filename, format='jpg')
        return filename

if __name__ == '__main__':
        app.run(debug=True,port=8000)

