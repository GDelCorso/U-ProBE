import customtkinter as ctk
from widget.import_widget import ImportSection
from widget.plot_widget import PlotSection
from widget.model_evaluation_widget import ModelEvaluationSection
from widget.inference_widget import InferenceSection
from widget.comunication_widget import CommunicationSection

class UprobePage:
    def __init__(self, master):
        self.master = master
        
        # Main frame for the inference page
        self.frame = ctk.CTkFrame(self.master)
        self.frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        
        # Configure grid layout for the frame
        self.frame.grid_rowconfigure((0, 1), weight=1)
        self.frame.grid_columnconfigure((0, 1), weight=1)
        
        # Create sections
        self.comunication_section = CommunicationSection(self.master)
        self.import_section = ImportSection(self.frame, self.comunication_section)
        self.plot_section = PlotSection(self.frame, self.comunication_section)
        self.model_evaluation_section = ModelEvaluationSection(self.frame, self.comunication_section) 
        self.inference_section = InferenceSection(self.frame, self.import_section, self.model_evaluation_section, self.comunication_section, self.plot_section)  

        # Position sections in the grid
        self.import_section.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.plot_section.frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.inference_section.frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.model_evaluation_section.frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")        
        self.comunication_section.message_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
