import customtkinter as ctk
from config import AppStyles as st

class PlotsPlaceholder:
    def __init__(self, master):
        self.master = master
        self.frame = ctk.CTkFrame(self.master)
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Configure grid layout for the frame
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Label for placeholder text
        self.placeholder_label = ctk.CTkLabel(self.frame, text="Plots Placeholder", font=st.HEADER_FONT)
        self.placeholder_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
