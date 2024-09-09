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

        dataset_loader_imported = self.import_section.dataset_class
        modelclass_imported = self.import_section.model_class
        
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
            self.results_df['MC-Dropout'] = self.compute_mc_dropout(len(original_data))
            
        if self.options_state["Topological data analysis"]:
            self.results_df['Topological data analysis'] = self.compute_topological_data_analysis(len(original_data))
            
        if self.options_state["Ensemble"]:
            self.results_df['Ensemble'] = self.compute_ensemble(len(original_data))
            
        if self.options_state["Few shot learning"]:
            self.results_df['Few shot learning'] = self.compute_few_shot_learning(len(original_data))
                

        self.results_df.insert(1, 'GT', original_data['label'])
        self.result_type = 'classification'
        for column in self.results_df.columns:
            if column not in ['Id', 'GT']:
                self.calculate_statistics(self.results_df)
        self.update_table()


    
    def compute_no_post_hoc_method(self, model, dataloader):
        model.eval()
        inference_results = []

        # Run inference
        with th.no_grad():
            for batch_features, _ in dataloader:
                outputs = model(batch_features)
                inference_results.extend(np.argmax(outputs, axis=1))
    
        return np.array(inference_results)
        
        
        

    def compute_trustscore(self, num_samples):
        # Logic to compute Trustscore
        return np.random.randint(0, 10, num_samples)




    def compute_mc_dropout(self, num_samples):
        
        return np.random.randint(0, 10, num_samples)

    
    
    
    
    def compute_topological_data_analysis(self, num_samples):
        # Logic to compute Topological Data Analysis
        return np.random.randint(0, 10, num_samples)




    def compute_ensemble(self, num_samples):
        # Logic to compute Ensemble
        return np.random.randint(0, 10, num_samples)




    def compute_few_shot_learning(self, num_samples):
        # Logic to compute Few Shot Learning
        return np.random.randint(0, 10, num_samples)



                
    def calculate_statistics(self, data):
        self.stats = {}
        
        ground_truth = data['GT']
        
        for column in data.columns:
            if column not in ['Id','GT']:
                data_column = data[column]
                self.stats[column] = {
                    'accuracy' : accuracy_score(data_column, ground_truth),
                    'precision' : precision_score(data_column, ground_truth, average='weighted'),
                    'recall' :  recall_score(data_column, ground_truth, average='weighted'),
                    'f1_score' :  f1_score(data_column, ground_truth, average='weighted'),
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
            
            # Classificatore: restituisce accuratezza e F1-score
            accuracy = method_stats['accuracy']
            f1_score = method_stats['f1_score']
            return [f"{accuracy:.3f}", f"{f1_score:.3f}"]
        
        # Se il metodo non esiste o non contiene le metriche cercate
        return ["N/A", "N/A"]

        
    def export_results(self):
        # Clear previous messages
        self.comunication_section.display_message("", st.COMUNICATION_COLOR)

        if self.results_df is None or self.results_df.empty:
            self.comunication_section.display_message("No inference results to export.", st.ERROR_COLOR)
            return

        # Prompt the user to select a file path for saving the .csv files
        file_path = fd.asksaveasfilename(
            title='Save as',
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile='results.csv'
        )
        
        if file_path:
            # Split the file path into directory and base file name
            base_path, ext = os.path.splitext(file_path)
            
            # Define paths for statistics and inference results
            stats_file_path = base_path + "_stats" + ext
            results_file_path = base_path + "_inferences" + ext
            
            # Save statistics to the stats file in the requested format
            with open(stats_file_path, 'w') as f:
                # Write the header for the methods
                methods = list(self.stats.keys())
                f.write("metric," + ",".join(methods) + "\n")
                
                # Write each metric as a row
                metrics = ['accuracy', 'precision', 'recall', 'f1_score']
                for metric in metrics:
                    f.write(f"{metric}")
                    for method in methods:
                        f.write(f",{self.stats[method][metric]:.2f}")
                    f.write("\n")
            
            # Save inference results to the results file
            self.results_df.to_csv(results_file_path, index=False)
            
            # Update status message to indicate successful export
            self.comunication_section.display_message(
                f"CSV files exported: {os.path.basename(stats_file_path)} and {os.path.basename(results_file_path)}", 
                st.COMUNICATION_COLOR
            )

