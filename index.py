from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
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

if __name__ == '__main__':
    app.run(debug=True)
