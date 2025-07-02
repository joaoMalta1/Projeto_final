import os, json

def receber_dados_arduino_e_atualizar_json():
    linha = 'ingresos, 2, setor a, 3, unidade, 0, setor b , 10, unidade, 0, novo, 1, teste1, 3, cm, 7'
    partes = [p.strip() for p in linha.split(",")] #cria lista separada por , e dps tira os caracteres vazios dos elementos da lista
    conjuntos_recebidos = []
    print(f"partes {partes} len {len(partes)}")
    i = 0
    x= 0
    while i < len(partes):    
        if i + 1 >= len(partes):
            print("Dados incompletos para um conjunto.") #verifica se tem informações de pelo menos 1 conjunto
            break
        titulo = partes[i]
        num_contagens = int(partes[i+1])
        i += 2 #pega o nome da contagem 

        contagens = []
        for _ in range(num_contagens):
            if i + 3 >= len(partes): #verifica se possui passo, unidade e qtd
                print("Dados incompletos para contagem.")
                break
            nome = partes[i] 
            passo = int(partes[i+1]) 
            unidade = partes[i+2]
            quantidade = int(partes[i+3])
            contagens.append({
                "nome": nome.strip(),
                "passo": passo,
                "unidade": unidade,
                "quantidade": quantidade
            })
            i += 4

        conjuntos_recebidos.append({
            "titulo": titulo.strip(),
            "contagens": contagens
        })

    caminho_json = os.path.join("db", "conjuntos.json")
    if not os.path.exists(caminho_json):
        print("Arquivo JSON não encontrado.")
        return

    with open(caminho_json, "r", encoding="utf-8") as f:
        dados_json = json.load(f)

    atualizou_algo = False
    for recebido in conjuntos_recebidos:
        for conjunto in dados_json:
            if conjunto["titulo"].strip() == recebido["titulo"]:
                for nova in recebido["contagens"]:
                    for contagem in conjunto["contagens"]:
                        if contagem["nome"].strip() == nova["nome"]:
                            contagem["quantidade"] = nova["quantidade"]
                            contagem["passo"] = nova["passo"]
                            contagem["unidade"] = nova["unidade"]
                atualizou_algo = True

    if atualizou_algo:
        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(dados_json, f, indent=2, ensure_ascii=False)
        print("JSON atualizado com sucesso.")
    else:
        print("Nenhum conjunto encontrado.")

receber_dados_arduino_e_atualizar_json()
