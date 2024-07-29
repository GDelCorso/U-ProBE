import customtkinter as ctk

class PostHocMethodsSection:
    def __init__(self, master):
        self.master = master  # Salva il master come attributo dell'istanza
        
        # Crea un frame per contenere i widget
        self.frame = ctk.CTkFrame(self.master)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Etichetta di intestazione con uno stile elegante
        self.label = ctk.CTkLabel(self.frame, text="Post-Hoc Methods", font=("Arial", 18, "bold"))
        self.label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="nsew")

    def create_widgets(self):
        # Lista di opzioni con checkbox
        options = [
            "Trustscore",
            "MC-Dropout",
            "Topological data analysis",
            "Ensemble",
            "Few shot learning"
        ]
        
        # Crea checkbox e aggiungili al frame
        for idx, option in enumerate(options):
            checkbox = ctk.CTkCheckBox(self.frame, text=option, font=("Arial", 14))
            checkbox.grid(row=idx + 1, column=0, pady=8, padx=15, sticky="w")

    def show(self):
        self.frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")