import os
import customtkinter as ctk
from home_page import HomePage
from inference_page import InferencePage

# Imposta il tema dell'applicazione
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("U-ProBE")
        self.geometry("1024x600")

        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        self.iconbitmap(icon_path)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.home_tab = self.tabview.add("Home")
        self.inference_page_tab = self.tabview.add("Inference Page")

        self.home_page = HomePage(self.home_tab)
        self.inference_page = InferencePage(self.inference_page_tab)

        self.show_home()

    def show_home(self):
        self.home_page.show_home()

    def show_inferencepage(self):
        self.inference_page.show_inference_page()

# Crea e avvia l'applicazione
app = App()
app.mainloop()
