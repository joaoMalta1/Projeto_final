import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import json
import threading
import time
import os
#telegram
import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#criapdf
from fpdf import FPDF
#email
import smtplib
from email.message import EmailMessage
import mimetypes
from datetime import datetime


# ==== Carregar o JSON ====
with open('db/conjuntos.json', 'r', encoding='utf-8') as file:
    dados = json.load(file)

# ==== Função que monta os dados a partir do registro escolhido ====
def processar_registro(registro):
    contadores = [c["nome"] for c in registro["contagens"]]
    valores = [c["quantidade"] for c in registro["contagens"]]
    passos = [c["passo"] for c in registro["contagens"]]
    historico = registro["historico"]

    evolucao = [[] for _ in contadores]
    acumulado = [0] * len(contadores)

    for evento in historico:
        for i in range(len(contadores)):
            if evento == i + 1:
                acumulado[i] += 1*passos[i]  # Incremento
            elif evento == -(i + 1):
                acumulado[i] -= 1*passos[i]  # Decremento
            evolucao[i].append(acumulado[i])  # <<< Agora dentro do loop!



    dias = list(range(1, len(historico) + 1))
    return contadores, valores, evolucao, dias

# ==== Tkinter Interface ====
root = tk.Tk()
root.title("Gráficos por Conjunto")
root.geometry("900x700")

# ==== Combobox para escolher o conjunto (registro) ====
tk.Label(root, text="Selecione o Conjunto:").pack(pady=5)
titulos = [registro["titulo"] for registro in dados]
selected_conjunto = tk.StringVar(value=titulos[0])
combo_conjuntos = ttk.Combobox(root, textvariable=selected_conjunto, values=titulos, state="readonly")
combo_conjuntos.pack()

# ==== Combobox para escolher o tipo de gráfico ====
tk.Label(root, text="Selecione o tipo de gráfico:").pack(pady=5)
tipos_grafico = ["Linha", "Barra", "Pizza"]
selected_grafico = tk.StringVar(value=tipos_grafico[0])
combo_grafico = ttk.Combobox(root, textvariable=selected_grafico, values=tipos_grafico, state="readonly")
combo_grafico.pack()

frame_grafico = tk.Frame(root)
frame_grafico.pack(fill="both", expand=True, padx=10, pady=10)

def atualizar_grafico():
    # Qual registro foi escolhido?
    titulo = selected_conjunto.get()
    registro = next(r for r in dados if r["titulo"] == titulo)

    contadores, valores, evolucao, dias = processar_registro(registro)
    print(evolucao)
    modo = selected_grafico.get()

    fig, ax = plt.subplots(figsize=(6, 4))

    if modo == "Linha":
        for i, nome in enumerate(contadores):
            ax.step(dias, evolucao[i], label=nome)
        ax.set_title(f"Evolução - {titulo} (Linha)")
        ax.set_xlabel("Evento")
        ax.set_ylabel("Total Contado")
        ax.legend()
        ax.grid(True)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    elif modo == "Barra":
        ax.bar(contadores, valores, color=['blue', 'orange', 'green', 'red', 'purple'][:len(contadores)])
        ax.set_title(f"Total por Contador - {titulo} (Barra)")
        ax.set_ylabel("Total Contado")
        ax.grid(True)

    elif modo == "Pizza":
        ax.pie(valores, labels=[f"{contadores[i]}: {valores[i]}" for i in range(len(contadores))], autopct='%1.1f%%')
        ax.set_title(f"Distribuição - {titulo} (Pizza)")

    # Limpar gráfico anterior
    for widget in frame_grafico.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

    # Variável para armazenar o texto
    email_salvo = ""
    dataframes = {}
# =========== Função para salvar o email ===============

def salvar_email():
    global email_salvo
    email_salvo = entrada.get()
    print("Email:", email_salvo)

    try:
        # Obtém o nome do conjunto selecionado na Combobox
        conjunto_escolhido = combo_conjuntos.get()

        if not conjunto_escolhido:
            print("❌ Nenhum conjunto selecionado.")
            return

        nome_pdf = f"{conjunto_escolhido}_relatorio.pdf"
        assunto = f"Relatório de Contagem - {conjunto_escolhido}"
        corpo = f"Segue em anexo o relatório atualizado para o conjunto: {conjunto_escolhido}"

        enviar_email_com_pdf(email_salvo, assunto, corpo, nome_pdf)
        salva_ultimo_email(email_salvo)

    except Exception as e:
        print("Erro ao tentar enviar o e-mail:", e)


