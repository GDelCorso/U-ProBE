import customtkinter as ctk

class InferenceExportSection:
    def __init__(self, master):
        self.frame = ctk.CTkFrame(master)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.label = ctk.CTkLabel(self.frame, text="Export")
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def create_widgets(self):
        self.inference_button = ctk.CTkButton(self.frame, text="Inference")
        self.inference_button.grid(row=1, column=0, pady=10, padx=10)
        self.export_button = ctk.CTkButton(self.frame, text="Export .csv")
        self.export_button.grid(row=2, column=0, pady=10, padx=10)
