from flask import Flask, render_template, request, redirect
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, TextInput
from bokeh.plotting import figure, output_file
from bokeh.layouts import widgetbox
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
import numpy as np


app = Flask(__name__)

@app.route('/')
def index():
    ts = TimeSeries(key='TB30LW5U413LFEYU',output_format='pandas')
    data, meta_data = ts.get_daily(symbol='GOOGL',outputsize='full')


    value = []
    dates = []
    for j in range(4):
        for i in range(10):
            if j*10 + i < 32:
                try:
                    value.append(data.loc['2020-04-%d%d 00:00:00'%(j,i)].values)
                    dates.append('04/%d%d'%(j,i))
                except:
                    pass
    value = np.array(value)

    N = len(value.T[1])

    x = np.arange(N)
    openval = value.T[0]
    closeval = value.T[2]


    source = ColumnDataSource(data=dict(x=x,y=closeval))
    plot = figure(plot_height=400,plot_width=600,title='GOOGL Closing Price',tools='crosshair,pan,reset,save,wheel_zoom')
    plot.xaxis.ticker = [i*2 for i in range(N//2)]
    dictionary = {int(i):j for i,j in zip(np.arange(N),dates)}
    plot.xaxis.major_label_overrides = dictionary

    plot.line('x','y',source=source,line_width=3,line_alpha=0.6)


    stock = TextInput(title='Stock',value='GOOGL')
    date = TextInput(title='Month/Year of Interest',value='04/2020')

    def update_stock(attrname,old,new):
        plot.title.text = stock.value + ' Closing Price'
        try:
            global data
            data, meta_data = ts.get_daily(symbol=stock.value,outputsize='full')
            value = []
            dates = []
            st = date.value
            dateval = st.split('/')[1] + '-' + st.split('/')[0] + '-'
            for j in range(4):
                for i in range(10):
                    if j*10 + i < 32:
                        try:
                            value.append(data.loc[dateval+'%d%d 00:00:00'%(j,i)].values)
                            dates.append(st.split('/')[0]+'/%d%d'%(j,i))
                        except:
                            pass
            value = np.array(value)
            N = len(value.T[1])
            x = np.arange(N)
            openval = value.T[0]
            closeval = value.T[2]
            source.data =dict(x=x,y=closeval)
        except:
            plot.title.text = "Not Found"


    def update_date(attrname,old,new):
        try:
            value = []
            dates = []
            st = date.value
            dateval = st.split('/')[1] + '-' + st.split('/')[0] + '-'
            for j in range(4):
                for i in range(10):
                    if j*10 + i < 32:
                        try:
                            value.append(data.loc[dateval+'%d%d 00:00:00'%(j,i)].values)
                            dates.append(st.split('/')[0]+'/%d%d'%(j,i))
                            except:
                                pass
            value = np.array(value)
            N = len(value.T[1])
            x = np.arange(N)
            openval = value.T[1]
            closeval = value.T[1]
            source.data =dict(x=x,y=openval)
            plot.xaxis.ticker = [i*2 for i in range(N//2)]
            dictionary = {int(i):j for i,j in zip(np.arange(N),dates)}
            plot.xaxis.major_label_overrides = dictionary
        except:
            pass


    stock.on_change('value',update_stock)
    date.on_change('value',update_date)



    layout = row(widgetbox(stock,date),plot)

    def modify_doc(doc):
        doc.add_root(row(layout,width=800))
        #doc.title = 'sliders'
        stock.on_change('value',update_stock)
        date.on_change('value',update_date)

    handler = FunctionHandler(modify_doc)
    appe = Application(handler)
    output_file("index.html")
    script,div = embed.components(appe)
    return render_template('bokeh.html',script=script,div=div)

@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run(port=33507)
