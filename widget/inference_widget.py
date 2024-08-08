import customtkinter as ctk
from tkinter import filedialog as fd
import pandas as pd
import os
from config import AppStyles as st
import importlib.util
import torch as th
from torch.utils.data import DataLoader
# import multiprocessing
# from multiprocessing import Process

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
        self.frame.grid_columnconfigure((0, 1), weight=1, uniform="column")

        # Header label for post-hoc methods
        self.post_hoc_label = ctk.CTkLabel(self.frame, text="Post-Hoc Methods", font=st.HEADER_FONT)
        self.post_hoc_label.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 5), sticky="nsew")

        # Create checkboxes for post-hoc methods
        self.create_inference_widgets()

        # Create widgets for export options
        self.create_buttons_widgets()

        # Initialize inference results
        self.inference_results = []

    def create_inference_widgets(self):
        # Dynamically create checkboxes based on options_state keys
        options = list(self.options_state.keys())

        # Create a frame for the checkboxes
        self.checkbox_frame = ctk.CTkFrame(self.frame)
        self.checkbox_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="nsew")

        # Arrange checkboxes horizontally and centered
        num_columns = 3  # Maximum number of columns for checkboxes
        self.checkboxes = {}
        for idx, option in enumerate(options):
            checkbox = ctk.CTkCheckBox(self.checkbox_frame, text=option, font=st.TEXT_FONT, command=lambda opt=option: self.update_option_state(opt))
            checkbox.grid(row=idx // num_columns, column=idx % num_columns, pady=2, padx=5, sticky="w")
            self.checkboxes[option] = checkbox

        # Configure checkbox_frame grid to make checkboxes adapt
        for i in range(num_columns):
            self.checkbox_frame.grid_columnconfigure(i, weight=1)

    def create_buttons_widgets(self):
        # Button to run inference
        self.inference_button = ctk.CTkButton(self.frame, text="Run Inference", command=self.run_inference, font=st.BUTTON_FONT)
        self.inference_button.grid(row=2, column=0, pady=5, padx=10, sticky="ew")

        # Button to export results
        self.export_button = ctk.CTkButton(self.frame, text="Export .csv", command=self.export_results, font=st.BUTTON_FONT)
        self.export_button.grid(row=2, column=1, pady=5, padx=10, sticky="ew")

    def update_option_state(self, option):
        # Toggle the state of the specified option
        self.options_state[option] = not self.options_state[option]

    def run_inference(self):
        # Clear previous messages
        self.comunication_section.display_message("", st.COMUNICATION_COLOR)

        # Check if all required files are imported
        if not self.import_section.get_model_file() or not self.import_section.get_dataset_file() or not self.import_section.get_data_file():
            self.comunication_section.display_message("Please ensure all required files are imported before running inference.", st.ERROR_COLOR)
            return

        # Check if at least one checkbox is selected
        if not any(self.options_state.values()):
            self.comunication_section.display_message(
                "Please select at least one post-hoc method before running inference.",
                st.ERROR_COLOR
            )
            return

        # Retrieve imported files
        model_file = self.import_section.get_model_file()
        dataset_loader_file = self.import_section.get_dataset_file()
        data_file = self.import_section.get_data_file()

        if not model_file or not dataset_loader_file or not data_file:
            self.comunication_section.display_message(
                "Please ensure all required files are imported before running inference.",
                st.ERROR_COLOR
            )
            return

        # Start progress indication
        self.comunication_section.start_progress()
        self.comunication_section.display_message(
            "Inference in progress... Please wait.",
            st.COMUNICATION_COLOR
        )

        try:
            # Import the Dataset class from the dataset file
            spec = importlib.util.spec_from_file_location("DatasetModule", dataset_loader_file)
            if spec is None:
                self.comunication_section.display_message(f"Cannot find the file: {dataset_loader_file}", st.ERROR_COLOR)
                return
            dataset_module = importlib.util.module_from_spec(spec)
            if spec.loader is None:
                self.comunication_section.display_message(f"Cannot load the loader for the module: {dataset_loader_file}", st.ERROR_COLOR)
                return
            spec.loader.exec_module(dataset_module)

            # Check if CustomLoader class exists in the module
            if not hasattr(dataset_module, 'CustomLoader'):
                self.comunication_section.display_message(f"The file {dataset_loader_file} does not contain a CustomLoader class.", st.ERROR_COLOR)
                return
            
            dataset_loader_imported = dataset_module.CustomLoader

            # Load the dataset from the CSV file
            data = pd.read_csv(data_file)

            # Initialize custom dataset and dataloader
            dataset = dataset_loader_imported(data)
            dataloader = DataLoader(dataset, batch_size=4, shuffle=False)

            # Load the trained model
            model = th.jit.load(model_file)
            model.eval()

            # Placeholder for inference results
            self.inference_results = []

            # Run inference
            with th.no_grad():
                for batch_features, _ in dataloader:
                    outputs = model(batch_features)
                    self.inference_results.extend(outputs.numpy())


            #def aux_fun(index, return_dict, batch_features, model):
            #    return_dict[index] = model(batch_features)
                
                

            # # Run inference
            # with th.no_grad():
            #     manager = multiprocessing.Manager()
            #     return_dict = manager.dict()
            #     i = 0
            #     procs = []
            #     for batch_features, _ in dataloader:
            #         proc = Process(target=aux_fun, args=(i, return_dict, batch_features, model)) 
            #         procs.append(proc)
            #         proc.start
            #         i+=1
            #     for proc in procs:
            #         proc.join()
            
            # #print("Return Dics =", return_dict.values())

            
            # Fake results for testing
            self.fake_results = []
            self.fake_results.append([0.77, 0.84])

            if self.options_state["Trustscore"]:
                self.fake_results.append(self.compute_trustscore())
            else:
                self.fake_results.append(["N/A", "N/A"])

            if self.options_state["MC-Dropout"]:
                self.fake_results.append(self.compute_mc_dropout())
            else:
                self.fake_results.append(["N/A", "N/A"])

            if self.options_state["Topological data analysis"]:
                self.fake_results.append(self.compute_topological_data_analysis())
            else:
                self.fake_results.append(["N/A", "N/A"])

            if self.options_state["Ensemble"]:
                self.fake_results.append(self.compute_ensemble())
            else:
                self.fake_results.append(["N/A", "N/A"])

            if self.options_state["Few shot learning"]:
                self.fake_results.append(self.compute_few_shot_learning())
            else:
                self.fake_results.append(["N/A", "N/A"])

            # Update the results table
            self.results_table.update_table(self.fake_results)

            # Update status message to indicate successful completion
            self.comunication_section.display_message(
                "Inference completed successfully. Results have been generated.",
                st.COMUNICATION_COLOR
            )

        except ImportError as e:
            self.comunication_section.display_message(
                f"Import Error: {e}",
                st.ERROR_COLOR
            )

        except FileNotFoundError as e:
            self.comunication_section.display_message(
                f"File Not Found: {e}",
                st.ERROR_COLOR
            )

        except pd.errors.EmptyDataError as e:
            self.comunication_section.display_message(
                "Dataset file is empty or cannot be read.",
                st.ERROR_COLOR
            )

        except Exception as e:
            self.comunication_section.display_message(
                f"An unexpected error occurred: {e}",
                st.ERROR_COLOR
            )

        finally:
            # Stop progress bar
            self.comunication_section.stop_progress()

    def compute_trustscore(self):
        # Logic to compute Trustscore
        return [0.77, 0.84]  

    def compute_mc_dropout(self):
        # Logic to compute MC-Dropout
        return [0.90, 0.91]  

    def compute_topological_data_analysis(self):
        # Logic to compute Topological Data Analysis
        return [0.78, 0.76]  

    def compute_ensemble(self):
        # Logic to compute Ensemble
        return [0.88, 0.87]  

    def compute_few_shot_learning(self):
        # Logic to compute Few Shot Learning
        return [0.80, 0.82]  

    def export_results(self):
        # Clear previous messages
        self.comunication_section.display_message("", st.COMUNICATION_COLOR)

        if not self.inference_results:
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
            # Extract only file names from paths
            model_file_name = os.path.basename(self.import_section.get_model_file())
            data_file_name = os.path.basename(self.import_section.get_data_file())

            # Export results to a CSV file
            df = pd.DataFrame(self.inference_results, columns=[f"Inference Results for file {model_file_name} on {data_file_name}"])
            df.to_csv(file_path, index=False)
            
            # Update status message to indicate successful export
            self.comunication_section.display_message(f"CSV file exported to {os.path.basename(file_path)}", st.COMUNICATION_COLOR)
