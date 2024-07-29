import customtkinter as ctk

class PostHocMethodsSection:

    def __init__(self, master):
        self.frame = ctk.CTkFrame(master)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        self.label = ctk.CTkLabel(self.frame, text="Post-Hoc Methods")
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def create_widgets(self):
        self.trustscore_checkbox = ctk.CTkCheckBox(self.frame, text="Trustscore")
        self.trustscore_checkbox.grid(row=1, column=0, pady=5, padx=10)
        self.mc_dropout_checkbox = ctk.CTkCheckBox(self.frame, text="MC-Dropout")
        self.mc_dropout_checkbox.grid(row=2, column=0, pady=5, padx=10)
        self.topological_data_checkbox = ctk.CTkCheckBox(self.frame, text="Topological data analysis")
        self.topological_data_checkbox.grid(row=3, column=0, pady=5, padx=10)
        self.ensemble_checkbox = ctk.CTkCheckBox(self.frame, text="Ensemble")
        self.ensemble_checkbox.grid(row=4, column=0, pady=5, padx=10)
        self.few_shot_learning_checkbox = ctk.CTkCheckBox(self.frame, text="Few shot learning")
        self.few_shot_learning_checkbox.grid(row=5, column=0, pady=5, padx=10)
