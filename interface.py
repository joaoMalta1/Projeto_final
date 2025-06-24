from flask import Flask,  render_template, request, jsonify
import json
import os

app = Flask(__name__)

conjuntos_teste = []

@app.route("/")
def home():
    conjuntos = []
    caminho_json = os.path.join("db", "conjuntos.json")
    if os.path.exists(caminho_json):
        try:
            with open(caminho_json, "r", encoding="utf-8") as f:
                conjuntos = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar conjuntos: {e}")
    return render_template('html/home.html', conjuntos=conjuntos)

@app.route("/registra_conjunto", methods=['POST'])
def registra_conjunto():
    data = request.get_json()
    novo_conjunto = data.get("titulo")
    if not novo_conjunto:
        return jsonify({"status": "erro", "mensagem": "titulo ausente"}), 400
    caminho_json = os.path.join("db", "conjuntos.json")
    if os.path.exists(caminho_json):
        try:
            with open(caminho_json, "r", encoding="utf-8") as f:
                conjuntos = json.load(f)
        except Exception as e:
            print(f"Erro ao ler o JSON: {e}")
            conjuntos = []
    else:
        conjuntos = []
    if any(conjunto.get("titulo") == novo_conjunto for conjunto in conjuntos):
        return jsonify({"status": "erro", "mensagem": "Conjunto já existe"}), 409
    conjuntos.append({ "titulo": novo_conjunto })
    try:
        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(conjuntos, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao escrever o JSON: {e}")
        return jsonify({"status": "erro", "mensagem": "Erro ao salvar conjunto"}), 500
    return jsonify({"status": "ok", "mensagem": "Conjunto registrado"}), 200



@app.route("/conjuntos/<string:titulo_conjunto>")
def contadores(titulo_conjunto):
    caminho_json = os.path.join("db", "conjuntos.json")
    if not os.path.exists(caminho_json):
        return "Nenhum conjunto encontrado", 404
    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            conjuntos = json.load(f)
    except Exception as e:
        print(f"Erro ao ler o JSON: {e}")
        return "Erro ao carregar conjuntos", 500
    for conjunto in conjuntos:
        if conjunto.get("titulo") == titulo_conjunto:
            contagens = conjunto.get("contagens", [])
            return render_template('html/conjuntos.html', contadores_conjunto=contagens)
    return "Conjunto não encontrado", 404



@app.route("/adiciona_contagem/<string:titulo_conjunto>", methods=["POST"])
def adiciona_contagem(titulo_conjunto):
    data = request.get_json()
    nome = data.get("nome")
    passo = data.get("passo")
    unidade = data.get("unidade")
    if not nome or not passo or not unidade:
        return jsonify({"status": "erro", "mensagem": "Dados incompletos"}), 400
    caminho_json = os.path.join("db", "conjuntos.json")
    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            conjuntos = json.load(f)
    except:
        return jsonify({"status": "erro", "mensagem": "Erro ao ler o JSON"}), 500
    for conjunto in conjuntos:
        if conjunto.get("titulo") == titulo_conjunto:
            if "contagens" not in conjunto:
                conjunto["contagens"] = []
            conjunto["contagens"].append({
                "nome": nome,
                "passo": int(passo),
                "unidade": unidade,
                "quantidade": 0
            })
            break
    else:
        return jsonify({"status": "erro", "mensagem": "Conjunto não encontrado"}), 404

    try:
        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(conjuntos, f, indent=2, ensure_ascii=False)
    except:
        return jsonify({"status": "erro", "mensagem": "Erro ao salvar"}), 500

    return jsonify({"status": "ok", "mensagem": "Contagem adicionada"}), 200


@app.errorhandler(404)
def page_not_found(e):
    return render_template('html/erro.html', erro=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('html/erro.html', erro=500), 500

if __name__ == "__main__":
    app.run()