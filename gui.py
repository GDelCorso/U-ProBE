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
        
        self.title("U-ProBE")
        self.geometry("1024x600")
        self.grid_rowconfigure(0, weight=0)  
        self.grid_rowconfigure(1, weight=1)  
        self.grid_rowconfigure(2, weight=0)  
        self.grid_rowconfigure(3, weight=0)  
        self.grid_rowconfigure(4, weight=1)  
        self.grid_columnconfigure(0, weight=1)  
        self.grid_columnconfigure(1, weight=1)
        
        self.iconbitmap("icon.ico")  # Imposta l'icona dell'applicazione
        
        self.headerbutton = ctk.CTkButton(self, text="Home", command=self.show_home)
        self.headerbutton.grid(row=0, column=0,columnspan=2, padx=10, pady=10, sticky="nsew")

        # Creazione e posizionamento del primo frame scrollabile con checkbox
        values1 = ["Capra", "Toro", "Bue", "Asino", "Cammello", "Cavallo", "Cinghiale", "Daino", "Gatto", "Lepre", "Maiale", "Mucca", "Pecora", "Pony", "Renna", "Scrofa", "Tasso", "Tigre", "Topo", "Zebra"]
        self.scrollable_checkbox_frame_1 = ScrollableCheckBoxFrame(self, "Animali", values1)
        self.scrollable_checkbox_frame_1.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")
        
        # Creazione e posizionamento del secondo frame scrollabile con checkbox
        values2 = ["Prosciutto", "Salame", "Mortadella", "Coppa", "Speck"]
        self.scrollable_checkbox_frame_2 = ScrollableCheckBoxFrame(self, "Salumi", values2)
        self.scrollable_checkbox_frame_2.grid(row=1, column=1, padx=(0, 10), pady=(10, 0), sticky="nsew")
        
        # Creazione e posizionamento dei pulsanti
        self.button1 = ctk.CTkButton(self, text="Selezionati nell'insieme 1?", command=self.button_callback_column1)
        self.button1.grid(row=2, column=0, padx=10, pady=10, sticky="nwes")
        
        self.button2 = ctk.CTkButton(self, text="Selezionati nell'insieme 2?", command=self.button_callback_column_2)
        self.button2.grid(row=2, column=1, padx=10, pady=10, sticky="nwse")
        
        self.button_both = ctk.CTkButton(self, text="Quali sono i selezionati totali?", command=self.button_callback_both)
        self.button_both.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nwes")
        
        # Creazione e posizionamento della textbox per lo storico
        self.result_textbox = ctk.CTkTextbox(self, height=15, width=80)
        self.result_textbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.grid_rowconfigure(4, weight=3)  # Imposta il peso della riga per espandersi

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
    
    def show_home(self):
        pass

# Crea e avvia l'applicazione
app = App()
app.mainloop()
