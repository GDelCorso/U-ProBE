import os
import customtkinter as ctk

# Imposta il tema dell'applicazione
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")

# Definizione della classe per il frame scrollabile con checkbox
class ScrollableCheckBoxFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, title, values):
        super().__init__(master, label_text=title)
        self.grid_columnconfigure(0, weight=1)  # Configura la colonna per espandersi
        self.values = values
        self.checkboxes = []
        
        # Crea una checkbox per ogni valore
        for i, value in enumerate(self.values):
            checkbox = ctk.CTkCheckBox(self, text=value)
            checkbox.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.checkboxes.append(checkbox)

    # Metodo per ottenere le checkbox selezionate
    def get(self):
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.append(checkbox.cget("text"))
        return checked_checkboxes
    

# Definizione della classe principale dell'applicazione
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("App con Header e Pagine")
        self.geometry("1024x600")
        
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        self.iconbitmap(icon_path)

        # Configura la griglia per l'intero layout
        self.grid_rowconfigure(0, weight=1)  
        self.grid_columnconfigure(0, weight=1)
        
        # Tabview per la navigazione delle pagine
        self.tabview = ctk.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.home_tab = self.tabview.add("Home")        
        # Configura le griglie della tab Home
        self.home_tab.grid_rowconfigure((0, 2, 3), weight=0)
        self.home_tab.grid_rowconfigure((1, 4), weight=1)
        self.home_tab.grid_columnconfigure((0, 1), weight=1)
        
        self.page2_tab = self.tabview.add("Blank")
        # Configura le griglie della tab Blank
        self.page2_tab.grid_rowconfigure(0, weight=1)
        self.page2_tab.grid_columnconfigure(0, weight=1)
        
        # Mostra la home di default
        self.show_home()

    # Metodo per mostrare la home
    def show_home(self):
        
        self.initial_text = ctk.CTkLabel(self.home_tab, text="Seleziona gli elementi che preferisci", font=("Arial", 20))
        self.initial_text.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        # Creazione e posizionamento del primo frame scrollabile con checkbox
        values1 = ["Capra", "Toro", "Bue", "Asino", "Cammello", "Cavallo", "Cinghiale", "Daino", "Gatto", "Lepre", "Maiale", "Mucca", "Pecora", "Pony", "Renna", "Scrofa", "Tasso", "Tigre", "Topo", "Zebra"]
        self.scrollable_checkbox_frame_1 = ScrollableCheckBoxFrame(self.home_tab, "Animali", values1)
        self.scrollable_checkbox_frame_1.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")
        
        # Creazione e posizionamento del secondo frame scrollabile con checkbox
        values2 = ["Prosciutto", "Salame", "Mortadella", "Coppa", "Speck"]
        self.scrollable_checkbox_frame_2 = ScrollableCheckBoxFrame(self.home_tab, "Salumi", values2)
        self.scrollable_checkbox_frame_2.grid(row=1, column=1, padx=(0, 10), pady=(10, 0), sticky="nsew")
        
        # Creazione e posizionamento dei pulsanti
        self.button1 = ctk.CTkButton(self.home_tab, text="Selezionati nell'insieme 1?", command=self.button_callback_column1)
        self.button1.grid(row=2, column=0, padx=10, pady=10, sticky="nwes")
        
        self.button2 = ctk.CTkButton(self.home_tab, text="Selezionati nell'insieme 2?", command=self.button_callback_column_2)
        self.button2.grid(row=2, column=1, padx=10, pady=10, sticky="nwse")
        
        self.button_both = ctk.CTkButton(self.home_tab, text="Quali sono i selezionati totali?", command=self.button_callback_both)
        self.button_both.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nwes")
        
        # Creazione e posizionamento della textbox per lo storico
        self.result_textbox = ctk.CTkTextbox(self.home_tab, height=15, width=80)
        self.result_textbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.home_tab.grid_rowconfigure(4, weight=1)  # Imposta il peso della riga per espandersi
        
    # Metodo per mostrare la pagina 2
    def show_page2(self):
        label = ctk.CTkLabel(self.page2_tab, text="Questa è la Pagina 2")
        label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Callback per il pulsante del primo insieme
    def button_callback_column1(self):
        selected_items = self.scrollable_checkbox_frame_1.get()
        if not selected_items:
            result = "Insieme 1: empty"
        else:
            result = "Insieme 1: " + ", ".join(selected_items)
        self.update_result_textbox(result)
    
    # Callback per il pulsante del secondo insieme
    def button_callback_column_2(self):
        selected_items = self.scrollable_checkbox_frame_2.get()
        if not selected_items:
            result = "Insieme 2: empty"
        else:
            result = "Insieme 2: " + ", ".join(selected_items)
        self.update_result_textbox(result)
    
    # Callback per il pulsante che mostra i selezionati totali
    def button_callback_both(self):
        selected_items = self.scrollable_checkbox_frame_1.get() + self.scrollable_checkbox_frame_2.get()
        if not selected_items:
            result = "Totale: empty"
        else:
            result = "Totale: " + ", ".join(selected_items)
        self.update_result_textbox(result)
    
    # Metodo per aggiornare la textbox con il nuovo risultato
    def update_result_textbox(self, result):
        # Inserisci il risultato nella textbox
        self.result_textbox.insert("end", result + "\n")
        # Scorri alla fine della textbox per mostrare l'ultimo risultato
        self.result_textbox.yview("end")

# Crea e avvia l'applicazione
app = App()
app.mainloop()
