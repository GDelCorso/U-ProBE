import customtkinter as ctk
from tkinter import filedialog as fd
import os

class ImportModelSection:
    def __init__(self, master):
        self.master = master
        self.frame = ctk.CTkFrame(master, corner_radius=15)
        self.frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self.frame, text="Import Model", font=("Arial", 24, "bold"))
        self.label.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="nsew")

        self.import_model_button = ctk.CTkButton(self.frame, text="Select Model File", command=self.select_file, 
                                                 corner_radius=10)
        self.import_model_button.grid(row=1, column=0, padx=20, pady=10)

        self.file_label = ctk.CTkLabel(self.frame, text="", font=("Arial", 14))
        self.file_label.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    def create_widgets(self):
        self.label.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="nsew")
        self.import_model_button.grid(row=1, column=0, padx=20, pady=10)
        self.file_label.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    def select_file(self):
        filetypes = (
            ('Model files', '*.pth'),
            ('All files', '*.*')
        )

        filename = fd.askopenfilename(
            title='Open a file',
            initialdir='.',
            filetypes=filetypes)
        
        if filename:
            self.file_label.configure(text=f"Selected file: {os.path.basename(filename)}")
            self.selected_file = filename