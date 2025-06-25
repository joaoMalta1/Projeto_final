import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import json, os

# ==== Carregar o JSON ====
path_json = os.path.join("db", "conjuntos.json")
if os.path.exists(path_json):
    with open(path_json, "r", encoding="utf-8") as f:
        dados = json.load(f)



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

# ==== Atualiza ao mudar o conjunto ou o tipo de gráfico ====
combo_conjuntos.bind("<<ComboboxSelected>>", lambda e: atualizar_grafico())
combo_grafico.bind("<<ComboboxSelected>>", lambda e: atualizar_grafico())

atualizar_grafico()
root.mainloop()
