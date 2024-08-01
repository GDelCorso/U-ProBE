import torch
import customtkinter as ctk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import AppStyles as st

class GraphVisualizer:
    def __init__(self, master, import_section):
        # Initialize main components and layout
        self.master = master
        self.import_section = import_section
        
        self.frame = ctk.CTkFrame(self.master)
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.frame.grid_rowconfigure((0, 1), weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Placeholder label for initial view
        self.placeholder_label = ctk.CTkLabel(self.frame, text="Graph Visualizer", font=st.HEADER_FONT)
        self.placeholder_label.grid(row=0, column=0, padx=10, pady=(0,10), sticky="nsew")
        
        # Button to visualize the model
        self.visualize_button = ctk.CTkButton(self.frame, text="Visualize Neural Network", command=self.visualize_model, font=st.BUTTON_FONT)
        self.visualize_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Frame for displaying the graph
        self.graph_frame = ctk.CTkFrame(self.frame)
        self.graph_frame.grid(row=2, column=0, padx=10, pady=(5,10), sticky="nsew")
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

    def visualize_model(self):
        # Load and visualize the model when the button is clicked
        model_path = self.import_section.get_model_file()
        if model_path is not None:
            model = self.load_model(model_path)
            if model:
                self.draw_graph(model)
            else:
                self.show_error("Unable to load the model.")
        else:
            self.show_error("No model selected.")

    def load_model(self, model_path):
        # Load the model from the given path
        try:
            model = torch.jit.load(model_path, map_location=torch.device('cpu'))
            return model
        except Exception as e:
            self.show_error(f"Error: {e}")
            
    def draw_graph(self, model):
        # Placeholder method for drawing the model graph
        pass

    def show_error(self, message):
        # Display an error message
        error_label = ctk.CTkLabel(self.frame, text=message, font=st.STATUS_FONT, text_color=st.ERROR_COLOR)
        error_label.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        self.frame.grid_rowconfigure(3, weight=1)
