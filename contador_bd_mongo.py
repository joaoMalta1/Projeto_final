import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from pymongo import MongoClient

# ==== Conectar ao MongoDB ====
client = MongoClient("mongodb://localhost:27017/")
db = client["meu_banco"]
colecao = db["contagens"]

# Buscar o primeiro documento
documento = colecao.find_one()
contadores = documento["contadores"]
historico = documento["historico"]

# ==== Processar os dados ====
valores = [0] * len(contadores)
evolucao = [[] for _ in contadores]

for evento in historico:
    for i in range(len(contadores)):
        if evento == i + 1:
            valores[i] += 1
        evolucao[i].append(valores[i])

dias = list(range(1, len(historico) + 1))

# ==== Interface Tkinter ====
root = tk.Tk()
root.title("Gráfico de Contadores (MongoDB)")
root.geometry("900x700")

tk.Label(root, text="Selecione o tipo de gráfico:").pack(pady=5)
tipos_grafico = ["Linha", "Barra", "Pizza"]
selected_grafico = tk.StringVar(value=tipos_grafico[0])
combo_grafico = ttk.Combobox(root, textvariable=selected_grafico, values=tipos_grafico, state="readonly")
combo_grafico.pack()

frame_grafico = tk.Frame(root)
frame_grafico.pack(fill="both", expand=True, padx=10, pady=10)

def atualizar_grafico():
    modo = selected_grafico.get()
    fig, ax = plt.subplots(figsize=(6, 4))

    if modo == "Linha":
        for i, contador in enumerate(contadores):
            ax.step(dias, evolucao[i], label=contador)
        ax.set_title("Evolução acumulada (Linha)")
        ax.set_xlabel("Evento")
        ax.set_ylabel("Total Contado")
        ax.legend()
        ax.grid(True)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    elif modo == "Barra":
        ax.bar(contadores, valores, color='skyblue')
        ax.set_title("Total por Contador (Barra)")
        ax.set_ylabel("Total Contado")
        ax.grid(True)

    elif modo == "Pizza":
        ax.pie(valores, labels=[f"{contadores[i]}: {valores[i]}" for i in range(len(contadores))],
               autopct='%1.1f%%')
        ax.set_title("Distribuição por Contador (Pizza)")

    for widget in frame_grafico.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

combo_grafico.bind("<<ComboboxSelected>>", lambda e: atualizar_grafico())
atualizar_grafico()
root.mainloop()
