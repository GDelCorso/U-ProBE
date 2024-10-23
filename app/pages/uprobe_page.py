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
        self.frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid layout for the frame
        self.frame.grid_rowconfigure(0, weight=1)  # Row for main content
        self.frame.grid_rowconfigure(1, weight=0)  # Row for communication section
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Content frame for sections
        self.content_frame = ctk.CTkFrame(self.frame)
        self.content_frame.grid(row=0, column=0, padx=10, pady=(10,0), sticky="nsew")
        self.content_frame.grid_rowconfigure((0, 1), weight=1)
        self.content_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Create sections
        self.comunication_section = CommunicationSection(self.frame)
        self.import_section = ImportSection(self.content_frame, self.comunication_section)
        self.plot_section = PlotSection(self.content_frame, self.comunication_section)
        self.model_evaluation_section = ModelEvaluationSection(self.content_frame, self.comunication_section)
        self.inference_section = InferenceSection(self.content_frame, self.import_section, self.model_evaluation_section, self.comunication_section, self.plot_section)
        
        # Position sections in the grid
        self.import_section.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.plot_section.frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.inference_section.frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.model_evaluation_section.frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Position communication section at the bottom
        self.comunication_section.frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,10))