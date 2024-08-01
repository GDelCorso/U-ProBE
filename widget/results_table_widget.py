import tkinter as tk
import customtkinter as ctk
from config import AppStyles as st  

class ResultsTable:
    def __init__(self, master):
        self.master = master
        self.data = None  # Dati iniziali impostati a None

        # Creazione del frame principale per la visualizzazione della tabella
        self.frame = ctk.CTkFrame(self.master, corner_radius=15, fg_color=st.CELL_BG)
        self.frame.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')
        
        # Creazione delle intestazioni delle colonne
        tk.Label(self.frame, text="Methodologies", font=st.COLUMN_FONT, bg=st.HEADER_BG, fg=st.HEADER_FG).grid(row=0, column=0, sticky='nsew', padx=1, pady=1)
        tk.Label(self.frame, text="Ground Truth", font=st.COLUMN_FONT, bg=st.HEADER_BG, fg=st.HEADER_FG).grid(row=0, column=1, sticky='nsew', padx=1, pady=1)
        tk.Label(self.frame, text="Prediction", font=st.COLUMN_FONT, bg=st.HEADER_BG, fg=st.HEADER_FG).grid(row=0, column=2, sticky='nsew', padx=1, pady=1)
        
        # Configurazione delle colonne del frame principale
        self.frame.grid_columnconfigure(0, weight=1, minsize=150)
        self.frame.grid_columnconfigure(1, weight=1, minsize=150)
        self.frame.grid_columnconfigure(2, weight=1, minsize=150)

        # Dizionario per memorizzare i riferimenti ai widget
        self.labels = {
            "Methodologies": [],
            "Ground Truth": [],
            "Prediction": []
        }
        
        self.init_table()

    def init_table(self):
        # Dati iniziali (valori nulli) da visualizzare
        methodologies = [
            "No method",
            "Trustscore",
            "MC-Dropout",
            "Topological data analysis",
            "Ensemble",
            "Few shot learning"
        ]
        
        empty_value = "N/A"  # Valore da mostrare prima che l'inferenza venga eseguita
        
        for i, method in enumerate(methodologies, start=1):
            tk.Label(self.frame, text=method, font=st.CELL_FONT, bg=st.CELL_BG, fg=st.CELL_FG).grid(row=i, column=0, sticky='nsew', padx=1, pady=1)
            tk.Label(self.frame, text=empty_value, font=st.CELL_FONT, bg=st.CELL_BG, fg=st.CELL_FG).grid(row=i, column=1, sticky='nsew', padx=1, pady=1)
            tk.Label(self.frame, text=empty_value, font=st.CELL_FONT, bg=st.CELL_BG, fg=st.CELL_FG).grid(row=i, column=2, sticky='nsew', padx=1, pady=1)
            
            # Memorizza i riferimenti ai widget
            self.labels["Methodologies"].append(self.frame.grid_slaves(row=i, column=0)[0])
            self.labels["Ground Truth"].append(self.frame.grid_slaves(row=i, column=1)[0])
            self.labels["Prediction"].append(self.frame.grid_slaves(row=i, column=2)[0])
            
            # Configurazione del layout del frame
            self.frame.grid_rowconfigure(i, weight=1)

    def update_table(self, inference_results):
        if inference_results is None or len(inference_results) != len(self.labels["Ground Truth"]):
            return

        for i, (ground_truth, prediction) in enumerate(inference_results):
            # Aggiorna il valore di "Ground Truth" e "Prediction" per la riga i+1
            self.labels["Ground Truth"][i].config(text=ground_truth)
            self.labels["Prediction"][i].config(text=prediction)
