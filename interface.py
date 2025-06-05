from flask import Flask,  render_template, request, redirect, jsonify

app = Flask(__name__)

conjuntos_teste = [["Contagem 1", "valor1", "valor2"], ["Contagem 2", "valor1", "valor2"]]

@app.route("/")
def home():
    return render_template('html/home.html')

@app.route("/registra_conjunto", methods=['POST'])
def registra_conjunto():
    data = request.get_json()
    novo_conjunto = data.get("titulo")
    if novo_conjunto:
        conjuntos_teste.append([novo_conjunto])
        print(conjuntos_teste)
        return jsonify({"status": "ok", "mensagem": "Conjunto registrado"}) ,200
    else:
        return jsonify({"status": "erro", "mensagem": "Título ausente"}), 400



# @app.route("/conjuntos/")
# def conjuntos():
#     return render_template('html/conjuntos.html')

# @app.route("/conjuntos/detalhes")
# def detalhes():
#     print(f"conjuntos {conjuntos_teste}")
#     return render_template('html/detalhes.html', conjuntos=conjuntos_teste)

# @app.route("/registra", methods = ['POST'])
# def registra():
#     if request.method == 'POST':
#         nova_contagem  = request.form.get('titulo')
#         conjuntos_teste.append([nova_contagem,'aa','bb'])
#         print("salvou")
#         return redirect("/conjuntos/detalhes")

if __name__ == "__main__":
    app.run()