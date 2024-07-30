import customtkinter as ctk
from widget.import_section import ImportSection
from widget.graph_visualizer import GraphVisualizer
from widget.results_table import ResultsTable
from widget.inference_section import InferenceSection

class InferencePage:
    def __init__(self, master):
        self.master = master
        
        # Creazione del frame principale per la pagina di inferenza
        self.frame = ctk.CTkFrame(self.master)
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configurazione della griglia all'interno del frame
        for i in range(2):
            self.frame.grid_rowconfigure(i, weight=1)
            self.frame.grid_columnconfigure(i, weight=1)

        # Creazione delle sezioni
        self.import_section = ImportSection(self.frame)
        self.graph_visualizer = GraphVisualizer(self.frame)
        self.post_hoc_methods_section = InferenceSection(self.frame, self.import_section)
        self.results_table = ResultsTable(self.frame)

        # Posizionamento delle sezioni nella griglia
        self.import_section.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.graph_visualizer.frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.post_hoc_methods_section.frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.results_table.frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
