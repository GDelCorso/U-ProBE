import customtkinter as ctk
from PIL import Image
import os
import random
from config import AppStyles as st
import visualtorch
import torch as th

class ImageDialog(ctk.CTkToplevel):
    def __init__(self, master, model, hidden_layers):
        
        super().__init__(master)
        self.title("Model Graph")
        
        
        icon_path = os.path.join(os.path.dirname(__file__), "../../../assets/icon.ico")
        self.after(250, lambda: self.iconbitmap(icon_path))
        

        image = visualtorch.graph_view(model, input_shape=(1, 3))
        self.loaded_img = image
        self.max_width = 1920
        self.max_height = 1080
        
        self.num_hidden_layers = len(hidden_layers)
        
        self.resize_image()
        self.create_widgets()
        self.configure_grid()
        self.set_geometry()
        
        self.lift()
        self.grab_set()
        self.minsize(400, 300)



    def resize_image(self):
        img_width, img_height = self.loaded_img.size
        aspect_ratio = img_width / img_height

        if img_width > self.max_width or img_height > self.max_height:
            if aspect_ratio > 1:
                new_width = self.max_width
                new_height = int(self.max_width / aspect_ratio)
            else:
                new_height = self.max_height
                new_width = int(self.max_height * aspect_ratio)
            
            self.loaded_img = self.loaded_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        self.image_ctk = ctk.CTkImage(light_image=self.loaded_img, dark_image=self.loaded_img, size=self.loaded_img.size)

    def create_widgets(self):
        # Titolo principale
        self.title_label = ctk.CTkLabel(self, text="Graph Visualizer", font=st.HEADER_FONT)
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.image_label = ctk.CTkLabel(self.main_frame, image=self.image_ctk)
        self.image_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        
        # Titolo per le checkbox
        self.checkbox_title_label = ctk.CTkLabel(self.main_frame, text="Dropout Layers", font=st.COLUMN_FONT)
        self.checkbox_title_label.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="nsew")
        
        self.checkbox_frame = ctk.CTkFrame(self.main_frame)
        self.checkbox_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.checkboxes = []
        for i in range(self.num_hidden_layers):
            layer_frame = ctk.CTkFrame(self.checkbox_frame, border_width=1)
            layer_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            
            # Configure the layout of the layer_frame
            layer_frame.columnconfigure(0, weight=0)
            layer_frame.columnconfigure(1, weight=1)
            layer_frame.rowconfigure(0, weight=1)
            layer_frame.rowconfigure(1, weight=1)
            
            checkbox = ctk.CTkCheckBox(layer_frame, text="")
            checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            
            layer_label = ctk.CTkLabel(layer_frame, text=f"Layer {i + 1}", font=st.TEXT_FONT)
            layer_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

            # Randomly decide whether to show "Dropout in Training"
            show_dropout = random.choice([True, False])
            if show_dropout:
                dropout_label = ctk.CTkLabel(layer_frame, text="Dropout in Training", font=st.TEXT_FONT)
                dropout_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="we")
                checkbox.select()
            else:
                # Placeholder to keep layout consistent
                dropout_label = ctk.CTkLabel(layer_frame, text="", font=st.TEXT_FONT)
                dropout_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="we")

            self.checkboxes.append(checkbox)

        self.close_button = ctk.CTkButton(self.main_frame, text="Close", command=self.destroy, font=st.BUTTON_FONT)
        self.close_button.grid(row=3, column=0, pady=(10, 0), sticky="ew")

    def configure_grid(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.checkbox_frame.grid_rowconfigure(0, weight=1)
        if(self.num_hidden_layers > 0):
            self.checkbox_frame.grid_columnconfigure(tuple(range(self.num_hidden_layers)), weight=1)

    def set_geometry(self):
        self.geometry(f"{min(self.loaded_img.width + 40, self.max_width)}x{min(self.loaded_img.height + 250, self.max_height)}")
        
