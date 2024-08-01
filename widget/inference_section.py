import customtkinter as ctk
from tkinter import filedialog as fd
import pandas as pd
import os
from config import AppStyles as st
import importlib.util
import torch as th
from torch.utils.data import DataLoader

class InferenceSection:
    def __init__(self, master, import_section):
        self.master = master
        self.import_section = import_section

        # Variabili per memorizzare lo stato delle checkbox
        self.options_state = {
            "Trustscore": False,
            "MC-Dropout": False,
            "Topological data analysis": False,
            "Ensemble": False,
            "Few shot learning": False,
        }

        # Creazione del frame principale
        self.frame = ctk.CTkFrame(master)
        self.frame.grid_rowconfigure((0, 1, 2), weight=1)
        self.frame.grid_columnconfigure((0, 1), weight=1, uniform="column")

        # Etichetta di intestazione per i metodi post-hoc
        self.post_hoc_label = ctk.CTkLabel(self.frame, text="Post-Hoc Methods", font=st.HEADER_FONT)
        self.post_hoc_label.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 5), sticky="nsew")

        # Lista di opzioni con checkbox per i metodi post-hoc
        self.create_post_hoc_widgets()

        # Creazione dei widget per l'esportazione
        self.create_export_widgets()

        # Etichetta per messaggi di stato e errori, inizialmente vuota
        self.status_label = ctk.CTkLabel(self.frame, text="", font=st.STATUS_FONT)
        self.status_label.grid(row=3, column=0, columnspan=2, padx=5, pady=2, sticky="nsew")

        # Inizializzazione dei risultati dell'inferenza
        self.inference_results = []

    def create_post_hoc_widgets(self):
        # Costruzione dinamica della lista delle opzioni dalle chiavi di options_state
        options = list(self.options_state.keys())

        # Creazione di una cornice per le checkbox
        self.checkbox_frame = ctk.CTkFrame(self.frame)
        self.checkbox_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="nsew")

        # Disposizione delle checkbox in orizzontale e centrata
        num_columns = 3  # Numero massimo di colonne per le checkbox
        self.checkboxes = {}
        for idx, option in enumerate(options):
            checkbox = ctk.CTkCheckBox(self.checkbox_frame, text=option, font=st.TEXT_FONT, command=lambda opt=option: self.update_option_state(opt))
            checkbox.grid(row=idx // num_columns, column=idx % num_columns, pady=2, padx=5, sticky="w")
            self.checkboxes[option] = checkbox

        # Configura la griglia della checkbox_frame per far sì che i checkbox si adattino
        for i in range(num_columns):
            self.checkbox_frame.grid_columnconfigure(i, weight=1)

    def create_export_widgets(self):
        # Pulsante per eseguire l'inferenza
        self.inference_button = ctk.CTkButton(self.frame, text="Run Inference", command=self.run_inference, font=st.BUTTON_FONT)
        self.inference_button.grid(row=2, column=0, pady=5, padx=10, sticky="ew")

        # Pulsante per esportare i risultati
        self.export_button = ctk.CTkButton(self.frame, text="Export .csv", command=self.export_results, font=st.BUTTON_FONT)
        self.export_button.grid(row=2, column=1, pady=5, padx=10, sticky="ew")

    def update_option_state(self, option):
        self.options_state[option] = not self.options_state[option]

    def run_inference(self):
        # Cancella il messaggio di errore precedente
        self.status_label.configure(text="", font=st.STATUS_FONT)

        # Verifica se almeno una checkbox è selezionata
        if not any(self.options_state.values()):
            self.status_label.configure(
                text="Please select at least one post-hoc method before running inference.",
                text_color=st.ERROR_COLOR
            )
            return

        # Recupera i file importati
        model_file = self.import_section.get_model_file()
        dataset_file = self.import_section.get_dataset_file()
        data_file = self.import_section.get_data_file()

        if not model_file or not dataset_file or not data_file:
            self.status_label.configure(
                text="Please ensure all required files are imported before running inference.",
                text_color=st.ERROR_COLOR
            )
            return

        # Messaggio di inferenza in corso
        self.status_label.configure(
            text="Inference in progress... Please wait.",
            text_color=st.COMUNICATION_COLOR
        )

        try:
            # Importa la classe Dataset dal file del dataset
            spec = importlib.util.spec_from_file_location("DatasetModule", dataset_file)
            if spec is None:
                raise ImportError(f"Cannot find the file: {dataset_file}")
            dataset_module = importlib.util.module_from_spec(spec)
            if spec.loader is None:
                raise ImportError(f"Cannot load the loader for the module: {dataset_file}")
            spec.loader.exec_module(dataset_module)
            Dataset_imported = dataset_module.CustomDataset

            # Carica il dataset dal file CSV
            data = pd.read_csv(data_file)
            features = data.iloc[:, :-1].values  # Tutte le colonne tranne l'ultima sono le feature
            targets = data.iloc[:, -1].values    # L'ultima colonna è il target

            # Inizializza il dataset personalizzato e il dataloader
            dataset = Dataset_imported(features, targets)
            dataloader = DataLoader(dataset, batch_size=32, shuffle=False)

            # Carica il modello addestrato
            model = th.jit.load(model_file)
            model.eval()

            # Placeholder per i risultati dell'inferenza
            self.inference_results = []

            # Inferenza
            with th.no_grad():
                for batch_features, _ in dataloader:
                    outputs = model(batch_features)
                    self.inference_results.extend(outputs.numpy())

            # Messaggio di completamento inferenza
            self.status_label.configure(
                text="Inference completed successfully. Results have been generated.",
                text_color=st.COMUNICATION_COLOR
            )

        except ImportError as e:
            self.status_label.configure(
                text=f"Import Error: {e}",
                text_color=st.ERROR_COLOR
            )

        except FileNotFoundError as e:
            self.status_label.configure(
                text=f"File Not Found: {e}",
                text_color=st.ERROR_COLOR
            )

        except pd.errors.EmptyDataError as e:
            self.status_label.configure(
                text="Dataset file is empty or cannot be read.",
                text_color=st.ERROR_COLOR
            )

        except Exception as e:
            self.status_label.configure(
                text=f"An unexpected error occurred: {e}",
                text_color=st.ERROR_COLOR
            )

    def export_results(self):
        # Cancella il messaggio di errore precedente
        self.status_label.configure(text="", font=st.STATUS_FONT)

        if not self.inference_results:
            self.status_label.configure(text="No inference results to export.", text_color=st.ERROR_COLOR)
            return
        
        # Chiede all'utente di selezionare un percorso per il file .csv
        file_path = fd.asksaveasfilename(
            title='Save as',
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile='results.csv'
        )
        
        if file_path:
            # Estrai solo i nomi dei file dai percorsi
            model_file_name = os.path.basename(self.import_section.get_model_file())
            data_file_name = os.path.basename(self.import_section.get_data_file())

            # Esporta i risultati in un file CSV
            df = pd.DataFrame(self.inference_results, columns=[f"Inference Results for file {model_file_name} on {data_file_name}"])
            df.to_csv(file_path, index=False)
            
            # Messaggio di esportazione completata
            self.status_label.configure(text=f"CSV file exported to {os.path.basename(file_path)}", text_color=st.COMUNICATION_COLOR)
