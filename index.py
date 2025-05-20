from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_cors import CORS
import asyncio
from playwright.async_api import async_playwright
import json

app = Flask(__name__)
CORS(app)

def get_proxy():
    return {}

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
    return render_template('view.html', ids=ids)

@app.route('/matriculas')
def matriculas():
    return render_template('matriculas.html')
# Función asincrónica usando Playwright
async def perform_lookup(badge):
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        url_cookies = "https://auto-info.gratis/es/"
        await page.goto(url_cookies)

        url1 = "https://auto-info.gratis/es/sprawdzam/"
        url2 = "https://auto-info.gratis/es/test/"
        post_data = f"numer={badge}&kraj=ES"

        headers = {
            'Host': 'auto-info.gratis',
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://auto-info.gratis',
            'Referer': 'https://auto-info.gratis/es/sprawdzam/',
            'Upgrade-Insecure-Requests': '1'
        }

        js_headers = json.dumps(headers)
        js_script1 = f"fetch('{url1}', {{method: 'POST', headers: {js_headers}, body: '{post_data}'}});"
        js_script2 = f"fetch('{url2}', {{method: 'POST', headers: {js_headers}, body: '{post_data}'}});"

        await page.evaluate(js_script1)
        await asyncio.sleep(1)
        await page.evaluate(js_script2)

        await asyncio.sleep(5)
        result_url = page.url  # Esta es la URL final que se va a devolver
        await browser.close()
        return result_url

@app.route("/searchbadge", methods=["POST"])
def searchbadge():
    badge = request.form.get("badge")
    if not badge:
        return jsonify({"error": "Introduce una matrícula"}), 400
    try:
        url_resultado = asyncio.run(perform_lookup(badge))
        return jsonify({"resultado": url_resultado}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
