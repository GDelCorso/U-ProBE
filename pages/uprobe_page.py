import customtkinter as ctk
from widget.import_widget import ImportSection
from widget.graph_visualizer_widget import GraphVisualizer
from widget.results_table_widget import ResultsTable
from widget.inference_widget import InferenceSection

class UprobePage:
    def __init__(self, master):
        self.master = master
        
        # Main frame for the inference page
        self.frame = ctk.CTkFrame(self.master)
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Grid configuration
        for i in range(2):
            self.frame.grid_rowconfigure(i, weight=1)
            self.frame.grid_columnconfigure(i, weight=1)

        # Create sections
        self.import_section = ImportSection(self.frame)
        self.graph_visualizer = GraphVisualizer(self.frame, self.import_section)
        self.results_table = ResultsTable(self.frame)  
        self.inference_section = InferenceSection(self.frame, self.import_section, self.results_table)  

        # Position sections in the grid
        self.import_section.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.graph_visualizer.frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.inference_section.frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.results_table.frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
