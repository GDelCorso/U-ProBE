import customtkinter as ctk
from widget.import_widget import ImportSection
from widget.graph_visualizer_widget import GraphVisualizer
from widget.results_table_widget import ResultsTable
from widget.inference_widget import InferenceSection

class UprobePage:
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
        self.results_table = ResultsTable(self.frame)  # Crea ResultsTable prima di InferenceSection
        self.inference_section = InferenceSection(self.frame, self.import_section, self.results_table)  # Passa ResultsTable a InferenceSection

        # Posizionamento delle sezioni nella griglia
        self.import_section.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.graph_visualizer.frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.inference_section.frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.results_table.frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
