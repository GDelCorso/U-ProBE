import os
import customtkinter as ctk
import tkinterdnd2 as tkdnd
from ui_elements import ScrollableCheckBoxFrame
from home_page import HomePage
from page2 import Page2

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
        self.page2_tab = self.tabview.add("Blank")

        self.home_page = HomePage(self.home_tab)
        self.page2 = Page2(self.page2_tab)

        self.show_home()

    def show_home(self):
        self.home_page.show_home()

    def show_page2(self):
        self.page2.show_page2()

# Crea e avvia l'applicazione
app = App()
app.mainloop()