#Função que salva o ultimo email usado em um arquivo

ARQUIVO_EMAIL = "ultimo_email.txt"

def salva_ultimo_email(email):
    with open(ARQUIVO_EMAIL, "w") as f:
        f.write(email)
#Função que carrega o ultimo email
def carregar_ultimo_email():
    if os.path.exists(ARQUIVO_EMAIL):
        with open(ARQUIVO_EMAIL, "r") as f:
            return f.read().strip()
    return ""

# Função que verifica se o email é valido e envia ele, caso for
def enviar_email():
    email = entrada.get()
    if email:
        print(f"Enviando e-mail para: {email}")
        salvar_email()
    else:
        print("Digite um e-mail válido.")
#===============================
# funcoes do eduardo
#===============================

# =========================
# Função que manda mensagem no Telegram
# =========================
def enviar_mensagem_telegram(dataframe, conjunto_contagem):
    try:
        import requests

        endereco_base = "https://api.telegram.org/bot8141606427:AAHgYPpVbfJJuungH6koswgqBHFSnA97q7w"
        endereco_envio = endereco_base + "/sendMessage"

        # Colunas que você quer mostrar (na ordem correta)
        colunas = ["nome", "passo", "unidade", "quantidade"]

        # Calcula a largura de cada coluna com base no maior valor
        larguras = {}
        for col in colunas:
            max_valor = max([len(str(v)) for v in dataframe[col]] + [len(col)])
            larguras[col] = max_valor + 2  # margem extra

        # Início da mensagem
        mensagem_texto = f"<b>Atualização de {conjunto_contagem.capitalize()}</b>\n<pre>"

        # Cabeçalho
        cabecalho = ""
        for col in colunas:
            cabecalho += str(col.capitalize()).ljust(larguras[col]) + "|"
        mensagem_texto += cabecalho.rstrip("|") + "\n"

        # Separador
        mensagem_texto += "-" * len(cabecalho) + "\n"

        # Linhas da tabela
        for _, row in dataframe.iterrows():
            linha = ""
            for col in colunas:
                valor = str(row[col])
                linha += valor.ljust(larguras[col]) + "|"
            mensagem_texto += linha.rstrip("|") + "\n"

        mensagem_texto += "</pre>"
        print(mensagem_texto)

        # Envia para o Telegram
        mensagem = {
            "chat_id": "7616089098",
            "text": mensagem_texto,
            "parse_mode": "HTML"
        }

        resposta = requests.post(endereco_envio, json=mensagem)
        print("Mensagem enviada ao Telegram com sucesso!!")

    except Exception as e:
        print(f"Erro no envio de mensagem Telegram: {e}")

def enviar_mensagem_do_conjunto_telegram():
    try:
        conjunto_escolhido = combo_conjuntos.get()
        if not conjunto_escolhido:
            print("❌ Nenhum conjunto selecionado.")
            return

        df = dataframes.get(conjunto_escolhido)
        if df is None:
            print(f"❌ Conjunto '{conjunto_escolhido}' não encontrado nos dataframes.")
            return

        enviar_mensagem_telegram(df, conjunto_escolhido)

    except Exception as e:
        print(f"Erro ao tentar enviar mensagem do Telegram: {e}")


#==========================
# funcao pra criar planilha xlsx
#==========================
def cria_excel(df_atual, nome_arquivo):
    # Atualizando informações de contagem na planilha
    if os.path.exists(nome_arquivo):
        df_existente = pd.read_excel(nome_arquivo)
        df_final = pd.concat([df_existente, df_atual], ignore_index=True)
    else:
        df_final = df_atual

    df_final.to_excel(nome_arquivo, index=False)
    print(f"Planilha Excel '{nome_arquivo}' atualizada !!!")

    return df_final

