import customtkinter as ctk
from tkinter import filedialog as fd
import csv

class InferenceExportSection:
    def __init__(self, master):
        # Crea un frame per contenere i widget
        self.frame = ctk.CTkFrame(master)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Etichetta di intestazione
        self.label = ctk.CTkLabel(self.frame, text="Export", font=("Arial", 24, "bold"))
        self.label.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="nsew")

        # Creazione dei widget
        self.create_widgets()

    def create_widgets(self):
        # Pulsante per eseguire l'inferenza
        self.inference_button = ctk.CTkButton(self.frame, text="Run Inference", command=self.run_inference)
        self.inference_button.grid(row=1, column=0, pady=10, padx=10)
        
        # Pulsante per esportare i risultati
        self.export_button = ctk.CTkButton(self.frame, text="Export .csv", command=self.export_results)
        self.export_button.grid(row=2, column=0, pady=10, padx=10)

    def run_inference(self):
        # Simula un processo di inferenza
        self.inference_results = ["Result 1", "Result 2", "Result 3"]
        print("Running inference...")
        # Mostra i risultati dell'inferenza
        print("Inference results:", self.inference_results)

    def export_results(self):
        # Chiede all'utente di selezionare un percorso per il file .csv
        file_path = fd.asksaveasfilename(
            title='Save as',
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
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
