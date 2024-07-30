import tkinter as tk
import customtkinter as ctk
from config import AppStyles as st  # Importa la classe di configurazione

class ResultsTable:
    def __init__(self, master):
        self.master = master
        
        # Creazione del frame principale per la visualizzazione della tabella
        self.frame = ctk.CTkFrame(self.master, corner_radius=15, fg_color=st.CELL_BG)
        self.frame.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')
        
        # Dati della tabella
        methodologies = [
            "No method",
            "Trustscore",
            "MC-Dropout",
            "Topological data analysis",
            "Ensemble",
            "Few shot learning"
        ]
        
        ground_truth = ["0.64", "0.85", "0.90", "0.78", "0.88", "0.80"]
        prediction = ["0.77", "0.84", "0.91", "0.76", "0.87", "0.82"]
        
        data = list(zip(methodologies, ground_truth, prediction))
        
        # Creazione delle intestazioni delle colonne
        tk.Label(self.frame, text="Methodologies", font=st.COLUMN_FONT, bg=st.HEADER_BG, fg=st.HEADER_FG).grid(row=0, column=0, sticky='nsew', padx=1, pady=1)
        tk.Label(self.frame, text="Ground Truth", font=st.COLUMN_FONT, bg=st.HEADER_BG, fg=st.HEADER_FG).grid(row=0, column=1, sticky='nsew', padx=1, pady=1)
        tk.Label(self.frame, text="Prediction", font=st.COLUMN_FONT, bg=st.HEADER_BG, fg=st.HEADER_FG).grid(row=0, column=2, sticky='nsew', padx=1, pady=1)
        
        # Configurazione delle colonne del frame principale
        self.frame.grid_columnconfigure(0, weight=1, minsize=150)
        self.frame.grid_columnconfigure(1, weight=1, minsize=150)
        self.frame.grid_columnconfigure(2, weight=1, minsize=150)

        for i, (method, gt, pred) in enumerate(data, start=1):
            # Riga dei dati
            tk.Label(self.frame, text=method, font=st.CELL_FONT, bg=st.CELL_BG, fg=st.CELL_FG).grid(row=i, column=0, sticky='nsew', padx=1, pady=1)
            tk.Label(self.frame, text=gt, font=st.CELL_FONT, bg=st.CELL_BG, fg=st.CELL_FG).grid(row=i, column=1, sticky='nsew', padx=1, pady=1)
            tk.Label(self.frame, text=pred, font=st.CELL_FONT, bg=st.CELL_BG, fg=st.CELL_FG).grid(row=i, column=2, sticky='nsew', padx=1, pady=1)
            
            # Configurazione del layout del frame
            self.frame.grid_rowconfigure(i, weight=1)
