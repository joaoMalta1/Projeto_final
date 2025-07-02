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


# ==== Carregar o JSON ====
with open('dados_contadores.json', 'r', encoding='utf-8') as file:
    dados = json.load(file)

# ==== Função que monta os dados a partir do registro escolhido ====
def processar_registro(registro):
    contadores = [c["nome"] for c in registro["contagens"]]
    valores = [c["quantidade"] for c in registro["contagens"]]
    historico = registro["historico"]

    evolucao = [[] for _ in contadores]
    acumulado = [0] * len(contadores)

    for evento in historico:
        for i in range(len(contadores)):
            if evento == i + 1:
                acumulado[i] += 1  # Incremento
            elif evento == -(i + 1):
                acumulado[i] -= 1  # Decremento
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
        ax.pie(valores, labels=[f"{contadores[i]}: {valores[i]}" for i in range(len(contadores))],
               autopct='%1.1f%%')
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
    global email_salvo, dataframes
    email_salvo = entrada.get()
    print("email:", email_salvo)
    try:
        for titulo in dataframes:
            nome_pdf = f"{titulo}_relatorio.pdf"
            assunto = f"Relatório de Contagem - {titulo}"
            corpo = f"Segue em anexo o relatório atualizado para o conjunto: {titulo}"
            enviar_email_com_pdf(email_salvo, assunto, corpo, nome_pdf)
    except Exception as e:
        print("Erro ao tentar enviar o(s) e-mail(s):", e)
#===============================
# funcoes do eduardo
#===============================

# =========================
# Função que manda mensagem no Telegram
# =========================
def enviar_mensagem_telegram(dataframe, conjunto_contagem):
    try:
        # Endereço da API do Telegram
        endereco_base = f"https://api.telegram.org/bot7929499599:AAFau1XWBd8hxDAQ2xlwGing-S4bpAjAD-8"
        endereco_envio = endereco_base + "/sendMessage"

        # Percorre as linhas do dataframe e monta mensagem para cada linha
        for _, row in dataframe.iterrows():
            mensagem_texto = f"Atualização de {conjunto_contagem.capitalize()}:\n"
            for coluna, valor in row.items():
                mensagem_texto += f" ->{coluna}: {valor}\n"

            # Monta o corpo da mensagem para enviar no Telegram
            mensagem = {"chat_id": "5240952608", "text": mensagem_texto}
            # Envia para a API do Telegram
            resposta = requests.post(endereco_envio, json=mensagem)
        print("Mensagem enviada ao Telegram com sucesso!!")

    except Exception as e:
        print(f"Erro no envio de mensagem Telegram: {e}")


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


# =========================
# Função para atualizar Google Sheets
# =========================
def atualizar_google_sheets(nome_planilha, dataframe):
    try:
        # permissoes que o programa terá
        scope = ["https://spreadsheets.google.com/feeds", 
                 "https://www.googleapis.com/auth/drive"]
        # carrega as credenciais com chave privada, email da conta de servico que atualiza as paginas e ID do projeto
        credentials = ServiceAccountCredentials.from_json_keyfile_name('servicos_integracao/credentials.json', scope)
        client = gspread.authorize(credentials)

        try:
            sheet = client.open(nome_planilha).sheet1
        except gspread.exceptions.SpreadsheetNotFound:
            sheet = client.create(nome_planilha).sheet1

        # Limpa a aba inteira do sheets antes de atualizar (pra nao sobreescrever os mesmos dados)
        sheet.clear()

        # Converte o dataframe em lista de listas, incluindo o cabeçalho
        dataframe = dataframe.astype(str)
        dados = [dataframe.columns.values.tolist()] + dataframe.values.tolist()
        # Atualiza os dados no Google Sheets
        sheet.update(range_name='A1', values=dados)
        print(f"Google Sheets '{nome_planilha}' atualizado com sucesso!!")

    except Exception as e:
        print(f"Erro ao atualizar Google Sheets: {e}")


# =========================
# Função que gera o PDF antes de mandar para email
# =========================
def gerar_relatorio_pdf(nome_arquivo_pdf, dataframe, titulo_relatorio):
    try:
        # Cria o PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)   # ativa a quebra automatica de linha
        pdf.add_page()

        # Título do relatório
        pdf.set_font("Arial", 'B', 16)      # parametros de fonte, estilo e tamanho
        pdf.cell(0, 10, titulo_relatorio, ln=True, align="C")   # parametros de largura, altura e texto
        pdf.ln(10)

        # Cabeçalho da tabela
        pdf.set_font("Arial", 'B', 12)
        for col in dataframe.columns:
            pdf.cell(50, 10, str(col), border=1)
        pdf.ln()

        # Dados da tabela
        pdf.set_font("Arial", '', 12)
        for _, row in dataframe.iterrows():
            for item in row:
                pdf.cell(50, 10, str(item), border=1)
            pdf.ln()

        # Salva o PDF
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
        email_remetente = email_salvo
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

caminho_json = "dados_contadores.json"
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

                # Dicionário para armazenar os DataFrames por título
                dataframes = {}
                # Para cada conjunto de contagem
                for conjunto in dados:
                    titulo = conjunto["titulo"]
                    contagens = conjunto["contagens"]

                    # Cria DataFrame a partir da lista de contagens
                    df = pd.DataFrame(contagens)
                    # Adiciona ao dicionário com o título como chave
                    dataframes[titulo] = df


                for titulo, df in dataframes.items():
                    print(f"Atualizando dados para: {titulo}")
                    # 1. Atualiza planilha Excel local
                    nome_excel = f"{titulo}.xlsx"
                    df_final = cria_excel(df, nome_excel)

                    # 2. Atualiza Google Sheets
                    atualizar_google_sheets(titulo, df_final)

                    # 3. Envia mensagem no Telegram
                    enviar_mensagem_telegram(df, titulo)

                    # 4. Gera PDF do relatório
                    nome_pdf = f"{titulo}_relatorio.pdf"
                    gerar_relatorio_pdf(nome_pdf, df_final, f"Relatório de Contagem - {titulo}")

                    print(f"Pronto para enviar e-mail com relatório '{nome_pdf}' quando o botão for clicado.")


        except Exception as e:
            print(f"Erro ao verificar JSON: {e}")

        time.sleep(1)  # espera 1 segundo para não sobrecarregar



# ==== Atualiza ao mudar o conjunto ou o tipo de gráfico ====
combo_conjuntos.bind("<<ComboboxSelected>>", lambda e: atualizar_grafico())
combo_grafico.bind("<<ComboboxSelected>>", lambda e: atualizar_grafico())

threading.Thread(target=monitorar_json, daemon=True).start()
entrada = tk.Entry(root, width=30)
entrada.pack(pady=10)

# Botão para salvar o texto
botao_email = tk.Button(root, text="Salvar email", command=salvar_email)
botao_email.pack(pady=10)

atualizar_grafico()
root.mainloop()


