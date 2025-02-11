from flask import Flask, render_template, redirect, url_for, request, jsonify
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    data = request.get_json()
    matricula = data.get("matricula")

    if not matricula:
        return jsonify({"error": "Matrícula no proporcionada"}), 400

    try:
        # Configuración de Selenium (modo sin interfaz gráfica)
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Acceder a la web
        driver.get("https://auto-info.gratis/es/")  

        # Esperar hasta 15 segundos para encontrar el campo de matrícula
        input_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='matriculaInput']")))  # Cambia si el selector es otro
        
        input_box.send_keys(matricula)
        input_box.send_keys(Keys.RETURN)

        time.sleep(3)  # Esperar a que los datos se carguen

        # Extraer datos
        html = driver.page_source
        driver.quit()

        return jsonify({"matricula": matricula, "html": html})  # Devuelve el HTML de la página

    except Exception as e:
        import traceback
        error_message = traceback.format_exc()  # Captura el error completo
        print("🔥 ERROR DETALLADO:", error_message)  # Lo imprime en la terminal
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
