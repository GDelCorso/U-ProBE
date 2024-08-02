import tkinter as tk
import customtkinter as ctk
from config import AppStyles as st  

class ResultsTable:
    def __init__(self, master):
        self.master = master
        self.data = None  # Initial data set to None

        # Create the main frame for displaying the table
        self.frame = ctk.CTkFrame(self.master, corner_radius=15, fg_color=st.CELL_BG)
        self.frame.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')
        
        # Create column headers
        tk.Label(self.frame, text="Methodologies", font=st.COLUMN_FONT, bg=st.HEADER_BG, fg=st.HEADER_FG).grid(row=0, column=0, sticky='nsew', padx=1, pady=1)
        tk.Label(self.frame, text="Ground Truth", font=st.COLUMN_FONT, bg=st.HEADER_BG, fg=st.HEADER_FG).grid(row=0, column=1, sticky='nsew', padx=1, pady=1)
        tk.Label(self.frame, text="Prediction", font=st.COLUMN_FONT, bg=st.HEADER_BG, fg=st.HEADER_FG).grid(row=0, column=2, sticky='nsew', padx=1, pady=1)
        
        # Configure the columns of the main frame
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)

        # Dictionary to store references to widgets
        self.labels = {
            "Methodologies": [],
            "Ground Truth": [],
            "Prediction": []
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
            self.labels["Ground Truth"].append(self.frame.grid_slaves(row=i, column=1)[0])
            self.labels["Prediction"].append(self.frame.grid_slaves(row=i, column=2)[0])
            
            # Configure row layout
            self.frame.grid_rowconfigure(i, weight=1)

    def update_table(self, inference_results):
        if inference_results is None or len(inference_results) != len(self.labels["Ground Truth"]):
            # Check if the number of results matches the number of rows
            return

        for i, (ground_truth, prediction) in enumerate(inference_results):
            # Update the "Ground Truth" and "Prediction" values for row i+1
            self.labels["Ground Truth"][i].config(text=ground_truth)
            self.labels["Prediction"][i].config(text=prediction)
