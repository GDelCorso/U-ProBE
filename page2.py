import customtkinter as ctk

class Page2:
    def __init__(self, master):
        self.master = master
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

    def show_page2(self):
        label = ctk.CTkLabel(self.master, text="Questa è la Pagina 2")
        label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
