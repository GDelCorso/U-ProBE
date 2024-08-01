import os   
import customtkinter as ctk
from pages.uprobe_page import UprobePage

# Imposta il tema dell'applicazione
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("U-ProBE")
        self.geometry("1024x600")

        icon_path = os.path.join(os.path.dirname(__file__), "assets/icon.ico")
        self.iconbitmap(icon_path)

        # Configura la griglia principale
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Crea e posiziona l'istanza di InferencePage
        self.inference_page = UprobePage(self)
        self.inference_page.frame.grid(row=0, column=0, sticky="nsew")

        
app = App()
app.mainloop()
