import customtkinter as ctk
from tkinter import filedialog as fd
import pandas as pd
import os
from config import AppStyles as st
import importlib.util
import torch as th
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, mean_squared_error, mean_absolute_error, r2_score

class InferenceSection:
    def __init__(self, master, import_section, results_table, comunication_section):
        self.master = master
        self.import_section = import_section
        self.results_table = results_table 
        self.comunication_section = comunication_section

        # Variables to store the state of checkboxes
        self.options_state = {
            "No post-hoc method": False,
            "Trustscore": False,
            "MC-Dropout": False,
            "Topological data analysis": False,
            "Ensemble": False,
            "Few shot learning": False,
        }

        # Main frame setup
        self.frame = ctk.CTkFrame(master)
        self.frame.grid_rowconfigure((0, 1, 2), weight=1)
        self.frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="column")

        # Header label for post-hoc methods
        self.post_hoc_label = ctk.CTkLabel(self.frame, text="Post-Hoc Methods", font=st.HEADER_FONT)
        self.post_hoc_label.grid(row=0, column=0, columnspan=3, padx=5, pady=(5, 5), sticky="nsew")

        # Create checkboxes for post-hoc methods
        self.create_inference_widgets()

        # Create widgets for export options
        self.create_buttons_widgets()
        
        # Initialize results dataframe
        self.results_df = None

    def create_inference_widgets(self):
        # Dynamically create checkboxes based on options_state keys
        self.options = list(self.options_state.keys())

        # Create a frame for the checkboxes
        self.checkbox_frame = ctk.CTkFrame(self.frame)
        self.checkbox_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=(5, 10), sticky="nsew")

        # Arrange checkboxes horizontally and centered
        num_columns = 3  # Maximum number of columns for checkboxes
        self.checkboxes = {}
        for idx, option in enumerate(self.options):
            checkbox = ctk.CTkCheckBox(self.checkbox_frame, text=option, font=st.TEXT_FONT, command=lambda opt=option: self.update_option_state(opt))
            checkbox.grid(row=idx // num_columns, column=idx % num_columns, pady=2, padx=5, sticky="w")
            self.checkboxes[option] = checkbox

        # Configure checkbox_frame grid to make checkboxes adapt
        for i in range(num_columns):
            self.checkbox_frame.grid_columnconfigure(i, weight=1)




    def create_buttons_widgets(self):
        # Frame per il batch size e il campo di input
        self.batch_size_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.batch_size_frame.grid(row=2, column=0, pady=5, padx=(20,10), sticky="ew")

        # Label e campo di input per la batch size
        self.batch_size_label = ctk.CTkLabel(self.batch_size_frame, text="Batch Size:", font=st.TEXT_FONT)
        self.batch_size_label.grid(row=0, column=0, padx=5, sticky="ew")

        self.batch_size_entry = ctk.CTkEntry(self.batch_size_frame, placeholder_text="4", width=50, font=st.TEXT_FONT)
        self.batch_size_entry.grid(row=0, column=1, padx=5, sticky="ew")

        # Button to run inference
        self.inference_button = ctk.CTkButton(self.frame, text="Run Inference", command=self.do_inference, font=st.BUTTON_FONT)
        self.inference_button.grid(row=2, column=1, pady=5, padx=5, sticky="ew")

        # Button to export results
        self.export_button = ctk.CTkButton(self.frame, text="Export .csv", command=self.export_results, font=st.BUTTON_FONT)
        self.export_button.grid(row=2, column=2, pady=5, padx=5, sticky="ew")






    def update_option_state(self, option):
        # Toggle the state of the specified option
        self.options_state[option] = not self.options_state[option]




    def do_inference(self):
        # Clear previous messages
        self.comunication_section.display_message("", st.COMUNICATION_COLOR)

        batch_size_text = self.batch_size_entry.get()
        if not batch_size_text.isdigit() or int(batch_size_text) <= 0:
            batch_size_text = "4"
        
        batch_size = int(batch_size_text)
        
         # Retrieve imported files
        model_file = self.import_section.get_model_file()
        modelclass_file = self.import_section.get_modelclass_file()
        dataset_loader_file = self.import_section.get_dataset_file()
        data_file = self.import_section.get_data_file()

        if not model_file or not modelclass_file or not dataset_loader_file or not data_file:
            self.comunication_section.display_message(
                "Please ensure all required files are imported before running inference.",
                st.ERROR_COLOR
            )
            return


        # Check if at least one checkbox is selected
        if not any(self.options_state.values()):
            self.comunication_section.display_message(
                "Please select at least one method before running inference.",
                st.ERROR_COLOR
            )
            return

        # Start progress indication
        self.comunication_section.start_progress()
        
        self.comunication_section.display_message(
            "Inference in progress... Please wait.",
            st.COMUNICATION_COLOR
        )

        dataset_loader_imported = self.validate_dataset_loader(dataset_loader_file)
        modelclass_imported = self.import_section.validate_modelclass(modelclass_file)
        
        if not dataset_loader_imported or not modelclass_imported:
            self.comunication_section.stop_progress()
            return
        
        # Load the dataset from the CSV file
        data = pd.read_csv(data_file)

        # Initialize custom dataset and dataloader
        dataset = dataset_loader_imported(data)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        state_dict = th.load(model_file)
        model = modelclass_imported()
        model.load_state_dict(state_dict)

        self.run_inference(model, dataloader, data_file)

        # Update status message to indicate successful completion
        self.comunication_section.display_message(
            "Inference completed successfully. Results have been generated.",
            st.COMUNICATION_COLOR
        )
        self.comunication_section.stop_progress()
            
    def validate_dataset_loader(self, dataset_loader_file):
        try:
            # Import the Dataset class from the dataset file
            spec = importlib.util.spec_from_file_location("DatasetModule", dataset_loader_file)
            if spec is None:
                self.comunication_section.display_message(f"Cannot find the file: {dataset_loader_file}", st.ERROR_COLOR)
                self.comunication_section.stop_progress()
                return
            dataset_module = importlib.util.module_from_spec(spec)
            if spec.loader is None:
                self.comunication_section.display_message(f"Cannot load the loader for the module: {dataset_loader_file}", st.ERROR_COLOR)
                self.comunication_section.stop_progress()
                return 
            spec.loader.exec_module(dataset_module)

            # Check if CustomLoader class exists in the module
            if not hasattr(dataset_module, 'CustomLoader'):
                self.comunication_section.display_message(f"The file {dataset_loader_file} does not contain a CustomLoader class.", st.ERROR_COLOR)
                self.comunication_section.stop_progress()
                return
            
            return dataset_module.CustomLoader
        except Exception as e:
            self.comunication_section.display_message(f"An error occurred while importing the dataset loader: {str(e)}", st.ERROR_COLOR)
            self.comunication_section.stop_progress()
        
            
            
    def run_inference(self, model, dataloader, data_file):
        original_data = pd.read_csv(data_file)
        
        # Inizializza il DataFrame dei risultati con l'Id
        self.results_df = pd.DataFrame({"Id": original_data['id']})
        
        # Esegui l'inferenza per il metodo "No post-hoc" se selezionato
        if self.options_state["No post-hoc method"]:
            self.results_df['No post-hoc method'] = self.compute_no_post_hoc_method(model, dataloader)
        
        # Esegui l'inferenza per gli altri metodi post-hoc selezionati
        if self.options_state["Trustscore"]:
            self.results_df['Trustscore'] = self.compute_trustscore(len(original_data))
            
        if self.options_state["MC-Dropout"]:
            self.results_df['MC-Dropout'] = self.compute_mc_dropout(model, dataloader)
            
        if self.options_state["Topological data analysis"]:
            self.results_df['Topological data analysis'] = self.compute_topological_data_analysis(len(original_data))
            
        if self.options_state["Ensemble"]:
            self.results_df['Ensemble'] = self.compute_ensemble(len(original_data))
            
        if self.options_state["Few shot learning"]:
            self.results_df['Few shot learning'] = self.compute_few_shot_learning(len(original_data))
                
        # Aggiungi la colonna con i valori o le etichette attese e calcola le statistiche
        if self.is_pytorch_classifier(model, dataloader):
            self.results_df.insert(1, 'GT', original_data['label'])
            self.result_type = 'classification'
            for column in self.results_df.columns:
                if column not in ['Id', 'GT']:
                    self.calculate_statistics_classifier(self.results_df)
            self.update_table()
        elif self.is_pytorch_regressor(model, dataloader):
            self.results_df.insert(1, 'GT', original_data['value'])
            self.result_type = 'regression'
            for column in self.results_df.columns:
                if column not in ['Id', 'GT']:
                    self.calculate_statistics_regressor(self.results_df)
            self.update_table()


    def is_pytorch_classifier(self, model, dataloader):
        model.eval()
        with th.no_grad():
            for batch_features, _ in dataloader:
                output = model(batch_features)
                # Se l'output ha più di una dimensione nel secondo asse, è un classificatore
                if output.shape[1] > 1:
                    return True
                else:
                    return False

    def is_pytorch_regressor(self,model, dataloader):
        model.eval()
        with th.no_grad():
            for batch_features, _ in dataloader:
                output = model(batch_features)  
                # Se l'output ha una sola dimensione nel secondo asse, è un regressore
                if output.shape[1] == 1:
                    return True
                else:
                    return False
    
    def compute_no_post_hoc_method(self, model, dataloader):
        model.eval()
        inference_results = []

        # Run inference
        with th.no_grad():
            for batch_features, _ in dataloader:
                outputs = model(batch_features)
                inference_results.extend(outputs.numpy())
    
        return np.array(inference_results)
        
        
        

    def compute_trustscore(self, num_samples):
        # Logic to compute Trustscore
        return np.random.uniform(0.5, 1.0, num_samples) 




    def compute_mc_dropout(self, model, dataloader, num_samples = 10):
        
        model.train()
        inference_results = []
        
        for batch_features, _ in dataloader:
            mean_prediction = self.monte_carlo_inference(model, batch_features, num_samples)
            inference_results.extend(mean_prediction.numpy())
        
        return np.array(inference_results)




    def monte_carlo_inference(self, model, input_data, num_samples):
        model.train()
                
        predictions = []
        with th.no_grad():
            for _ in range(num_samples):
                output = model(input_data)
                predictions.append(output)
    
        # Stack predictions and calculate statistics
        predictions = th.stack(predictions)
        mean_prediction = th.mean(predictions, dim=0)
                
        return mean_prediction
    
    
    
    
    def compute_topological_data_analysis(self, num_samples):
        # Logic to compute Topological Data Analysis
        return np.random.uniform(0.7, 0.9, num_samples)




    def compute_ensemble(self, num_samples):
        # Logic to compute Ensemble
        return np.random.uniform(0.75, 0.98, num_samples)




    def compute_few_shot_learning(self, num_samples):
        # Logic to compute Few Shot Learning
        return np.random.uniform(0.65, 0.92, num_samples)



                
    def calculate_statistics_classifier(self, data):
        self.stats = {}
        
        ground_truth = data['GT']
        
        for column in data.columns:
            if column not in ['Id','GT']:
                self.stats[column] = {
                    'accuracy' : accuracy_score(ground_truth, data[column]),
                    'precision' : precision_score(ground_truth, data[column], average='weighted'),
                    'recall' : recall_score(ground_truth, data[column], average='weighted'),
                    'f1_score' : f1_score(ground_truth, data[column], average='weighted'),
                    'confusion_matrix' : confusion_matrix(ground_truth, data[column]).tolist(),
                }
    
    def calculate_statistics_regressor(self, data):
        self.stats = {}
        
        ground_truth = data['GT']
        
        for column in data.columns:
            if column not in ['Id','GT']:
                self.stats[column] = {
                    'mean_squared_error': mean_squared_error(ground_truth, data[column]),
                    'mean_absolute_error': mean_absolute_error(ground_truth, data[column]),
                    'r2_score' : r2_score(ground_truth, data[column]),
                    'median_absolute_error' : np.median(np.abs(ground_truth - data[column])),
                    'max_error': np.max(np.abs(ground_truth - data[column])),
                }
    

                  
    def update_table(self):
        results_to_table = []
        for method in self.options:
            get_stats = self.get_stats(method)
            results_to_table.append(get_stats)
        
        self.results_table.update_table(results_to_table, self.result_type)
        
        
        
        
    def get_stats(self, method):
        if method in self.stats:
            method_stats = self.stats[method]
            
            if 'accuracy' in method_stats:
                # Classificatore: restituisce accuratezza e F1-score
                accuracy = method_stats['accuracy']
                f1_score = method_stats['f1_score']
                return [f"{accuracy:.3f}", f"{f1_score:.3f}"]

            elif 'mean_squared_error' in method_stats:
                # Regressore: restituisce R² score e Mean Squared Error (MSE)
                r2_score = method_stats['r2_score']
                mse = method_stats['mean_squared_error']
                return [f"{r2_score:.3f}", f"{mse:.3f}"]
        
        # Se il metodo non esiste o non contiene le metriche cercate
        return ["N/A", "N/A"]

        
       # self.results_table.update_results(results_to_table)
    def export_results(self):
        # Clear previous messages
        self.comunication_section.display_message("", st.COMUNICATION_COLOR)

        if self.results_df is None or self.results_df.empty:
            self.comunication_section.display_message("No inference results to export.", st.ERROR_COLOR)
            return
        
        # Prompt the user to select a file path for saving the .csv file
        file_path = fd.asksaveasfilename(
            title='Save as',
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile='results.csv'
        )
        
        if file_path:            
        
            with open(file_path, 'w') as f:
                f.write("\n\nStatistics:\n")
                for column, column_stats in self.stats.items():
                    f.write(f"\n{column}:\n")
                    for stat, value in column_stats.items():
                        f.write(f"{stat}: {value:.2f}\n")
                f.write("\n\nResults:\n")
            self.results_df.to_csv(file_path, mode='a', index=False)
        
            # Update status message to indicate successful export
            self.comunication_section.display_message(f"CSV file exported to {os.path.basename(file_path)}", st.COMUNICATION_COLOR)
