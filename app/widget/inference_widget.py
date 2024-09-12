import customtkinter as ctk
from tkinter import filedialog as fd
import pandas as pd
import os
import torch as th
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import methods
from config import AppStyles as st
import threading
import queue

class InferenceSection:
    def __init__(self, master, import_section, results_table, communication_section):
        self.master = master
        self.import_section = import_section
        self.results_table = results_table
        self.communication_section = communication_section

        self.options = [
            "No post-hoc method",
            "Trustscore",
            "MC-Dropout",
            "Topological data analysis",
            "Ensemble",
            "Few shot learning",
        ]
        self.options_state = {option: False for option in self.options}

        self.setup_ui()

        self.results_df = None
        self.inference_thread = None
        self.batch_size = None
        self.queue = queue.Queue()

    def setup_ui(self):
        self.frame = ctk.CTkFrame(self.master)
        self.frame.grid_rowconfigure((0, 1, 2), weight=1)
        self.frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="column")

        self.post_hoc_label = ctk.CTkLabel(self.frame, text="Post-Hoc Methods", font=st.HEADER_FONT)
        self.post_hoc_label.grid(row=0, column=0, columnspan=3, padx=5, pady=(5, 5), sticky="nsew")

        self.create_inference_widgets()
        self.create_buttons_widgets()

        self.results_df = None

    def create_inference_widgets(self):
        self.checkbox_frame = ctk.CTkFrame(self.frame)
        self.checkbox_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=(5, 10), sticky="nsew")

        num_columns = 3
        self.checkboxes = {}
        for idx, option in enumerate(self.options):
            checkbox = ctk.CTkCheckBox(
                self.checkbox_frame, 
                text=option, 
                font=st.TEXT_FONT, 
                command=lambda opt=option: self.update_option_state(opt)
            )
            checkbox.grid(row=idx // num_columns, column=idx % num_columns, pady=2, padx=5, sticky="w")
            self.checkboxes[option] = checkbox

        for i in range(num_columns):
            self.checkbox_frame.grid_columnconfigure(i, weight=1)

    def create_buttons_widgets(self):
        self.batch_size_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.batch_size_frame.grid(row=2, column=0, pady=5, padx=(20,10), sticky="ew")

        self.batch_size_label = ctk.CTkLabel(self.batch_size_frame, text="Batch Size:", font=st.TEXT_FONT)
        self.batch_size_label.grid(row=0, column=0, padx=5, sticky="ew")

        self.batch_size_entry = ctk.CTkEntry(self.batch_size_frame, placeholder_text="4", width=50, font=st.TEXT_FONT)
        self.batch_size_entry.grid(row=0, column=1, padx=5, sticky="ew")

        self.inference_button = ctk.CTkButton(self.frame, text="Run Inference", command=self.do_inference, font=st.BUTTON_FONT)
        self.inference_button.grid(row=2, column=1, pady=5, padx=5, sticky="ew")

        self.export_button = ctk.CTkButton(self.frame, text="Export .csv", command=self.export_results, font=st.BUTTON_FONT)
        self.export_button.grid(row=2, column=2, pady=5, padx=5, sticky="ew")

    def update_option_state(self, option):
        self.options_state[option] = not self.options_state[option]

    def do_inference(self):
        self.communication_section.display_message("", st.COMUNICATION_COLOR)

        if not self.validate_inputs():
            return

        self.communication_section.start_progress()
        self.communication_section.display_message("Inference in progress... Please wait.", st.COMUNICATION_COLOR)

        self.inference_button.configure(state="disabled")

        self.inference_thread = threading.Thread(target=self.run_inference_thread)
        self.inference_thread.start()

        self.master.after(100, self.check_inference_progress)

    def run_inference_thread(self):
        try:
            self.run_inference()
            self.queue.put(("success", "Inference completed successfully. Results have been generated."))
        except Exception as e:
            self.queue.put(("error", f"An error occurred during inference: {str(e)}"))

    def check_inference_progress(self):
        try:
            message_type, message = self.queue.get_nowait()
            if message_type == "success":
                self.communication_section.display_message(message, st.COMUNICATION_COLOR)
            elif message_type == "error":
                self.communication_section.display_message(message, st.ERROR_COLOR)
            
            self.communication_section.stop_progress()
            self.inference_button.configure(state="normal")
        except queue.Empty:
            self.master.after(100, self.check_inference_progress)

    def validate_inputs(self):
        
        self.batch_size = self.get_batch_size()
        
        if self.batch_size is None:
            return False

        if not self.import_section.get_model_file or not self.import_section.get_data_file or not self.import_section.get_dataset_file or not self.import_section.get_modelclass_file:
            self.communication_section.display_message("Please ensure all required files are imported before running inference.", st.ERROR_COLOR)
            return False

        if not any(self.options_state.values()):
            self.communication_section.display_message("Please select at least one method before running inference.", st.ERROR_COLOR)
            return False

        return True

    def get_batch_size(self):
        batch_size_text = self.batch_size_entry.get()
        if not batch_size_text.isdigit() or int(batch_size_text) <= 0:
            self.communication_section.display_message("Invalid batch size. Using default value of 4.", st.WARNING_COLOR)
            return 4
        return int(batch_size_text)

    def run_inference(self):
        model, dataloader, original_data = self.prepare_data(self.batch_size)

        self.results_df = pd.DataFrame({"Id": original_data['id'], "GT": original_data['label']})

        if self.options_state["No post-hoc method"]:
            self.results_df['No post-hoc method'] = self.compute_no_post_hoc_method(model, dataloader)

        if self.options_state["Trustscore"]:
            self.results_df['Trustscore'] = self.compute_trustscore(model, dataloader,len(original_data))

        if self.options_state["MC-Dropout"]:
            self.results_df['MC-Dropout'] = self.compute_mc_dropout(model, dataloader, len(original_data))

        if self.options_state["Topological data analysis"]:
            self.results_df['Topological data analysis'] = self.compute_topological_data_analysis(model, dataloader, len(original_data))

        if self.options_state["Ensemble"]:
            self.results_df['Ensemble'] = self.compute_ensemble(model, dataloader, len(original_data))

        if self.options_state["Few shot learning"]:
            self.results_df['Few shot learning'] = self.compute_few_shot_learning(model, dataloader, len(original_data))

        self.calculate_statistics()
        self.update_table()

    def prepare_data(self, batch_size):
        model_file = self.import_section.get_model_file()
        data_file = self.import_section.get_data_file()

        dataset_loader_imported = self.import_section.dataset_class
        modelclass_imported = self.import_section.model_class

        data = pd.read_csv(data_file)
        dataset = dataset_loader_imported(data)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        state_dict = th.load(model_file)
        model = modelclass_imported()
        model.load_state_dict(state_dict)

        return model, dataloader, data

    def compute_no_post_hoc_method(self, model, dataloader):
        model.eval()
        inference_results = []
        with th.no_grad():
            for batch_features, _ in dataloader:
                outputs = model(batch_features)
                inference_results.extend(np.argmax(outputs, axis=1))
        return np.array(inference_results)

    def compute_trustscore(self, model, dataloader, num_samples):
        return methods.trustscore(model, dataloader, num_samples)

    def compute_mc_dropout(self, model, dataloader, num_samples):
        return methods.mc_dropout(model, dataloader, num_samples)

    def compute_topological_data_analysis(self, model, dataloader, num_samples):
        return methods.topological_data_analysis(model, dataloader, num_samples)

    def compute_ensemble(self, model, dataloader, num_samples):
        return methods.ensemble(model, dataloader, num_samples)

    def compute_few_shot_learning(self, model, dataloader, num_samples):
        return methods.few_shot_learning(model, dataloader, num_samples)

    def get_stats(self, method):
        if method in self.stats:
            method_stats = self.stats[method]
            
            accuracy= method_stats['accuracy']
            precision = method_stats['precision']
            return [f"{accuracy:.4f}", f"{precision:.4f}"]
        return ["N/A", "N/A"]
        

    def update_table(self):
        results_to_table = []
        for method in self.options:
            get_stats = self.get_stats(method)
            results_to_table.append(get_stats)
        
        self.results_table.update_table(results_to_table, 'classification')
        
    def calculate_statistics(self):
        if self.results_df is None or self.results_df.empty:
            return
        
        ground_truth = self.results_df['GT']
        self.stats = {}
        
        for column in self.results_df.columns:
            if column not in ['Id', 'GT']:
                predictions = self.results_df[column]
                self.stats[column] = {
                    'accuracy': accuracy_score(ground_truth, predictions),
                    'precision': precision_score(ground_truth, predictions, average='weighted', zero_division=0),
                    'recall': recall_score(ground_truth, predictions, average='weighted', zero_division=0),
                    'f1_score': f1_score(ground_truth, predictions, average='weighted', zero_division=0)
                }
                

    def export_results(self):
        if self.results_df is None or self.results_df.empty or not self.stats:
            self.communication_section.display_message("No results to export. Please run inference first.", st.ERROR_COLOR)
            return

        file_path = fd.asksaveasfilename(
            title='Save as',
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile='results.csv'
        )
        if file_path:
            base_path, ext = os.path.splitext(file_path)
            stats_file_path = base_path + "_stats" + ext
            results_file_path = base_path + "_inferences" + ext

            with open(stats_file_path, 'w') as f:
                methods = list(self.stats.keys())
                f.write("metric," + ",".join(methods) + "\n")
                metrics = ['accuracy', 'precision', 'recall', 'f1_score']
                for metric in metrics:
                    f.write(f"{metric}")
                    for method in methods:
                        f.write(f",{self.stats[method][metric]:.4f}")
                    f.write("\n")

            self.results_df.to_csv(results_file_path, index=False)

            self.communication_section.display_message(
                f"CSV files exported: {os.path.basename(stats_file_path)} and {os.path.basename(results_file_path)}",
                st.COMUNICATION_COLOR
            )
        else:
            self.communication_section.display_message("Export cancelled.", st.ERROR_COLOR)

