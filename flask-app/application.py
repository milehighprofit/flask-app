from flask import Flask, render_template
from tickers import alle
from tickers1 import htf
from tickers2 import ltf
import datetime as dt
import requests
import pandas as pd
import numpy as np
import matplotlib
application = Flask(__name__)

@application.route('/')
def home():
    cols1 = (htf.iloc[-3:] != 0).any()
    websitedata1 = htf.iloc[-3:][cols1[cols1].index]
    return render_template("home.html", tables1 = [websitedata1.to_html(classes='data')])

@application.route('/1hour/')
def about():
    cols = (alle.iloc[-3:] != 0).any()
    websitedata = alle.iloc[-3:][cols[cols].index]
    return render_template("about.html", tables = [websitedata.to_html(classes='data')])

@application.route('/5min/')
def lowtimeframe():
    cols2 = (ltf.iloc[-3:] != 0).any()
    websitedata2 = ltf.iloc[-3:][cols2[cols2].index]
    return render_template("lowtimeframe.html", tables2 = [websitedata2.to_html(classes='data')])

if __name__ == '__main__':
    application.run()