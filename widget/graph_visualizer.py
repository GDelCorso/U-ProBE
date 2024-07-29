import customtkinter as ctk

class GraphVisualizer:
    def __init__(self, master):
        self.master = master
        
        # Creazione del frame principale per la visualizzazione del grafico
        self.frame = ctk.CTkFrame(self.master)
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configurazione della griglia all'interno del frame
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Creazione dell'etichetta "Placeholder"
        self.placeholder_label = ctk.CTkLabel(self.frame, text="Placeholder Graph Visualizer", font=("Arial", 24, "bold"))
        self.placeholder_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Centratura orizzontale e verticale
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)