import customtkinter as ctk
from config import AppStyles as st

class ModelEvaluationSection:
    def __init__(self, master, communication_section):
        self.master = master
        self.communication_section = communication_section
        self.stats = None
        
        # Main frame con padding
        self.frame = ctk.CTkFrame(self.master)
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        # Titolo della sezione
        self.title_label = ctk.CTkLabel(self.frame, text="Model Evaluation", font=st.HEADER_FONT)
        self.title_label.grid(row=0, column=0, columnspan=6, pady=10, sticky='nsew')
        
        self.stats_labels = {}
        self.stats_values = {}
        
        # Prima riga: Numero di test
        self.create_stat_row("Number of Tests", 1, 0, colspan=6)
        
        # Statistiche principali
        main_stats = [
            ("Accuracy", "F1 Score"),
            ("Recall", "Precision")
        ]
        
        for i, (left_stat, right_stat) in enumerate(main_stats, start=2):
            self.create_stat_row(left_stat, i, 0, colspan=3)
            self.create_stat_row(right_stat, i, 3, colspan=3)
        
        # Trustscore e MC-Dropout con distribuzioni (mediana, Q1, Q3)
        self.create_distribution_row("Trustscore", 4)
        self.create_distribution_row("MC-Dropout", 5)
        
        # Configura i pesi delle righe e colonne
        for i in range(6):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(6):
            self.frame.grid_columnconfigure(i, weight=1)

    def create_stat_row(self, label_text, row, col, colspan=3):
        # Container per ogni riga, con margini e colore di sfondo
        container = ctk.CTkFrame(self.frame)
        container.grid(row=row, column=col, columnspan=colspan, sticky='nsew', padx=5, pady=(0,3))
        
        # Etichetta (testo) con font prioritario
        label = ctk.CTkLabel(container, text=label_text, font=st.TEXT_FONT, anchor='w')
        label.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.stats_labels[label_text] = label
        
        # Valore (es. "N/A") con il font attuale
        value = ctk.CTkLabel(container, text="N/A", font=st.CELL_FONT, anchor='e')
        value.grid(row=0, column=1, sticky='e', padx=10, pady=5)
        self.stats_values[label_text] = value
        
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

    def create_distribution_row(self, stat_name, row):
        # Container per ogni riga con distribuzioni
        container = ctk.CTkFrame(self.frame)
        container.grid(row=row, column=0, columnspan=6, sticky='nsew', padx=5, pady=(0,3))

        # Etichette e valori con margine (padding)
        label = ctk.CTkLabel(container, text=f"{stat_name}", font=st.TEXT_FONT, anchor='w')
        label.grid(row=0, column=0, columnspan=2, sticky='w', padx=(10, 0), pady=5)
        
        median_label = ctk.CTkLabel(container, text="Median", font=st.TEXT_FONT, anchor='w')
        median_label.grid(row=0, column=2, sticky='w', padx=(10, 0), pady=5)
        
        median_value = ctk.CTkLabel(container, text="N/A", font=st.CELL_FONT, anchor='e')
        median_value.grid(row=0, column=2, sticky='e', padx=(0, 10), pady=5)
        self.stats_values[f"{stat_name} Median"] = median_value
        
        q1_label = ctk.CTkLabel(container, text="Q1", font=st.TEXT_FONT, anchor='w')
        q1_label.grid(row=0, column=3, sticky='w', padx=(10, 0), pady=5)
        
        q1_value = ctk.CTkLabel(container, text="N/A", font=st.CELL_FONT, anchor='e')
        q1_value.grid(row=0, column=3, sticky='e', padx=(0, 10), pady=5)
        self.stats_values[f"{stat_name} Q1"] = q1_value
        
        q3_label = ctk.CTkLabel(container, text="Q3", font=st.TEXT_FONT, anchor='w')
        q3_label.grid(row=0, column=4, sticky='w', padx=(10, 0), pady=5)
        
        q3_value = ctk.CTkLabel(container, text="N/A", font=st.CELL_FONT, anchor='e')
        q3_value.grid(row=0, column=4, sticky='e', padx=(0, 10), pady=5)
        self.stats_values[f"{stat_name} Q3"] = q3_value
        
        # Configurazione delle colonne del container
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_columnconfigure(2, weight=1)
        container.grid_columnconfigure(3, weight=1)
        container.grid_columnconfigure(4, weight=1)

    def update_stats(self, results_df, stats):
        self.stats = stats
        
        num_tests = len(results_df)
        self.stats_values["Number of Tests"].configure(text=str(num_tests))
        
        if "No post-hoc method" in stats:
            no_post_hoc_stats = stats["No post-hoc method"]
            self.stats_values["Accuracy"].configure(text=f"{no_post_hoc_stats['accuracy']:.4f}")
            self.stats_values["F1 Score"].configure(text=f"{no_post_hoc_stats['f1_score']:.4f}")
            self.stats_values["Recall"].configure(text=f"{no_post_hoc_stats['recall']:.4f}")
            self.stats_values["Precision"].configure(text=f"{no_post_hoc_stats['precision']:.4f}")
        
        if "Trustscore" in results_df.columns:
            trustscore_median = results_df["Trustscore"].median()
            trustscore_q1 = results_df["Trustscore"].quantile(0.25)
            trustscore_q3 = results_df["Trustscore"].quantile(0.75)
            self.stats_values["Trustscore Median"].configure(text=f"{trustscore_median:.4f}")
            self.stats_values["Trustscore Q1"].configure(text=f"{trustscore_q1:.4f}")
            self.stats_values["Trustscore Q3"].configure(text=f"{trustscore_q3:.4f}")
        
        if "MC-Dropout Score" in results_df.columns:
            mc_dropout_median = results_df["MC-Dropout Score"].median()
            mc_dropout_q1 = results_df["MC-Dropout Score"].quantile(0.25)
            mc_dropout_q3 = results_df["MC-Dropout Score"].quantile(0.75)
            self.stats_values["MC-Dropout Median"].configure(text=f"{mc_dropout_median:.4f}")
            self.stats_values["MC-Dropout Q1"].configure(text=f"{mc_dropout_q1:.4f}")
            self.stats_values["MC-Dropout Q3"].configure(text=f"{mc_dropout_q3:.4f}")

    def reset_stats(self):
        for value_label in self.stats_values.values():
            value_label.configure(text="N/A")
