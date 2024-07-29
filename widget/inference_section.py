import customtkinter as ctk
from tkinter import filedialog as fd
import csv

class InferenceSection:
    def __init__(self, master, import_section):
        self.master = master
        self.import_section = import_section  # Referenza all'oggetto ImportSection
        
        # Creazione del frame principale
        self.frame = ctk.CTkFrame(master)
        self.frame.grid_rowconfigure((0, 1, 2), weight=1, uniform="row")
        self.frame.grid_columnconfigure((0, 1), weight=1, uniform="column")

        # Etichetta di intestazione per i metodi post-hoc
        self.post_hoc_label = ctk.CTkLabel(self.frame, text="Post-Hoc Methods", font=("Arial", 18, "bold"))
        self.post_hoc_label.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 5), sticky="nsew")

        # Lista di opzioni con checkbox per i metodi post-hoc
        self.create_post_hoc_widgets()

        # Creazione dei widget per l'esportazione
        self.create_export_widgets()

        # Inizializzazione dei risultati dell'inferenza
        self.inference_results = []

    def create_post_hoc_widgets(self):
        options = [
            "Trustscore",
            "MC-Dropout",
            "Topological data analysis",
            "Ensemble",
            "Few shot learning",
        ]

        # Creazione di una cornice per le checkbox
        self.checkbox_frame = ctk.CTkFrame(self.frame)
        self.checkbox_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="nsew")

        # Disposizione delle checkbox in orizzontale e centrata
        num_columns = 3  # Numero massimo di colonne per le checkbox
        for idx, option in enumerate(options):
            checkbox = ctk.CTkCheckBox(self.checkbox_frame, text=option, font=("Arial", 12))
            checkbox.grid(row=idx // num_columns, column=idx % num_columns, pady=2, padx=5, sticky="w")

        # Configura la griglia della checkbox_frame per far sì che i checkbox si adattino
        for i in range(num_columns):
            self.checkbox_frame.grid_columnconfigure(i, weight=1)

    def create_export_widgets(self):
        # Pulsante per eseguire l'inferenza
        self.inference_button = ctk.CTkButton(self.frame, text="Run Inference", command=self.run_inference, font=("Arial", 12))
        self.inference_button.grid(row=2, column=0, pady=5, padx=10, sticky="ew")

        # Pulsante per esportare i risultati
        self.export_button = ctk.CTkButton(self.frame, text="Export .csv", command=self.export_results, font=("Arial", 12))
        self.export_button.grid(row=2, column=1, pady=5, padx=10, sticky="ew")

    def run_inference(self):
        # Recupera i file importati
        model_file = self.import_section.get_model_file()
        dataloader_file = self.import_section.get_dataloader_file()
        dataset_file = self.import_section.get_dataset_file()
        
        if not model_file or not dataloader_file or not dataset_file:
            print("Please ensure all required files are imported before running inference.")
            return
        
        # Simula un processo di inferenza
        self.inference_results = ["Result 1", "Result 2", "Result 3"]
        print("Running inference...")
        print(f"Using model file: {model_file}")
        print(f"Using dataloader file: {dataloader_file}")
        print(f"Using dataset file: {dataset_file}")
        # Mostra i risultati dell'inferenza
        print("Inference results:", self.inference_results)

    def export_results(self):
        if not self.inference_results:
            print("No inference results to export.")
            return
        
        # Chiede all'utente di selezionare un percorso per il file .csv
        file_path = fd.asksaveasfilename(
            title='Save as',
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile='results.csv'
        )
        
        if file_path:
            # Esporta i risultati in un file CSV
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Inference Results"])  # Header
                for result in self.inference_results:
                    writer.writerow([result])
            print(f"Results exported to {file_path}")
