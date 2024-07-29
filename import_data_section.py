import customtkinter as ctk

class ImportDataSection:
    def __init__(self, master):
        self.frame = ctk.CTkFrame(master)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        self.label = ctk.CTkLabel(self.frame, text="Import Data")
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def create_widgets(self):
        self.import_dataloader_button = ctk.CTkButton(self.frame, text="Import DataLoader")
        self.import_dataloader_button.grid(row=1, column=0, pady=5, padx=10)
        self.import_dataset_button = ctk.CTkButton(self.frame, text="Import DataSet 'Test'")
        self.import_dataset_button.grid(row=2, column=0, pady=5, padx=10)
