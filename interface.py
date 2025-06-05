from flask import Flask,  render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('html/home.html')

@app.route("/conjuntos/")
def conjuntos():
    return render_template('html/conjuntos.html')

@app.route("/conjuntos/detalhes")
def detalhes():
    return render_template('html/detalhes.html', conjuntos=[["Contagem 1", "valor1", "valor2"], ["Contagem 2", "valor1", "valor2"]])

if __name__ == "__main__":
    app.run()