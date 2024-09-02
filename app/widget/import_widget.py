import importlib.util
import customtkinter as ctk
from tkinter import filedialog as fd
import os
from config import AppStyles as st
from torch import nn
from widget.dialog.graph_visualization import ImageDialog

class ImportSection:
    def __init__(self, master, comunication_section):
        self.master = master
        self.comunication_section = comunication_section
        
        # Main frame setup
        self.frame = ctk.CTkFrame(master)
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configure grid layout for the frame
        self.frame.grid_rowconfigure((0, 1, 2), weight=1)
        self.frame.grid_columnconfigure((0, 1), weight=1, uniform="column")
        
        # Section title label
        self.import_title_label = ctk.CTkLabel(self.frame, text="Import Files", font=st.HEADER_FONT)
        self.import_title_label.grid(row=0, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="nsew")
        
        # Import buttons for different file types
        self.import_model_button = ctk.CTkButton(self.frame, text="Import Model (.pth)", font=st.BUTTON_FONT, command=self.select_model_file, corner_radius=10)
        self.import_model_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.import_dataloader_button = ctk.CTkButton(self.frame, text="Import DataSet Loader (.py)", font=st.BUTTON_FONT, command=self.import_dataset, corner_radius=10)
        self.import_dataloader_button.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.import_modelclass_button = ctk.CTkButton(self.frame, text="Import ModelClass (.py)", font=st.BUTTON_FONT, command=self.select_modelclass_file, corner_radius=10)
        self.import_modelclass_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.import_dataset_button = ctk.CTkButton(self.frame, text="Import Data File (.csv)", font=st.BUTTON_FONT, command=self.import_datafile, corner_radius=10)
        self.import_dataset_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        # Frame for displaying selected files and removal buttons
        self.file_frame = ctk.CTkFrame(self.frame)
        self.file_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=(5,10), sticky="nsew")
        self.file_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.file_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Labels and remove buttons for selected files
        self.model_file_label = ctk.CTkLabel(self.file_frame, text="No Model selected", font=st.TEXT_FONT)
        self.model_file_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.model_remove_button = ctk.CTkButton(self.file_frame, text="X", command=self.remove_model_file, width=10, height=10, corner_radius=10)
        self.model_remove_button.grid(row=0, column=2, padx=(0, 10), pady=5, sticky="e")

        self.model_class_file_label = ctk.CTkLabel(self.file_frame, text="No Model Class File selected", font=st.TEXT_FONT)
        self.model_class_file_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.data_remove_button = ctk.CTkButton(self.file_frame, text="X", command=self.remove_model_class_file, width=10, height=10, corner_radius=10)
        self.data_remove_button.grid(row=1, column=2, padx=(0, 10), pady=5, sticky="e")
        
        self.dataset_file_label = ctk.CTkLabel(self.file_frame, text="No DataSet Loader selected", font=st.TEXT_FONT)
        self.dataset_file_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.dataset_remove_button = ctk.CTkButton(self.file_frame, text="X", command=self.remove_dataset_file, width=10, height=10, corner_radius=10)
        self.dataset_remove_button.grid(row=2, column=2, padx=(0, 10), pady=5, sticky="e")
        
        self.data_file_label = ctk.CTkLabel(self.file_frame, text="No Data File selected", font=st.TEXT_FONT)
        self.data_file_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.data_remove_button = ctk.CTkButton(self.file_frame, text="X", command=self.remove_data_file, width=10, height=10, corner_radius=10)
        self.data_remove_button.grid(row=3, column=2, padx=(0, 10), pady=5, sticky="e")
        
        # Button to visualize the neural network
        self.visualize_button = ctk.CTkButton(self.frame, text="Visualize Neural Network", font=st.BUTTON_FONT, command=self.visualize_model, corner_radius=10)
        self.visualize_button.grid(row=4, column=0, columnspan=2, padx=10, pady=(5,10), sticky="ew")
        
        # File path variables for storing selected file paths
        self.model_path = None
        self.dataset_file_path = None
        self.data_file_path = None
        self.model_class_path = None
        self.dropout_checkboxes = None

    # Function to select the model file (.pth)
    def select_model_file(self):
        filetypes = (
            ('Model files', '*.pth'),
        )

        filename = fd.askopenfilename(
            title='Select Model File',
            initialdir='.',
            filetypes=filetypes
        )
        
        if filename:
            self.model_path = filename
            self.model_file_label.configure(text=f"Model: {os.path.basename(filename)}", font=st.TEXT_FONT)

    # Function to select the ModelClass file (.py)
    def select_modelclass_file(self):
        filetypes = (
            ('ModelClass files', '*.py'),
        )

        filename = fd.askopenfilename(
            title='Select ModelClass File',
            initialdir='.',
            filetypes=filetypes
        )
        
        if filename:
            self.model_class_path = filename
            self.model_class_file_label.configure(text=f"ModelClass: {os.path.basename(filename)}", font=st.TEXT_FONT)

    # Function to import the dataset loader file (.py)
    def import_dataset(self):
        filetypes = (
            ('DataSet Loader files', '*.py'),
        )

        filename = fd.askopenfilename(
            title='Select DataSet Loader file',
            initialdir='.',
            filetypes=filetypes
        )
        
        if filename:
            self.dataset_file_path = filename
            self.dataset_file_label.configure(text=f"DataSet Loader: {os.path.basename(filename)}", font=st.TEXT_FONT)

    # Function to import the data file (.csv)
    def import_datafile(self):
        filetypes = (
            ('Data Files', '*.csv'),
        )

        filename = fd.askopenfilename(
            title='Select Data File',
            initialdir='.',
            filetypes=filetypes
        )
        
        if filename:
            self.data_file_path = filename
            self.data_file_label.configure(text=f"Data File: {os.path.basename(filename)}", font=st.TEXT_FONT)
    
    # Function to remove the selected model file
    def remove_model_file(self):
        self.model_path = None
        self.model_file_label.configure(text="No Model selected", font=st.TEXT_FONT)
        
    # Function to remove the selected ModelClass file
    def remove_model_class_file(self):
        self.model_class_path = None
        self.model_class_file_label.configure(text="No Model Class File selected", font=st.TEXT_FONT)
        
    # Function to remove the selected dataset loader file
    def remove_dataset_file(self):
        self.dataset_file_path = None
        self.dataset_file_label.configure(text="No DataSet Loader selected", font=st.TEXT_FONT)
        
    # Function to remove the selected data file
    def remove_data_file(self):
        self.data_file_path = None
        self.data_file_label.configure(text="No Data File selected", font=st.TEXT_FONT)
        
    # Function to retrieve the selected model file path
    def get_model_file(self):
        return self.model_path
    
    # Function to retrieve the selected ModelClass file path
    def get_modelclass_file(self):
        return self.model_class_path

    # Function to retrieve the selected dataset loader file path
    def get_dataset_file(self):
        return self.dataset_file_path

    # Function to retrieve the selected data file path
    def get_data_file(self):
        return self.data_file_path
    
    # Function to set the dropout checkboxes
    def set_dropout_checkboxes(self, checkboxes):
        self.dropout_checkboxes = checkboxes
        
    # Function to retrieve the dropout checkboxes
    def get_dropout_checkboxes(self):
        return self.dropout_checkboxes
        
    # Function to visualize the neural network model
    def visualize_model(self):
        
        if self.model_class_path is None:
            self.comunication_section.display_message("No ModelClass file selected", st.ERROR_COLOR)
            return
        
        self.comunication_section.display_message("Visualizing Neural Network", st.COMUNICATION_COLOR)
        
        model_to_visualize = self.validate_modelclass()
        
        if model_to_visualize is None:
            return
        
        layers = self.get_layers(model_to_visualize)
        model_sequence = self.destructure_model(model_to_visualize)
        
        if layers is None:
            self.comunication_section.display_message("No hidden layers found in the model", st.ERROR_COLOR)
            return

        image_dialog = ImageDialog(self.master, self, model_to_visualize(), layers, model_sequence)
        image_dialog.mainloop()

    # Function to validate the ModelClass file
    def validate_modelclass(self):
        try:
            spec = importlib.util.spec_from_file_location("ModelClassModule", self.model_class_path)
            if spec is None:
                self.comunication_section.display_message(f"Cannot find the file: {self.model_class_path}", st.ERROR_COLOR)
                return
            modelclass_module = importlib.util.module_from_spec(spec)
            if spec.loader is None:
                self.comunication_section.display_message(f"Cannot load the loader for the module: {self.model_class_path}", st.ERROR_COLOR)
                return
            spec.loader.exec_module(modelclass_module)
            
            if not hasattr(modelclass_module, "CustomModel"):
                self.comunication_section.display_message(f"CustomModel not found in the file: {self.model_class_path}", st.ERROR_COLOR)
                return
            
            return modelclass_module.CustomModel
        
        except Exception as e:
            self.comunication_section.display_message(f"Error loading the ModelClass file: {e}", st.ERROR_COLOR)
                

    # Function to get the hidden layers of the model
    def get_layers(self, model_class):
        try:
            if not callable(model_class):
                raise ValueError("model_class must be a callable class")
            
            model = model_class()
            hidden_layers = []

            def extract_layers(module):
                for _, child_module in module.named_children():
                    if isinstance(child_module, (nn.Linear, nn.Conv1d, nn.Conv2d, nn.Conv3d)):
                        hidden_layers.append(child_module)
                    elif isinstance(child_module, (nn.Sequential, nn.ModuleList, nn.ModuleDict)):
                        extract_layers(child_module)
            
            extract_layers(model)
            return hidden_layers
        
        except Exception as e:
            self.comunication_section.display_message(f"Error getting hidden layers: {e}", st.ERROR_COLOR)

    # Function to destructure the model into a sequence of layers
    def destructure_model(self, model_class):
        try:
            if not callable(model_class):
                raise ValueError("model_class must be a callable class")
            
            model = model_class()
            model_sequence = []

            def extract_layers(module):
                for _, child_module in module.named_children():
                    if isinstance(child_module, (nn.Sequential, nn.ModuleList, nn.ModuleDict)):
                        extract_layers(child_module)
                    else:
                        model_sequence.append(child_module)
            
            extract_layers(model)
            return model_sequence
        
        except Exception as e:
            self.comunication_section.display_message(f"Error getting model sequence: {e}", st.ERROR_COLOR)
