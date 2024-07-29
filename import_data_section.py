import customtkinter as ctk
from tkinter import filedialog as fd
import os

class ImportDataSection:
    def __init__(self, master):
        self.master = master
        self.frame = ctk.CTkFrame(master, corner_radius=15)
        self.frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # Label with the section title
        self.label = ctk.CTkLabel(self.frame, text="Import Data", font=("Arial", 24, "bold"))
        self.label.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="nsew")

        # Placeholder for file paths
        self.dataloader_file_path = None
        self.dataset_file_path = None

    def create_widgets(self):
        # Import DataLoader button
        self.import_dataloader_button = ctk.CTkButton(self.frame, text="Import DataLoader", corner_radius=10, command=self.import_dataloader)
        self.import_dataloader_button.grid(row=1, column=0, padx=20, pady=10)

        # Import DataSet button
        self.import_dataset_button = ctk.CTkButton(self.frame, text="Import DataSet 'Test'", corner_radius=10, command=self.import_dataset)
        self.import_dataset_button.grid(row=2, column=0, padx=20, pady=10)

    def import_dataloader(self):
        filetypes = (
            ('DataLoader files', '*.py'),
            ('All files', '*.*')
        )

        filename = fd.askopenfilename(
            title='Select DataLoader file',
            initialdir='.',
            filetypes=filetypes
        )
        
        if filename:
            self.dataloader_file_path = filename
            print(f"DataLoader file selected: {os.path.basename(filename)}")
            # Here you can add further processing for the DataLoader file

    def import_dataset(self):
        filetypes = (
            ('DataSet files', '*.csv'),
            ('All files', '*.*')
        )

        filename = fd.askopenfilename(
            title='Select DataSet file',
            initialdir='.',
            filetypes=filetypes
        )
        
        if filename:
            self.dataset_file_path = filename
            print(f"DataSet file selected: {os.path.basename(filename)}")

