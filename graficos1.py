import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random

# Tipos de contagem e dados fictícios
contadores = ['Contagem A', 'Contagem B', 'Contagem C', 'Contagem D', 'Contagem E']

dias = list(range(1, 31))
contagem = []
for i in range(30):
    alt = random.randint(1,5)
    contagem.append(alt)
valores = [0,0,0,0,0]
lista_conts = [
    [],[],[],[],[]
]
for n in contagem:
    for i in range(5):
        if n == i+1:
            valores[i]+=1
        lista_conts[i].append(valores[i])
for lista in lista_conts:
    print(lista)

# Janela principal
root = tk.Tk()
root.title("Gráfico por Tipo de Contagem")
root.geometry("900x700")



# Label e Combobox para tipo de gráfico
tk.Label(root, text="Selecione o tipo de gráfico:").pack(pady=5)
tipos_grafico = ["Linha", "Barra", "Pizza"]
selected_grafico = tk.StringVar(value=tipos_grafico[0])
combo_grafico = ttk.Combobox(root, textvariable=selected_grafico, values=tipos_grafico, state="readonly")
combo_grafico.pack()

# Frame do gráfico
frame_grafico = tk.Frame(root)
frame_grafico.pack(fill="both", expand=True, padx=10, pady=10)

# Função para atualizar o gráfico
def atualizar_grafico():
    modo = selected_grafico.get()

    fig, ax = plt.subplots(figsize=(6, 4))

    if modo == "Linha":
        fig.clear()
        fig, ax = plt.subplots(figsize=(6, 4))
        for contador in contadores:
            for lista in lista_conts:
                if lista_conts.index(lista) == contadores.index(contador):
                    y = lista
                    ax.step(dias,y,label = contador)
                    ax.set_title("Evolução dos contadores por dia")
                    ax.spines['bottom'].set_visible(False) 
                    ax.get_xaxis().set_visible(False)   
                    ax.set_ylabel("Quantidade contada")
                    ax.grid(True)
                    ax.legend()
    elif modo == "Barra":
        ax.bar(contadores, valores, color='skyblue')
        for i, v in enumerate(valores):
            ax.text(i, v + 0.5, str(v), ha='center')
        ax.set_title("Total por contador")
        ax.set_ylabel("Total Contado")
        ax.grid(True)

    elif modo == "Pizza":
        y = valores
        ax.pie(y, labels=[f"{contadores[i]}: {y[i]}" for i in range(len(contadores))], autopct='%1.1f%%')
        ax.set_title("Distribuição entre contadores")

    # Limpar gráfico anterior
    for widget in frame_grafico.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

# Atualização automática ao trocar as opções

combo_grafico.bind("<<ComboboxSelected>>", lambda e: atualizar_grafico())



# Mostrar gráfico inicial
atualizar_grafico()

root.mainloop()
