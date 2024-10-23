import customtkinter as ctk
from config import AppStyles as st
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors
import pandas as pd
from typing import Optional

class PlotSection:
    def __init__(self, master, communication_section):
        self.master = master
        self.frame = ctk.CTkFrame(self.master)
        self.communication_section = communication_section
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Main layout configuration
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        self.title_label = ctk.CTkLabel(self.frame, text="Results Plot", font=st.HEADER_FONT)
        self.title_label.grid(row=0, column=0, padx=5, pady=(5,0), sticky="nsew")
        
        # Frame for the plot
        self.plot_frame = ctk.CTkFrame(self.frame)
        self.plot_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        
        # Controls frame
        self.controls_frame = ctk.CTkFrame(self.frame)
        self.controls_frame.grid(row=2, column=0, padx=5, pady=(0,5), sticky="ew")
        
        # Configure grid for controls frame
        for i in range(5):
            self.controls_frame.grid_columnconfigure(i, weight=1)
        
        # Sample input
        self.sample_label = ctk.CTkLabel(self.controls_frame, text="Samples:", font=st.TEXT_FONT)
        self.sample_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.sample_entry = ctk.CTkEntry(self.controls_frame, width=80)
        self.sample_entry.grid(row=0, column=1, padx=5, pady=5)
        self.sample_entry.insert(0, "100")
        
        # MC-Dropout checkbox
        self.mc_dropout_var = ctk.BooleanVar(value=False)
        self.mc_dropout_cb = ctk.CTkCheckBox(self.controls_frame, text="MC-Dropout",
                                             variable=self.mc_dropout_var,
                                             command=self.update_visualization,
                                             font=st.TEXT_FONT)
        self.mc_dropout_cb.grid(row=0, column=2, padx=5, pady=5)
        
        # Trustscore checkbox
        self.trustscore_var = ctk.BooleanVar(value=False)
        self.trustscore_cb = ctk.CTkCheckBox(self.controls_frame, text="Trustscore",
                                             variable=self.trustscore_var,
                                             command=self.update_visualization,
                                             font=st.TEXT_FONT)
        self.trustscore_cb.grid(row=0, column=3, padx=5, pady=5)
        
        # Shuffle button
        self.shuffle_button = ctk.CTkButton(self.controls_frame, text="Shuffle", 
                                            command=self.shuffle_plot,
                                            font=st.BUTTON_FONT,
                                            width=100)
        self.shuffle_button.grid(row=0, column=4, padx=5, pady=5)
        
        # Reference to the results DataFrame and current sample
        self.results_df: Optional[pd.DataFrame] = None
        self.current_sample: Optional[pd.DataFrame] = None
        
        # Colormap for trustscore (red -> green)
        self.trust_colors = ['red', 'yellow', 'green']
        self.trust_cmap = mcolors.LinearSegmentedColormap.from_list('trust', self.trust_colors)
        
        # Create initial placeholder plot
        self.create_placeholder_plot()

    def create_placeholder_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.ax.set_title("Waiting for results...", pad=10)
        self.ax.set_xlabel("Ground Truth")
        self.ax.set_ylabel("Prediction")
        
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    def update_plot(self, results_df: pd.DataFrame):
        self.results_df = results_df
        self.shuffle_plot()  # Generate the first random sample

    def get_point_properties(self, row):
        base_size = 50
        size = base_size
        color = 'blue'
        alpha = 0.8  # Improve transparency for better visualization
        
        if self.mc_dropout_var.get():
            # MC-Dropout influences size (larger = less confident)
            dropout_score = row['MC-Dropout Score']
            # Adjusting scale to make size variation more visible
            size = base_size * (1 + (1 - dropout_score) * 4)  # Higher dropout score = smaller size
        
        if self.trustscore_var.get():
            # Trustscore influences color (greener = more reliable)
            normalized_trust = min(max(row['Trustscore'], 0), 1)  # Clamp between 0 and 1
            color = self.trust_cmap(normalized_trust)
            
        return size, color, alpha

    def update_visualization(self):
        if self.current_sample is None:
            return
            
        self.ax.clear()
        
        # Plot each point with its properties
        for _, row in self.current_sample.iterrows():
            size, color, alpha = self.get_point_properties(row)
            self.ax.scatter(row['GT'], row['No post-hoc method'], 
                            s=size, color=color, alpha=alpha)
        
        # Reference line y=x
        max_val = max(self.current_sample['GT'].max(), self.current_sample['No post-hoc method'].max())
        min_val = min(self.current_sample['GT'].min(), self.current_sample['No post-hoc method'].min())
        self.ax.plot([min_val, max_val], [min_val, max_val], 
                     'k--', alpha=0.5, label='Perfect Prediction')
        
        # Configure plot
        title = "GT vs Predictions"
        if self.mc_dropout_var.get() and self.trustscore_var.get():
            title += "\nSize: MC-Dropout (larger=less confident) • Color: Trustscore (green=better)"
        elif self.mc_dropout_var.get():
            title += "\nSize: MC-Dropout Score (larger=less confident)"
        elif self.trustscore_var.get():
            title += "\nColor: Trustscore (green=better)"
        title += f"\n({len(self.current_sample)} samples)"
        
        self.ax.set_title(title, pad=10)
        self.ax.set_xlabel("Ground Truth")
        self.ax.set_ylabel("Prediction")
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.legend(loc='upper left', fontsize='small')
        
        plt.tight_layout()
        self.canvas.draw()

    def shuffle_plot(self):
        if self.results_df is None:
            self.communication_section.display_message(
                "Error: No data available. Please run inference first."
            )
            return
        
        try:
            n_samples = int(self.sample_entry.get())
            if n_samples <= 0:
                raise ValueError("Number of samples must be positive")
        except ValueError as e:
            self.communication_section.display_message(
                f"Error: Invalid number of samples - {str(e)}"
            )
            return
            
        n_samples = min(n_samples, len(self.results_df))
        self.current_sample = self.results_df.sample(n=n_samples)
        self.update_visualization()

    def clear_plot(self):
        self.results_df = None
        self.current_sample = None
        self.create_placeholder_plot()
