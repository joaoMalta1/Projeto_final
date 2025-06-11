import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random

# Tipos de contagem e dados fictícios
contadores = ['Contagem A', 'Contagem B', 'Contagem C', 'Contagem D', 'Contagem E']
dados_ficticios = {
    contador: [random.randint(0, 20) for _ in range(10)]
    for contador in contadores
}
dias = list(range(1, 11))

# Janela principal
root = tk.Tk()
root.title("Gráfico por Tipo de Contagem")
root.geometry("900x700")

# Label e Combobox para tipo de contagem
tk.Label(root, text="Selecione o tipo de contagem:").pack(pady=5)
contador_escolhido = tk.StringVar(value=contadores[0])
combo_cont = ttk.Combobox(root, textvariable=contador_escolhido, values=contadores, state="readonly")
combo_cont.pack()

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
    cont = contador_escolhido.get()
    modo = selected_grafico.get()
    y = dados_ficticios[cont]

    fig, ax = plt.subplots(figsize=(6, 4))

    if modo == "Linha":
        ax.plot(dias, y, marker='o')
        ax.set_title(f"Evolução de {cont} (Linha)")
        ax.set_xlabel("Dia")
        ax.set_ylabel("Total Contado")
        ax.grid(True)
    elif modo == "Barra":
        ax.bar(dias, y)
        ax.set_title(f"Evolução de {cont} (Barras)")
        ax.set_xlabel("Dia")
        ax.set_ylabel("Total Contado")
        ax.grid(True)
    elif modo == "Pizza":
        fig.clear()
        fig, ax = plt.subplots()
        ax.pie(y, labels=[f"Dia {i}" for i in dias], autopct='%1.1f%%')
        ax.set_title(f"Distribuição de {cont} (Pizza)")

    # Limpar gráfico anterior
    for widget in frame_grafico.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

# Atualização automática ao trocar as opções
combo_cont.bind("<<ComboboxSelected>>", lambda e: atualizar_grafico())
combo_grafico.bind("<<ComboboxSelected>>", lambda e: atualizar_grafico())



# Mostrar gráfico inicial
atualizar_grafico()

root.mainloop()
