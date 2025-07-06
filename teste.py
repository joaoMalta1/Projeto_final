
def trata_resposta(resposta):
    linha = resposta.strip()
    partes = [p.strip() for p in linha.split(",")]
    historico = []
    if "historico" in partes:
        idx = partes.index("historico")
        partes_dados = partes[:idx]
        for i in partes[idx + 1 : ]:
            print(f"i: {i}")
            i = i.strip()
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



print( trata_resposta("foi, 3, daniel, 1, cm, 73, bella, 5, m, 35, jjj, 3, m, 42, historico, 5, 8, 5, 7, 23, 1\n"))