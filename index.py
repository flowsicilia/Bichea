from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_cors import CORS
import asyncio
from playwright.async_api import async_playwright
import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user

app = Flask(__name__)
CORS(app)


app.config['SECRET_KEY'] = 'bicheatest1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bichea.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False  # Para sesiones no permanentes
app.config["SESSION_TIME_OUT"] = 3600 #En segundos


db = SQLAlchemy(app)
login_manager = LoginManager(app)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

login_manager = LoginManager(app)
login_manager.login_view = '/'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.')
    return render_template('login.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/camaras')
@login_required
def camaras():
    return render_template('camaras.html')

@app.route('/view/<ids>')
@login_required
def cam_viewer(ids):
    return render_template('view.html', ids=ids)

@app.route('/matriculas')
@login_required
def matriculas():
    return render_template('matriculas.html')
# Función asincrónica usando Playwright
async def handle_dialog(dialog):
    print(dialog.message)
    await dialog.dismiss()

async def perform_lookup(badge):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(    user_agent="Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36",
            viewport={"width": 412, "height": 915},  # Dimensiones de móvil
            is_mobile=True,
            device_scale_factor=2.625,
            has_touch=True)
        page = await context.new_page()

        url = "https://auto-info.gratis/es/"
        await page.goto(url)

        try:
            await page.get_by_placeholder('Matrícula').fill(badge)
            print('✅ MATRICULA seleccionada CORRECTAMENTE')
            button = page.get_by_role('button', name = 'Seleccione su país de registro')
            await button.click()
            await asyncio.sleep(2)
            await page.get_by_text('España', exact=True).click()
            print('✅ Pais seleccionado CORRECTAMENTE')
            await asyncio.sleep(2)
            button2 = page.get_by_role('button', name='Comprobar')
            await button2.click()
        except Exception as e:
            print(f'❌ERROR al seleccionar matricula o pais: {e}')

        try: 
            await page.wait_for_url("**/sprawdzam/**") # Esperar a que la pagina redirija a la URL
            await asyncio.sleep(2)
            await page.get_by_text('Consentir', exact=True).click()
            await asyncio.sleep(5)
            
             # Esperar a que el iframe del reCAPTCHA esté presente
            iframe_element = page.frame_locator("iframe[title='reCAPTCHA']")

            # Acceder al frame
            frame = await page.frame_locator("iframe[title='reCAPTCHA']").locator(".recaptcha-checkbox-border").click()

            if frame:
                # Hacer clic en el checkbox 
                await frame.click(".recaptcha-checkbox-border")
                print("✅ Checkbox del reCAPTCHA clickeado")
            else:
                print("❌ No se pudo acceder al iframe del reCAPTCHA")

            await asyncio.sleep(5)
            confirmCaptcha = page.get_by_role('button', name= 'Confirmar')
            await confirmCaptcha.click()
        except Exception as e:
            print(f'❌ERROR en la redirección: {e}')

        page.on("console", lambda msg: print(f"error: {msg.text}") if msg.type == "error" else None)

@app.route("/searchbadge", methods=["POST"])
@login_required
def searchbadge():
    badge = request.form.get("badge")
    if not badge:
        return jsonify({"error": "Introduce una matrícula"}), 400
    try:
        url_resultado = asyncio.run(perform_lookup(badge))
        return jsonify({"resultado": url_resultado}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True)