'''
# =========================
# Função para atualizar Google Sheets
# =========================
def atualizar_google_sheets(nome_planilha, dataframe):
    try:
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name('Credentials.json', scope)
        client = gspread.authorize(credentials)

        try:
            sheet = client.open_by_key("1lnHGk6e7HftHsJL1Sd5SMdm4vig9xIlBBKbi-_s95LU").sheet1
        except gspread.exceptions.SpreadsheetNotFound:
            print("❌ Planilha não encontrada. Compartilhou com a conta de serviço?")
            return

        sheet.clear()

        # 🔁 Remove duplicatas pela primeira coluna (mantém a última)
        dataframe = dataframe.drop_duplicates(subset=dataframe.columns[0], keep='last')

        # Converte o DataFrame em lista de listas com cabeçalho
        dataframe = dataframe.astype(str)
        dados = [dataframe.columns.values.tolist()] + dataframe.values.tolist()

        sheet.update(range_name='A1', values=dados)
        print(f"✅ Google Sheets '{nome_planilha}' atualizado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao atualizar Google Sheets: {e}")

'''

def atualizar_google_sheets_abas(planilha_id, dataframes):
    try:
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name('Credentials.json', scope)
        client = gspread.authorize(credentials)

        spreadsheet = client.open_by_key(planilha_id)

        for titulo, df in dataframes.items():
            print(f"🔁 Atualizando aba '{titulo}'...")

            df = df.fillna("").astype(str)
            df['Atualizado em'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                worksheet = spreadsheet.worksheet(titulo)
                dados_existentes = worksheet.get_all_values()
                if not dados_existentes:
                    # Se a aba existe mas está vazia
                    worksheet.update("A1", [df.columns.tolist()] + df.values.tolist())
                else:
                    # Verifica se os cabeçalhos batem
                    cabecalho_existente = dados_existentes[0]
                    colunas_df = df.columns.tolist()
                    
                    if cabecalho_existente != colunas_df:
                        print(f"⚠️ Cabeçalhos diferentes na aba '{titulo}'. Abortando atualização.")
                        continue
                    
                    worksheet.append_rows(df.values.tolist())

            except gspread.exceptions.WorksheetNotFound:
                # Cria nova aba com os dados completos
                from re import sub
                titulo_sanitizado = sub(r'[^\w\s\-]', '', titulo)[:100]  # tira símbolos especiais e limita a 100 chars
                try:
                    worksheet = spreadsheet.add_worksheet(title=titulo_sanitizado, rows="100", cols="20")
                    dados = [df.columns.tolist()] + df.values.tolist()
                    worksheet.update("A1", dados)
                    print(f"✅ Nova aba '{titulo_sanitizado}' criada com sucesso.")
                except Exception as e:
                    print(f"❌ Erro ao criar aba '{titulo_sanitizado}': {e}")

        print("✅ Todas as abas atualizadas com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao atualizar abas no Google Sheets: {e}")


# =========================
# Função que gera o PDF antes de mandar para email
# =========================
def gerar_relatorio_pdf(nome_arquivo_pdf, dataframe, titulo_relatorio):
    try:
        dataframe = dataframe.fillna("").astype(str)
        dataframe['Atualizado em'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        colunas = dataframe.columns.tolist()

        if os.path.exists(nome_arquivo_pdf):
            with open(nome_arquivo_pdf.replace(".pdf", ".csv"), "a", encoding="utf-8") as f:
                for _, row in dataframe.iterrows():
                    f.write(";".join(row.astype(str)) + "\n")
        else:
            with open(nome_arquivo_pdf.replace(".pdf", ".csv"), "w", encoding="utf-8") as f:
                f.write(";".join(colunas) + "\n")
                for _, row in dataframe.iterrows():
                    f.write(";".join(row.astype(str)) + "\n")

        df_completo = pd.read_csv(nome_arquivo_pdf.replace(".pdf", ".csv"), sep=";")

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, titulo_relatorio, ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 12)
        for col in df_completo.columns:
            pdf.cell(50, 10, str(col), border=1)
        pdf.ln()

        pdf.set_font("Arial", '', 12)
        for _, row in df_completo.iterrows():
            for item in row:
                pdf.cell(50, 10, str(item), border=1)
            pdf.ln()

        pdf.output(nome_arquivo_pdf)
        print(f"Relatório '{nome_arquivo_pdf}' gerado com sucesso")

    except Exception as e:
        print(f"Erro ao gerar relatório PDF: {e}")

# =========================
# Função manda email com PDF gerado
# =========================
def enviar_email_com_pdf(destinatario, assunto, corpo_email, caminho_pdf):
    try:
        # Dados do seu e-mail (remetente)
        email_remetente = "efcneumayer@gmail.com"
        senha = "aama nnog iooc lawt"  # Atenção! Não é sua senha normal. É uma senha de app.

        # Monta o e-mail
        msg = EmailMessage()
        msg['Subject'] = assunto
        msg['From'] = email_remetente
        msg['To'] = destinatario
        msg.set_content(corpo_email)

        # Lê o arquivo PDF
        with open(caminho_pdf, 'rb') as arquivo:
            tipo, _ = mimetypes.guess_type(caminho_pdf)     # pegar o tipo do arquivo utilizado
            tipo_principal, sub_tipo = tipo.split('/')
            msg.add_attachment(arquivo.read(),              #attachment: mandar email com o corpo dos parametros
                               maintype=tipo_principal,
                               subtype=sub_tipo,
                               filename=os.path.basename(caminho_pdf))      

        # Conecta no servidor SMTP do Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:          #biblioteca smtp para mandar o email 
            smtp.login(email_remetente, senha)                         # senha do google security
            smtp.send_message(msg)

        print(f"E-mail enviado com sucesso para {destinatario}")

    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")




#=============================
# WHILE INTEGRADO COM OS DOIS PROGRAMAS
#=============================

caminho_json = "db/conjuntos.json"
ultima_modificacao = None

def monitorar_json():
    global ultima_modificacao, dataframes
    while True:
        try:
            nova_mod = os.path.getmtime(caminho_json)
            if nova_mod != ultima_modificacao:
                ultima_modificacao = nova_mod
                print("JSON atualizado! Atualizando gráfico...")

                # Recarrega o JSON atualizado
                with open(caminho_json, 'r', encoding='utf-8') as file:
                    global dados
                    dados = json.load(file)

                # Atualiza os títulos da combobox, caso tenham mudado
                novos_titulos = [registro["titulo"] for registro in dados]
                combo_conjuntos['values'] = novos_titulos

                # Mantém o título atual se ainda existir
                titulo_atual = selected_conjunto.get()
                if titulo_atual not in novos_titulos:
                    selected_conjunto.set(novos_titulos[0])

                root.after(0, atualizar_grafico)
                
                #=====================================
                #DADOS DO EDUARDO A PARTIR DAQUI
                #=====================================

                # Prepara os DataFrames
                dataframes = {}
                for conjunto in dados:
                    titulo = conjunto["titulo"]
                    contagens = conjunto["contagens"]
                    df = pd.DataFrame(contagens)
                    dataframes[titulo] = df

                # 1. Atualiza Google Sheets com abas separadas
                planilha_id = "1lnHGk6e7HftHsJL1Sd5SMdm4vig9xIlBBKbi-_s95LU"
                atualizar_google_sheets_abas(planilha_id, dataframes)

                for titulo, df in dataframes.items():
                    print(f"Atualizando dados para: {titulo}")
                    # 1. Atualiza planilha Excel local
                    nome_excel = f"{titulo}.xlsx"
                    df_final = cria_excel(df, nome_excel)

                    # 2. Atualiza Google Sheets
                    #atualizar_google_sheets(titulo, df_final)

                    # 3. Gera PDF do relatório
                    nome_pdf = f"{titulo}_relatorio.pdf"
                    gerar_relatorio_pdf(nome_pdf, df_final, f"Relatório de Contagem - {titulo}")

                    print(f"Pronto para enviar e-mail com relatório '{nome_pdf}' quando o botão for clicado.")
                # Envia a mensagem para o telegram
                enviar_mensagem_do_conjunto_telegram()


        except Exception as e:
            print(f"Erro ao verificar JSON: {e}")

        time.sleep(5)  # espera 5 segundo para não sobrecarregar



# ==== Atualiza ao mudar o conjunto ou o tipo de gráfico ====
combo_conjuntos.bind("<<ComboboxSelected>>", lambda e: atualizar_grafico())
combo_grafico.bind("<<ComboboxSelected>>", lambda e: atualizar_grafico())

# Cria label para a entrada do email
label_email = tk.Label(root, text="Digite seu e-mail aqui:")
label_email.pack(pady=(15, 0))

threading.Thread(target=monitorar_json, daemon=True).start()
entrada = tk.Entry(root, width=30)
entrada.pack(pady=10)


# Inserir último e-mail 
ultimo_email = carregar_ultimo_email()
if ultimo_email:
    entrada.insert(0, ultimo_email)
    entrada.config(fg="black")





# Botão para salvar o texto
botao_email = tk.Button(root, text="Enviar", command=enviar_email)
botao_email.pack(pady=10)





atualizar_grafico()
root.mainloop()
