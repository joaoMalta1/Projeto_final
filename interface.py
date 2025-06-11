from flask import Flask,  render_template, request, jsonify

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
        contagens = []
        conjuntos_teste.append([novo_conjunto, contagens])
        print(conjuntos_teste)
        return jsonify({"status": "ok", "mensagem": "vonjunto registrado"}) ,200
    else:
        return jsonify({"status": "erro", "mensagem": "titulo ausente"}), 400



@app.route("/conjuntos/<string:titulo_conjunto>")
def contadores(titulo_conjunto):
    for i in conjuntos_teste:
        if(i[0] == titulo_conjunto):
            print(f"achou o conjunto {i[0]}")
            return render_template('html/conjuntos.html', contadores_conjunto = i[1:])


@app.route("/adiciona_contagem/<string:titulo_conjunto>", methods=['POST'])
def adiciona_contagem(titulo_conjunto):
    for i in conjuntos_teste:
        if i[0] == titulo_conjunto:
            i[1].append(0)  # Adiciona uma nova contagem (ou contador)
            print(f"Conjunto {i[0]} contadores {i[1]}")
            return jsonify({"status": "ok"}), 200
    return jsonify({"status": "erro", "mensagem": "conjunto não encontrado"}), 404


@app.errorhandler(404)
def page_not_found(e):
    return render_template('html/erro.html', erro=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('html/erro.html', erro=500), 500


# @app.route("/conjuntos/detalhes")
# def detalhes():
#     print(f"conjuntos {conjuntos_teste}")
#     return render_template('html/detalhes.html', conjuntos=conjuntos_teste)

if __name__ == "__main__":
    app.run()