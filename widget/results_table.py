import tkinter as tk
from tkinter import font
import customtkinter as ctk

class ResultsTable:
    def __init__(self, master):
        self.master = master
        
        # Creazione del frame principale per la visualizzazione della tabella
        self.frame = ctk.CTkFrame(self.master, corner_radius=15, fg_color='#242424')
        self.frame.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')
        
        # Definizione dei colori e del font
        self.header_font = font.Font(family='Arial', size=16, weight='bold')
        self.cell_font = font.Font(family='Arial', size=12)
        self.header_bg = '#2FA572'
        self.header_fg = 'white'
        self.cell_bg = '#242424'
        self.cell_fg = 'white'
        self.hover_bg = '#404040'
        
        # Dati della tabella
        methodologies = [
            "Trustscore",
            "MC-Dropout",
            "Topological data analysis",
            "Ensemble",
            "Few shot learning"
        ]
        
        ground_truth = ["0.85", "0.90", "0.78", "0.88", "0.80"]
        prediction = ["0.84", "0.91", "0.76", "0.87", "0.82"]
        
        data = list(zip(methodologies, ground_truth, prediction))
        
        # Creazione delle intestazioni delle colonne
        tk.Label(self.frame, text="Methodologies", font=self.header_font, bg=self.header_bg, fg=self.header_fg).grid(row=0, column=0, sticky='nsew', padx=1, pady=1)
        tk.Label(self.frame, text="Ground Truth", font=self.header_font, bg=self.header_bg, fg=self.header_fg).grid(row=0, column=1, sticky='nsew', padx=1, pady=1)
        tk.Label(self.frame, text="Prediction", font=self.header_font, bg=self.header_bg, fg=self.header_fg).grid(row=0, column=2, sticky='nsew', padx=1, pady=1)
        
        # Configurazione delle colonne del frame principale
        self.frame.grid_columnconfigure(0, weight=1, minsize=150)
        self.frame.grid_columnconfigure(1, weight=1, minsize=150)
        self.frame.grid_columnconfigure(2, weight=1, minsize=150)

        for i, (method, gt, pred) in enumerate(data, start=1):
            # Riga dei dati
            tk.Label(self.frame, text=method, font=self.cell_font, bg=self.cell_bg, fg=self.cell_fg).grid(row=i, column=0, sticky='nsew', padx=1, pady=1)
            tk.Label(self.frame, text=gt, font=self.cell_font, bg=self.cell_bg, fg=self.cell_fg).grid(row=i, column=1, sticky='nsew', padx=1, pady=1)
            tk.Label(self.frame, text=pred, font=self.cell_font, bg=self.cell_bg, fg=self.cell_fg).grid(row=i, column=2, sticky='nsew', padx=1, pady=1)
            
            # Configurazione del layout del frame
            self.frame.grid_rowconfigure(i, weight=1)
            
