import customtkinter as ctk
from ui_elements import ScrollableCheckBoxFrame

class HomePage:
    def __init__(self, master):
        self.master = master
        self.master.grid_rowconfigure((0, 2, 3), weight=0)
        self.master.grid_rowconfigure((1, 4), weight=1)
        self.master.grid_columnconfigure((0, 1), weight=1)

    def show_home(self):
        self.initial_text = ctk.CTkLabel(self.master, text="Seleziona gli elementi che preferisci", font=("Arial", 20))
        self.initial_text.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        values1 = ["Capra", "Toro", "Bue", "Asino", "Cammello", "Cavallo", "Cinghiale", "Daino", "Gatto", "Lepre", "Maiale", "Mucca", "Pecora", "Pony", "Renna", "Scrofa", "Tasso", "Tigre", "Topo", "Zebra"]
        self.scrollable_checkbox_frame_1 = ScrollableCheckBoxFrame(self.master, "Animali", values1)
        self.scrollable_checkbox_frame_1.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")

        values2 = ["Prosciutto", "Salame", "Mortadella", "Coppa", "Speck"]
        self.scrollable_checkbox_frame_2 = ScrollableCheckBoxFrame(self.master, "Salumi", values2)
        self.scrollable_checkbox_frame_2.grid(row=1, column=1, padx=(0, 10), pady=(10, 0), sticky="nsew")

        self.button1 = ctk.CTkButton(self.master, text="Selezionati nell'insieme 1?", command=self.button_callback_column1)
        self.button1.grid(row=2, column=0, padx=10, pady=10, sticky="nwes")

        self.button2 = ctk.CTkButton(self.master, text="Selezionati nell'insieme 2?", command=self.button_callback_column_2)
        self.button2.grid(row=2, column=1, padx=10, pady=10, sticky="nwse")

        self.button_both = ctk.CTkButton(self.master, text="Quali sono i selezionati totali?", command=self.button_callback_both)
        self.button_both.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nwes")

        self.result_textbox = ctk.CTkTextbox(self.master, height=15, width=80)
        self.result_textbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def button_callback_column1(self):
        selected_items = self.scrollable_checkbox_frame_1.get()
        result = "Insieme 1: " + ", ".join(selected_items) if selected_items else "Insieme 1: empty"
        self.update_result_textbox(result)

    def button_callback_column_2(self):
        selected_items = self.scrollable_checkbox_frame_2.get()
        result = "Insieme 2: " + ", ".join(selected_items) if selected_items else "Insieme 2: empty"
        self.update_result_textbox(result)

    def button_callback_both(self):
        selected_items = self.scrollable_checkbox_frame_1.get() + self.scrollable_checkbox_frame_2.get()
        result = "Totale: " + ", ".join(selected_items) if selected_items else "Totale: empty"
        self.update_result_textbox(result)

    def update_result_textbox(self, result):
        self.result_textbox.insert("end", result + "\n")
        self.result_textbox.yview("end")
