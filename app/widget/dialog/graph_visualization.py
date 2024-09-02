from collections import defaultdict
import customtkinter as ctk
from PIL import Image
import os
import random
from config import AppStyles as st
import visualtorch
from torch import nn

class ImageDialog(ctk.CTkToplevel):
    def __init__(self, master, model, layers, model_sequence):
        super().__init__(master)
        self.title("Model Graph")
        
        icon_path = os.path.join(os.path.dirname(__file__), "../../../assets/icon.ico")
        self.after(250, lambda: self.iconbitmap(icon_path))
        
        self.max_width = 1920
        self.max_height = 1080
                
        self.model = model
        self.input_layer = layers[0]
        self.hidden_layers = layers[1:]
        self.num_hidden_layers = len(self.hidden_layers)
        self.model_sequence = model_sequence

        self.batch_size = 4
        self.input_shape = (self.batch_size, 3, 224, 224)
        
        self.create_widgets()
        self.configure_grid()
        
        self.lift()
        self.grab_set()
        self.minsize(720, 420)

    def resize_image(self):
        img_width, img_height = self.loaded_img.size
        aspect_ratio = img_width / img_height

        max_img_width = self.max_width - 40
        max_img_height = self.max_height - 200

        if aspect_ratio > 1:
            new_width = min(img_width, max_img_width)
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = min(img_height, max_img_height)
            new_width = int(new_height * aspect_ratio)

        self.loaded_img = self.loaded_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.image_ctk = ctk.CTkImage(light_image=self.loaded_img, dark_image=self.loaded_img, size=self.loaded_img.size)

    def create_widgets(self):
        # Titolo principale
        self.title_label = ctk.CTkLabel(self, text="Graph Visualizer", font=st.HEADER_FONT)
        self.title_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        if not self.try_inference_graph():
            # Etichetta iniziale che mostra il testo
            self.image_label = ctk.CTkLabel(self.main_frame, text="Insert input shape to visualize model", font=st.HEADER_FONT, width=400, height=280)
            self.image_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
            
            # Frame contenente input e bottone
            self.input_button_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
            self.input_button_frame.grid(row=1, column=0, padx=10, pady=5, sticky="n")
            
            self.input_shape_entry = ctk.CTkEntry(self.input_button_frame, placeholder_text="3, 224, 224")
            self.input_shape_entry.grid(row=0, column=0, padx=5, pady=5)
            
            self.update_button = ctk.CTkButton(self.input_button_frame, text="Show Graph", command=self.show_graph_from_button, font=st.BUTTON_FONT)
            self.update_button.grid(row=0, column=1, padx=5, pady=5)

            # Zona di testo per l'errore
            self.error_label = ctk.CTkLabel(self.main_frame, text="", font=st.STATUS_FONT, text_color=st.ERROR_COLOR)
            self.error_label.grid(row=2, column=0, padx=10, pady=5, sticky="n")
        
        # Titolo per le checkbox
        self.checkbox_title_label = ctk.CTkLabel(self.main_frame, text="Dropout Layers", font=st.COLUMN_FONT)
        self.checkbox_title_label.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        
        self.checkbox_frame = ctk.CTkFrame(self.main_frame)
        self.checkbox_frame.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        
        self.close_button = ctk.CTkButton(self, text="Close", command=self.destroy, font=st.BUTTON_FONT)
        self.close_button.grid(row=2, column=0, pady=(5,10), padx=10, sticky="sew")

    def set_checkboxes(self):
        self.checkboxes = []
        max_columns = 4  # Numero massimo di colonne per le checkbox
        num_rows = (self.num_hidden_layers + max_columns - 1) // max_columns  # Calcola il numero di righe necessarie

        # Configura la griglia per avere le colonne e righe necessarie
        for r in range(num_rows):
            self.checkbox_frame.grid_rowconfigure(r, weight=1)
        for c in range(max_columns):
            self.checkbox_frame.grid_columnconfigure(c, weight=1)
            
        
        aux_model_layers = self.model_sequence[1:]
        while aux_model_layers and str(aux_model_layers[0]) != str(self.hidden_layers[0]):
            aux_model_layers = aux_model_layers[1:]
        

        # Aggiungi checkbox alla griglia
        for i in range(self.num_hidden_layers):
            row = i // max_columns
            col = i % max_columns

            layer_frame = ctk.CTkFrame(self.checkbox_frame, border_width=1)
            layer_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            # Configura la griglia del frame per avere una sola colonna e righe
            layer_frame.columnconfigure(0, weight=1)
            layer_frame.rowconfigure(0, weight=1)
            layer_frame.rowconfigure(1, weight=0)

            # Checkbox con testo
            if self.is_convolutional(self.hidden_layers[i]):
                checkbox = ctk.CTkCheckBox(layer_frame, text=f"Hidden Layer {i + 1}:\n   {self.hidden_layers[i].__class__.__name__}\n  Input: {self.hidden_layers[i].in_channels} Output: {self.hidden_layers[i].out_channels}", font=st.TEXT_FONT)
                checkbox.grid(row=0, column=0, padx=5, pady=(5,0), sticky="w")
            else:
                checkbox = ctk.CTkCheckBox(layer_frame, text=f"Hidden Layer {i + 1}:\n   {self.hidden_layers[i].__class__.__name__}\n   Input: {self.hidden_layers[i].in_features} Output: {self.hidden_layers[i].out_features}", font=st.TEXT_FONT)
                checkbox.grid(row=0, column=0, padx=5, pady=(5,0), sticky="w")
            
            
            aux_model_layers, dropout_name, probability, have_dropout = self.have_dropout(aux_model_layers, i)
            if have_dropout:
                dropout_label = ctk.CTkLabel(layer_frame, text=f"{dropout_name} in Training\n p={probability}", font=st.TEXT_FONT)
                dropout_label.grid(row=1, column=0, padx=5, pady=5, sticky="we")
                checkbox.select()
            else:
                dropout_label = ctk.CTkLabel(layer_frame, text="", font=st.TEXT_FONT)
                dropout_label.grid(row=1, column=0, padx=5, pady=5, sticky="we")
            
            while aux_model_layers and str(aux_model_layers[0]) != str(self.hidden_layers[i+1]):
                aux_model_layers = aux_model_layers[1:]
            
            self.checkboxes.append(checkbox)
            
        
    def have_dropout(self, aux_model_layers, i):
        if i == self.num_hidden_layers - 1:
            while aux_model_layers:
                if isinstance(aux_model_layers[0], (nn.Dropout, nn.Dropout1d, nn.Dropout2d, nn.Dropout3d)):
                    return aux_model_layers,aux_model_layers[0].__class__.__name__, aux_model_layers[0].p, True
                aux_model_layers = aux_model_layers[1:]
            return aux_model_layers,"No Dropout", 0, False

        while aux_model_layers and str(aux_model_layers[0]) != str(self.hidden_layers[i+1]):
            if isinstance(aux_model_layers[0], (nn.Dropout, nn.Dropout1d, nn.Dropout2d, nn.Dropout3d)):
                return aux_model_layers, aux_model_layers[0].__class__.__name__ , aux_model_layers[0].p, True
            aux_model_layers = aux_model_layers[1:]
        return aux_model_layers, "No dropout", 0, False

    def configure_grid(self):
        self.grid_rowconfigure((0,1,2), weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        if self.num_hidden_layers > 0:
            self.set_checkboxes()
        

    def set_geometry(self):
        self.geometry(f"{self.max_width}x{self.max_height}")

    def show_graph_from_button(self):
        input_shape_text = self.input_shape_entry.get()
        try:
            self.input_shape = (self.batch_size,) + tuple(map(int, input_shape_text.strip("()").split(',')))
            
            self.create_image()
            
            # Rimuovi i widget di inserimento e il bottone
            self.input_button_frame.grid_forget()
            self.checkbox_title_label.grid_forget()
            self.error_label.grid_forget()
            
            # Espandi l'immagine per occupare tutto lo spazio disponibile
            self.image_label.configure(image=self.image_ctk, text="")
            self.image_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
            self.main_frame.grid_rowconfigure(0, weight=1)
            
        except (Exception):
            # Gestisci qualsiasi errore che si verifica, inclusi quelli di visualtorch
            self.error_label.configure(text="Invalid input shape format or error generating graph. Please try again.")
            self.error_label.grid(row=2, column=0, padx=10, pady=5, sticky="n")

    def create_image(self):
        
        if self.num_hidden_layers > 10:
            self.loaded_img = visualtorch.graph_view(self.model, input_shape=self.input_shape, layer_spacing=50, padding=10, node_size=15)
        elif self.num_hidden_layers > 5:
            self.loaded_img = visualtorch.graph_view(self.model, input_shape=self.input_shape, layer_spacing=85, padding=10, node_size=25)
        else:
            self.loaded_img = visualtorch.graph_view(self.model, input_shape=self.input_shape, layer_spacing=120, padding=10, node_size=40)
        
        self.resize_image()
        

    def try_inference_graph(self):
        try:
            self.try_inference_input_shape()
            
            self.create_image()

            # Espandi l'immagine per occupare tutto lo spazio disponibile
            self.image_label = ctk.CTkLabel(self.main_frame, image=self.image_ctk, text="")
            self.image_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
            self.main_frame.grid_rowconfigure(0, weight=1)
            
            return True
        except (Exception):
            return False
    
    def try_inference_input_shape(self):
        if isinstance(self.input_layer, nn.Linear):
            self.input_shape = (self.batch_size, self.input_layer.in_features)
        elif self.is_convolutional(self.input_layer):
            self.input_shape = (self.batch_size, self.input_layer.in_channels, 28, 28)
        return 
    
    def is_convolutional(self, layer):
        return isinstance(layer, (nn.Conv1d, nn.Conv2d, nn.Conv3d))
    