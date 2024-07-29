import customtkinter as ctk
from import_model_section import ImportModelSection
from import_data_section import ImportDataSection
from post_hoc_methods_section import PostHocMethodsSection
from inference_export_section import InferenceExportSection

class InferencePage:
    def __init__(self, master):
        self.master = master

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

        # Creazione delle sezioni
        self.import_model_section = ImportModelSection(self.master)
        self.import_data_section = ImportDataSection(self.master)
        self.post_hoc_methods_section = PostHocMethodsSection(self.master)
        self.inference_export_section = InferenceExportSection(self.master)

        # Creazione dei widget per ogni sezione
        self.import_model_section.create_widgets()
        self.import_data_section.create_widgets()
        self.post_hoc_methods_section.create_widgets()
        self.inference_export_section.create_widgets()

        # Posizionamento delle sezioni nella griglia
        self.import_model_section.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.import_data_section.frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.post_hoc_methods_section.frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.inference_export_section.frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
    def show_inference_page(self):
        pass

