import torch
import customtkinter as ctk
import visualtorch
from widget.dialog_image import ImageDialog 
from config import AppStyles as st

class GraphVisualizer:
    def __init__(self, master, import_section):
        # Initialize main components and layout
        self.master = master
        self.import_section = import_section
        
        self.frame = ctk.CTkFrame(self.master)
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.frame.grid_rowconfigure((0, 1), weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Placeholder label for initial view
        self.placeholder_label = ctk.CTkLabel(self.frame, text="Graph Visualizer", font=st.HEADER_FONT)
        self.placeholder_label.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Button to visualize the model
        self.visualize_button = ctk.CTkButton(self.frame, text="Visualize Neural Network", command=self.visualize_model, font=st.BUTTON_FONT)
        self.visualize_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Label for displaying error messages, initially empty
        self.error_label = ctk.CTkLabel(self.frame, text="", font=st.STATUS_FONT, text_color=st.ERROR_COLOR)
        self.error_label.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.frame.grid_rowconfigure(2, weight=0)  # Set weight to 0 so it doesn't take much space initially

        # Attribute to hold the image reference
        self.ctk_image = None

    def visualize_model(self):
        # Load and visualize the model when the button is clicked
        model_path = self.import_section.get_model_file()
        if model_path is not None:
            model = self.load_model(model_path)
            if model:
                self.show_image_dialog(model)
            else:
                self.show_error("Unable to load the model.")
        else:
            self.show_error("No model selected.")

    def load_model(self, model_path):
        # Load the model from the given path
        try:
            model = torch.jit.load(model_path, map_location=torch.device('cpu'))
            return model
        except Exception as e:
            self.show_error(f"Error: {e}")
            return None
            
    def show_image_dialog(self, model):
        # Visualize the model architecture and get the image
        first_parameter = next(model.parameters())
        input_shape = first_parameter.size()
        img = visualtorch.graph_view(model, input_shape)
        
        # Create and open the image dialog directly with the image object
        dialog = ImageDialog(self.master, img) 
        dialog.mainloop()

    def show_error(self, message):
        # Display an error message and ensure it does not take up too much space
        self.error_label.configure(text=message)
        self.frame.grid_rowconfigure(2, weight=0)  # Ensure the error label row doesn't grow
