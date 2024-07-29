import customtkinter as ctk

class ImportModelSection:
    def __init__(self, master):
        self.frame = ctk.CTkFrame(master)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        self.label = ctk.CTkLabel(self.frame, text="Import Model")
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
    def create_widgets(self):
        self.import_model_button = ctk.CTkButton(self.frame, text="Import Model")
        self.import_model_button.grid(row=1, column=0, pady=10, padx=10)
