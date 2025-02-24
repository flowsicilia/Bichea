from flask import Flask, render_template, redirect, url_for, request, jsonify
import sqlite3
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/camaras')
def camaras():
    return render_template('camaras.html')

@app.route('/view/<ids>')
def cam_viewer(ids):
    #split_ids = ids.split(".")
    return render_template('view.html', ids=ids)

@app.route('/matriculas')
def matriculas():
    return render_template('matriculas.html')

@app.route("/scrapear", methods=["POST"])
def scrapear():
    payload = {
        'numer':'1414GZT',
        'kraj':'ES',
        'g-recaptcha-response':'1'} 

    if request.method == "POST":
        url = "https://auto-info.gratis/es/sprawdzam/"

if __name__ == '__main__':
    app.run(debug=True)
