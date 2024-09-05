import tkinter as tk
import customtkinter as ctk
from config import AppStyles as st  

class ResultsTable:
    def __init__(self, master, comunication_section):
        self.master = master
        self.data = None  # Initial data set to None
        self.comunication_section = comunication_section

        # Create the main frame for displaying the table
        self.frame = ctk.CTkFrame(self.master, corner_radius=15, fg_color=st.CELL_BG)
        self.frame.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

        # Create column headers with generic names
        self.methodology_label = tk.Label(self.frame, text="Methodologies", font=st.COLUMN_FONT, bg=st.HEADER_BG, fg=st.HEADER_FG)
        self.methodology_label.grid(row=0, column=0, sticky='nsew', padx=1, pady=1)

        self.metric1_label = tk.Label(self.frame, text="Metric 1", font=st.COLUMN_FONT, bg=st.HEADER_BG, fg=st.HEADER_FG)
        self.metric1_label.grid(row=0, column=1, sticky='nsew', padx=1, pady=1)

        self.metric2_label = tk.Label(self.frame, text="Metric 2", font=st.COLUMN_FONT, bg=st.HEADER_BG, fg=st.HEADER_FG)
        self.metric2_label.grid(row=0, column=2, sticky='nsew', padx=1, pady=1)

        # Configure the columns of the main frame
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)

        # Dictionary to store references to widgets
        self.labels = {
            "Methodologies": [],
            "Metric 1": [],
            "Metric 2": []
        }
        
        self.init_table()

    def init_table(self):
        # Initial data (null values) to display
        methodologies = [
            "No method",
            "Trustscore",
            "MC-Dropout",
            "Topological data analysis",
            "Ensemble",
            "Few shot learning"
        ]
        
        empty_value = "N/A"  # Value to display before inference is run
        
        for i, method in enumerate(methodologies, start=1):
            tk.Label(self.frame, text=method, font=st.CELL_FONT, bg=st.CELL_BG, fg=st.CELL_FG).grid(row=i, column=0, sticky='nsew', padx=1, pady=1)
            tk.Label(self.frame, text=empty_value, font=st.CELL_FONT, bg=st.CELL_BG, fg=st.CELL_FG).grid(row=i, column=1, sticky='nsew', padx=1, pady=1)
            tk.Label(self.frame, text=empty_value, font=st.CELL_FONT, bg=st.CELL_BG, fg=st.CELL_FG).grid(row=i, column=2, sticky='nsew', padx=1, pady=1)
            
            # Store references to the widgets
            self.labels["Methodologies"].append(self.frame.grid_slaves(row=i, column=0)[0])
            self.labels["Metric 1"].append(self.frame.grid_slaves(row=i, column=1)[0])
            self.labels["Metric 2"].append(self.frame.grid_slaves(row=i, column=2)[0])
            
            # Configure row layout
            self.frame.grid_rowconfigure(i, weight=1)

    def update_table(self, inference_results, inference_type):
        if inference_results is None or len(inference_results) != len(self.labels["Metric 1"]):
            # Check if the number of results matches the number of rows
            return

        # Check if the result type is accuracy (classification) or MSE (regression)
        if inference_type == 'classification':
            self.metric1_label.config(text="Accuracy")
            self.metric2_label.config(text="F1 Score")
        elif inference_type == 'regression':
            self.metric1_label.config(text="MSE")
            self.metric2_label.config(text="R² Score")
        
        # Update the table rows with inference results
        for i, (val1, val2) in enumerate(inference_results):
            self.labels["Metric 1"][i].config(text=val1)
            self.labels["Metric 2"][i].config(text=val2)
