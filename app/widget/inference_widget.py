import customtkinter as ctk
from tkinter import filedialog as fd
import pandas as pd
import os
import torch as th
from torch.utils.data import DataLoader
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
        
        self.distances = [
            "Nearest",
            "Average",
            "Centroid",
            "K-Nearest",            
        ]
        
        self.options_state = {option: False for option in self.options}

        self.setup_ui()
        self.results_df = None
        self.inference_thread = None
        self.batch_size = None
        self.selected_distance = "Nearest"
        self.default_k = 5
        self.queue = queue.Queue()

    def setup_ui(self):
        self.frame = ctk.CTkFrame(self.master)
        self.frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
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
        # Frame for parameters
        self.parameters_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.parameters_frame.grid(row=2, column=0, columnspan=3, pady=5, padx=5, sticky="ew")
        
        # Configure columns to distribute space evenly
        for i in range(6):
            self.parameters_frame.grid_columnconfigure(i, weight=1)

        # Batch Size section
        self.batch_size_label = ctk.CTkLabel(self.parameters_frame, text="Batch Size:", font=st.TEXT_FONT)
        self.batch_size_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.batch_size_entry = ctk.CTkEntry(self.parameters_frame, placeholder_text="12", width=50, font=st.TEXT_FONT)
        self.batch_size_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Trustscore options (hidden initially)
        self.distance_frame_label = ctk.CTkLabel(self.parameters_frame, text="Distance:", font=st.TEXT_FONT)
        self.distance_frame_entry = ctk.CTkOptionMenu(
            self.parameters_frame, 
            values=self.distances, 
            font=st.TEXT_FONT,
            width=100,
            command=self.on_distance_change
        )
        
        # K-nearest options (hidden initially)
        self.k_nearest_label = ctk.CTkLabel(self.parameters_frame, text="K:", font=st.TEXT_FONT)
        self.k_nearest_frame_entry = ctk.CTkEntry(self.parameters_frame, placeholder_text="5", width=50, font=st.TEXT_FONT)

        # Hide Trustscore options initially
        self.toggle_trustscore_options(visible=False)

        # Buttons
        self.inference_button = ctk.CTkButton(self.frame, text="Run Inference", command=self.do_inference, font=st.BUTTON_FONT)
        self.inference_button.grid(row=3, column=0, pady=5, padx=5, sticky="ew")
        self.export_button = ctk.CTkButton(self.frame, text="Export .csv", command=self.export_results, font=st.BUTTON_FONT)
        self.export_button.grid(row=3, column=2, pady=5, padx=5, sticky="ew")

    def toggle_trustscore_options(self, visible):
        if visible:
            self.distance_frame_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
            self.distance_frame_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        else:
            self.distance_frame_label.grid_remove()
            self.distance_frame_entry.grid_remove()
            self.k_nearest_label.grid_remove()
            self.k_nearest_frame_entry.grid_remove()

    def on_distance_change(self, choice):
        self.selected_distance = choice
        if choice == "K-Nearest":
            self.k_nearest_label.grid(row=0, column=4, padx=5, pady=5, sticky="e")
            self.k_nearest_frame_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        else:
            self.k_nearest_label.grid_remove()
            self.k_nearest_frame_entry.grid_remove()

    def update_option_state(self, option):
        self.options_state[option] = not self.options_state[option]
        
        if option != "No post-hoc method":
            if self.options_state[option]:
                if not self.options_state["No post-hoc method"]:
                    self.options_state["No post-hoc method"] = True
                    self.checkboxes["No post-hoc method"].select()
        else:
            if not self.options_state["No post-hoc method"]:
                for opt in self.options:
                    if opt != "No post-hoc method":
                        self.options_state[opt] = False
                        self.checkboxes[opt].deselect()
        
        if option == "Trustscore":
            self.toggle_trustscore_options(visible=self.options_state[option])
            if not self.options_state[option]:
                self.selected_distance = None
                self.distance_frame_entry.set(self.distances[0])

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

        if not self.import_section.get_model_file() or not self.import_section.get_data_file() or not self.import_section.get_dataset_file() or not self.import_section.get_modelclass_file():
            self.communication_section.display_message("Please ensure all required files are imported before running inference.", st.ERROR_COLOR)
            return False

        if not any(self.options_state.values()):
            self.communication_section.display_message("Please select at least one method before running inference.", st.ERROR_COLOR)
            return False

        return True

    def get_batch_size(self):
        batch_size_text = self.batch_size_entry.get()
        if not batch_size_text.isdigit() or int(batch_size_text) <= 0:
            self.communication_section.display_message("Invalid batch size. Using default value of 12.", st.WARNING_COLOR)
            return 12
        return int(batch_size_text)
    
    def get_trustscore_params(self):
        distance = self.selected_distance.lower() if self.selected_distance else None  
        
        if distance == "k-nearest":
            k_value = self.k_nearest_frame_entry.get()
            try:
                k = int(k_value) if k_value else self.default_k
                if k <= 0:
                    k = self.default_k
            except ValueError:
                k = self.default_k 
        else:
            k = None
            
        return distance, k

    def run_inference(self):
        model, dataloader, original_data = self.prepare_data(self.batch_size)
        
        test_data = original_data[original_data['split'] == 'test']

        # Crea il DataFrame per i risultati dei test
        self.results_df = pd.DataFrame({"Id": test_data['id'], "GT": test_data['label']})

        if self.options_state["No post-hoc method"]:
            self.results_df['No post-hoc method'], _ = self.compute_no_post_hoc_method(model, dataloader)

        if self.options_state["Trustscore"]:
            self.results_df['Trustscore'] = self.compute_trustscore(model, dataloader)

        if self.options_state["MC-Dropout"]:
            self.results_df['MC-Dropout'] = self.compute_mc_dropout(model, dataloader, len(test_data), self.import_section.get_num_classes(), self.import_section.get_threshold_halting_criterion())

        if self.options_state["Topological data analysis"]:
            self.results_df['Topological data analysis'] = self.compute_topological_data_analysis(model, dataloader, len(test_data))

        if self.options_state["Ensemble"]:
            self.results_df['Ensemble'] = self.compute_ensemble(model, dataloader, len(test_data))

        if self.options_state["Few shot learning"]:
            self.results_df['Few shot learning'] = self.compute_few_shot_learning(model, dataloader, len(test_data))

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
        return methods.no_post_hoc_method(model, dataloader)

    def compute_trustscore(self, model, dataloader):
        distance, k_nearest = self.get_trustscore_params()
        return methods.trustscore(model, dataloader, distance, k_nearest)

    def compute_mc_dropout(self, model, dataloader, num_samples, num_classes, threshold_halting_criterion):
        return methods.mc_dropout(model, dataloader, num_samples, num_classes, threshold_halting_criterion)

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
        # Refactor the code to update the table with the results
        pass
        
    def calculate_statistics(self):
        if self.results_df is None or self.results_df.empty:
            return
        
        ground_truth = self.results_df['GT']
        self.stats = {}
        
        if "No post-hoc method" in self.results_df.columns:
            predictions = self.results_df["No post-hoc method"]
            self.stats["No post-hoc method"] = {
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

