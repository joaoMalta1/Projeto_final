from flask import Flask,  render_template, request, jsonify
import json
import os
import serial 
import time

app = Flask(__name__)
conjuntos_teste = []
porta = "COM26"

@app.route("/")
def home():
    conjuntos = []
    path_json = os.path.join("db", "conjuntos.json")
    if os.path.exists(path_json):
        try:
            with open(path_json, "r", encoding="utf-8") as f:
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
    path_json = os.path.join("db", "conjuntos.json")
    if os.path.exists(path_json):
        try:
            with open(path_json, "r", encoding="utf-8") as f:
                conjuntos = json.load(f)
        except Exception as e:
            print(f"Erro ao ler o JSON: {e}")
            conjuntos = []
    else:
        conjuntos = []
    if any(conjunto.get("titulo") == novo_conjunto for conjunto in conjuntos):
        return jsonify({"status": "erro", "mensagem": "Conjunto já existe"}), 409
    conjuntos.append({ "titulo": novo_conjunto, "historico": [] })
    try:
        with open(path_json, "w", encoding="utf-8") as f:
            json.dump(conjuntos, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao escrever o JSON: {e}")
        return jsonify({"status": "erro", "mensagem": "Erro ao salvar conjunto"}), 500
    return jsonify({"status": "ok", "mensagem": "Conjunto registrado"}), 200



@app.route("/conjuntos/<string:titulo_conjunto>")
def contadores(titulo_conjunto):
    path_json = os.path.join("db", "conjuntos.json")
    if not os.path.exists(path_json):
        return "Nenhum conjunto encontrado", 404
    try:
        with open(path_json, "r", encoding="utf-8") as f:
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
    path_json = os.path.join("db", "conjuntos.json")
    try:
        with open(path_json, "r", encoding="utf-8") as f:
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
                "quantidade": 0,
            })
            break
    else:
        return jsonify({"status": "erro", "mensagem": "Conjunto não encontrado"}), 404

    try:
        with open(path_json, "w", encoding="utf-8") as f:
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

@app.route("/envia_arduino/<string:titulo_conjunto>", methods=["POST"])
def envia_arduino(titulo_conjunto):
    path_json = os.path.join("db", "conjuntos.json")
    if os.path.exists(path_json):
        with open(path_json, "r", encoding="utf-8") as f:
            dados_json = json.load(f)

        for conjunto in dados_json:
            if conjunto.get("titulo") == titulo_conjunto:
                titulo = conjunto["titulo"]
                contagens = conjunto["contagens"]
                partes = [titulo, str(len(contagens))]
                for contagem in contagens:
                    partes.append(contagem["nome"])
                    partes.append(str(contagem["passo"]))
                    partes.append(contagem["unidade"])
                    partes.append(str(contagem["quantidade"]))
                
                linha_serial = ",".join(partes) + "\n"
                data = ('configurar ' + linha_serial).strip()

                print(f">>> Enviando: {data}")

                try:
                    porta_serial = serial.Serial(porta, baudrate=9600, timeout=2)
                    time.sleep(5)  # Aguarda o Arduino reiniciar

                    porta_serial.write(data.encode("utf-8"))
                    
                    resposta = ""
                    tempo_inicio = time.time()
                    while time.time() - tempo_inicio < 2:
                        if porta_serial.in_waiting > 0:
                            resposta = porta_serial.readline().decode("utf-8").strip()
                            break
                        time.sleep(0.1)

                    porta_serial.close()

                    print(f"<<< Resposta: {resposta}")

                    if resposta and titulo in resposta:
                        return jsonify({"status": "ok", "mensagem": f"Arduino respondeu: {resposta}"})
                    else:
                        return jsonify({"status": "erro", "mensagem": f"Arduino respondeu algo inesperado: {resposta}"}), 500

                except Exception as e:
                    print(e)
                    return jsonify({"status": "erro", "mensagem": f"Erro na comunicação: {str(e)}"}), 500

    return jsonify({"status": "erro", "mensagem": "Conjunto não encontrado"}), 404


@app.route("/recebe_arduino", methods=["POST"])
def recebe_arduino():
    porta_serial = serial.Serial(porta, baudrate=9600, timeout=2)
    time.sleep(5)  # Aguarda o Arduino reiniciar
    data = 'enviar'
    porta_serial.write(data.encode("utf-8"))

    resposta = ""
    tempo_inicio = time.time()
    while time.time() - tempo_inicio < 5:
        if porta_serial.in_waiting > 0:
            resposta = porta_serial.readline().decode("utf-8").strip()
            break
        time.sleep(0.1)
    porta_serial.close()
    print(f"<<< Resposta: {resposta}")
    print(resposta)

    path_json = os.path.join("db", "conjuntos.json")
    if not os.path.exists(path_json):
        return jsonify({"erro": "Arquivo JSON não encontrado."}), 500

    recebido = trata_resposta(resposta)[0]
    print(f"json gerado{recebido}")


    with open(path_json, "r", encoding="utf-8") as f:
        dados_json = json.load(f)

    atualizou = False
    for conjunto in dados_json:
        if conjunto["titulo"].strip() == recebido["titulo"]:
            conjunto["historico"] = recebido["historico"]
            for nova in recebido["contagens"]:
                for contagem in conjunto["contagens"]:
                    if contagem["nome"].strip() == nova["nome"]:
                        contagem["quantidade"] = nova["quantidade"]
                        contagem["passo"] = nova["passo"]
                        contagem["unidade"] = nova["unidade"]
            atualizou = True

    if atualizou:
        with open(path_json, "w", encoding="utf-8") as f:
            json.dump(dados_json, f, indent=2, ensure_ascii=False)
        return jsonify({"status": "ok", "mensagem": "JSON atualizado com sucesso."})
    else:
        return jsonify({"status": "vazio", "mensagem": "Nenhum conjunto encontrado."})



def trata_resposta(resposta):
    linha = resposta.strip()
    partes = [p.strip() for p in linha.split(",")]
    historico = []
    if "historico" in partes:
        idx = partes.index("historico")
        partes_dados = partes[:idx]
        for i in partes[idx + 1 : ]:
            if(i == '5'):
                historico.append(-1)
            elif (i == '6'):
                historico.append(-2)
            elif (i == '7'):
                historico.append(-3)
            elif (i == '8'):
                historico.append(-4)
            else:
                historico.append(int(i))
        
    else:
        partes_dados = partes
        historico = []

    recebidos = []
    i = 0
    while i < len(partes_dados):
        if i + 1 >= len(partes_dados):
            break

        titulo = partes_dados[i]
        try:
            num_contagens = int(partes_dados[i + 1])
        except ValueError:
            break
        i += 2

        contagens = []
        for _ in range(num_contagens):
            if i + 3 >= len(partes_dados):
                break
            nome = partes_dados[i]
            try:
                passo = int(partes_dados[i + 1].strip())
                unidade = partes_dados[i + 2].strip()
                quantidade = int(partes_dados[i + 3].strip())
            except ValueError:
                break
            contagens.append({
                "nome": nome.strip(),
                "passo": passo,
                "unidade": unidade,
                "quantidade": quantidade
            })
            i += 4

        recebidos.append({
            "titulo": titulo.strip(),
            "contagens": contagens,
            "historico": historico
        })
        print(recebidos)

    return recebidos


if __name__ == "__main__":
    app.run(use_reloader=False)