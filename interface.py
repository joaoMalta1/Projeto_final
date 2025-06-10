from flask import Flask,  render_template, request, redirect, jsonify

app = Flask(__name__)

conjuntos_teste = []

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



@app.route("/conjuntos/<string:titulo_conjunto>")
def contadores(titulo_conjunto):
    for i in conjuntos_teste:
        if(i[0] == titulo_conjunto):
            print(f"achou o conjunto {i[0]}")
            return render_template('html/conjuntos.html', contadores_conjunto = i[1:])


# @app.route("/conjuntos/detalhes")
# def detalhes():
#     print(f"conjuntos {conjuntos_teste}")
#     return render_template('html/detalhes.html', conjuntos=conjuntos_teste)


if __name__ == "__main__":
    app.run()