from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_cors import CORS
import requests
import urllib3


app = Flask(__name__)
CORS(app)

# Disable SSL certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Custom headers to scraping
headers = {
    'Host': 'auto-info.gratis',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://auto-info.gratis',
    'Referer': 'https://auto-info.gratis/es/sprawdzam/',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',}
# Get proxy to scraping
def get_proxy():
    params = {
        'request': 'getproxies',
        'protocol': 'http',
        'timeout' : '1500',
        'country': 'all',
        'ssl': 'all',
        'anonymity': 'all',}
    response = requests.get('https://api.proxyscrape.com/v2/', params=params)
    proxies = response.text.split('\n')
    return {"http":"http://" + proxies[0]} if proxies else {}

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

@app.route("/searchbadge", methods=["POST"])
def searchbadge():
    badge = request.form.get("badge")
    if not badge:
        return jsonify({"error": "Introduce una matrícula"}), 400

    proxies = get_proxy()
    
    # Get cookies
    url_cookies = "https://auto-info.gratis/es/"
    response_cookies = requests.get(url_cookies, headers=headers, proxies=proxies, verify=False)
    cookies = response_cookies.cookies

    # First POST
    url = "https://auto-info.gratis/es/sprawdzam/"
    post_data = f"numer={badge}&kraj=ES&g-recaptcha-response=1"
    response = requests.post(url, cookies=cookies, headers=headers, data=post_data, proxies=proxies, verify=False)

    if response.status_code == 200:
        # Second POST
        url2 = "https://auto-info.gratis/es/test/"
        response2 = requests.post(url2, cookies=cookies, headers=headers, data=post_data, proxies=proxies, verify=False)
        report = 'https://auto-info.gratis' + response2.text
        return jsonify({"resultado": report})

    return jsonify({"error": f"Error en la petición: {response.status_code}", "detalle": response.text}), 500

if __name__ == '__main__':
    app.run(debug=True)
