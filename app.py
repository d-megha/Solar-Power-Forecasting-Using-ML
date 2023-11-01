from flask import (Flask, url_for,
    render_template,
    redirect, request)
from forms import InputForm
import urllib.request, json
import os, pickle
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

model = pickle.load(open('model.pkl', 'rb'))

loc = {'Mumbai': [19.076090, 72.877426],
        'Delhi': [28.679079, 77.069710],
        'Kolkata': [22.572645, 88.363892],
        'Chennai': [13.067439, 80.237617]}

api_key = os.environ.get('API_KEY')

@app.route("/", methods=['GET', 'POST'])
def index():
    selectedValue = 0
    return render_template("index.html", c=0)

@app.route("/result", methods=['POST'])
def result():
    location = request.form['dropdown']
    lat = loc[str(location)][0]
    lon = loc[str(location)][1]
    
    # make external api request
    url = "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&units=metric&appid={}".format(lat, lon, api_key)
    
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)['list']

    temp = []
    speed = []
    date_txt = []
    Gt = np.loadtxt("Gt")

    for i in dict:
        temp = temp + [i['main']['temp']]
        speed = speed + [i['wind']['speed']]
        date_txt = date_txt + [i['dt_txt']]

    pred = pd.DataFrame([Gt, speed, temp]).T
    forecast = model.predict(pred)

    # Create the plotly graph for power
    fig = make_subplots()
    fig.add_trace(go.Scatter(x=date_txt, y=forecast, mode='lines', name='line'))
    fig.update_layout(
        title={
        'text': "Forecasted Power",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        yaxis_title='Power (Watts)'
    )

    # Create the plotly graph for temperature
    config = {'displayModeBar': False}
    fig1 = make_subplots()
    fig1.add_trace(go.Scatter(x=date_txt, y=temp, mode='lines', name='line'))
    fig1.update_layout(
        title={
        'text': "Forecasted Temperature",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        yaxis_title='Temperature (°C)'
    )

    # Create the plotly graph for wind speed
    fig2 = make_subplots()
    fig2.add_trace(go.Scatter(x=date_txt, y=speed, mode='lines', name='line'))
    fig2.update_layout(
        title={
        'text': "Forecasted Wind Speed",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        yaxis_title='Wind Speed (m/s)'
    )


    return render_template(
        "index.html", 
        plot=fig.to_html(full_html=False, config=config),
        plot1=fig1.to_html(full_html=False, config=config),
        plot2=fig2.to_html(full_html=False, config=config),
        c=1, 
        selectedValue=location)