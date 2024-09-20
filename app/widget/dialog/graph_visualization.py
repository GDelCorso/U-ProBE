from collections import defaultdict
import customtkinter as ctk
from PIL import Image
import os
from config import AppStyles as st
import visualtorch
from torch import nn

class ImageDialog(ctk.CTkToplevel):
    def __init__(self, master, import_widget, model, layers, model_sequence):
        super().__init__(master)
        self.title("Model Graph")

        # Set icon for the window
        icon_path = os.path.join(os.path.dirname(__file__), "../../../assets/icon.ico")
        self.after(250, lambda: self.iconbitmap(icon_path))

        self.max_width = 1280
        self.max_height = 720

        self.model = model
        self.input_layer = layers[0]
        self.hidden_layers = layers[1:]
        self.num_hidden_layers = len(self.hidden_layers)
        self.model_sequence = model_sequence
        self.import_widget = import_widget

        self.already_shown = True
        self.batch_size = 4
        self.input_shape = (self.batch_size, 3, 224, 224)
        
        self.threshhold_halting_criterion = self.import_widget.get_threshold_halting_criterion()
        if(self.threshhold_halting_criterion is None):
            self.already_shown = False
            self.threshhold_halting_criterion = 0.001
        
        self.checkboxes_dict = self.import_widget.get_dropout_checkboxes()
        if self.checkboxes_dict is None:
            self.already_shown = False
            self.checkboxes_dict = defaultdict(lambda: {"checked": False, "mc_dropout": 0.0})

        self.create_widgets()
        self.configure_grid()

        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)
        self.minsize(720, 420)

        # Bind window close protocol
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def resize_image(self):
        img_width, img_height = self.loaded_img.size
        aspect_ratio = img_width / img_height

        max_img_width = self.max_width - 40
        max_img_height = self.max_height - 300

        if aspect_ratio > 1:
            new_width = min(img_width, max_img_width)
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = min(img_height, max_img_height)
            new_width = int(new_height * aspect_ratio)

        # Resize image with high-quality resampling
        self.loaded_img = self.loaded_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.image_ctk = ctk.CTkImage(light_image=self.loaded_img, dark_image=self.loaded_img, size=self.loaded_img.size)

    def create_widgets(self):
        # Main title
        self.title_label = ctk.CTkLabel(self, text="Graph Visualizer", font=st.HEADER_FONT)
        self.title_label.grid(row=0, column=0, padx=10, pady=(5,0), sticky="nsew")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        if not self.try_inference_graph():
            # Initial label to prompt for input shape
            self.image_label = ctk.CTkLabel(
                self.main_frame,
                text="Insert input shape to visualize model",
                font=st.HEADER_FONT,
                width=400,
                height=200  # Reduced height
            )
            self.image_label.grid(row=0, column=0, padx=10, pady=(5,0), sticky="nsew")

            # Frame containing input and button
            self.input_button_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
            self.input_button_frame.grid(row=1, column=0, padx=10, pady=2, sticky="n")

            self.input_shape_entry = ctk.CTkEntry(self.input_button_frame, placeholder_text="3, 224, 224")
            self.input_shape_entry.grid(row=0, column=0, padx=5, pady=2)

            self.update_button = ctk.CTkButton(
                self.input_button_frame,
                text="Show Graph",
                command=self.show_graph_from_button,
                font=st.BUTTON_FONT
            )
            self.update_button.grid(row=0, column=1, padx=5, pady=2)

            # Error message area
            self.error_label = ctk.CTkLabel(
                self.main_frame,
                text="",
                font=st.STATUS_FONT,
                text_color=st.ERROR_COLOR
            )
            self.error_label.grid(row=2, column=0, padx=10, pady=(5,0), sticky="n")

        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.grid(row=3, column=0, padx=10, pady=(5,0), sticky="nsew")
        self.top_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # "Dropout Layers" title (centered)
        self.checkbox_title_label = ctk.CTkLabel(self.top_frame, text="MC-Dropout Layers", font=st.COLUMN_FONT)
        self.checkbox_title_label.grid(row=0, column=1, padx=10, pady=(5,2))

        # Halting criterion frame (right-aligned)
        self.threshhold_threshhold_halting_criterion_frame = ctk.CTkFrame(self.top_frame)
        self.threshhold_threshhold_halting_criterion_frame.grid(row=0, column=2, padx=10, pady=2, sticky="e")

        # Halting criterion label and input
        self.threshhold_halting_label = ctk.CTkLabel(self.threshhold_threshhold_halting_criterion_frame, text="Threshhold Halting Criterion:", font=st.TEXT_FONT)
        self.threshhold_halting_label.grid(row=0, column=0, padx=(5, 5), pady=2, sticky="w")
        
        self.threshhold_halting_entry = ctk.CTkEntry(self.threshhold_threshhold_halting_criterion_frame, width=60)
        self.threshhold_halting_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.threshhold_halting_entry.insert(0, str(self.threshhold_halting_criterion))

        # Checkbox frame (now in a separate row)
        self.checkbox_frame = ctk.CTkFrame(self.main_frame)
        self.checkbox_frame.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

    def set_checkboxes(self):
        self.checkboxes = []
        max_columns = 4  # Maximum number of columns for checkboxes
        num_rows = (self.num_hidden_layers + max_columns - 1) // max_columns  # Calculate required rows

        # Configure grid rows and columns
        for r in range(num_rows):
            self.checkbox_frame.grid_rowconfigure(r, weight=1)
        for c in range(max_columns):
            self.checkbox_frame.grid_columnconfigure(c, weight=1)

        # Remove input layer from model sequence
        aux_model_layers = self.model_sequence[1:]
        
        # Remove all layers before the first hidden layer
        while aux_model_layers and str(aux_model_layers[0]) != str(self.hidden_layers[0]):
            aux_model_layers = aux_model_layers[1:]

        # Add checkboxes to grid
        for i in range(self.num_hidden_layers):
            row = i // max_columns
            col = i % max_columns

            layer_frame = ctk.CTkFrame(self.checkbox_frame, border_width=1)
            layer_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

            # Configure grid for the layer frame
            layer_frame.columnconfigure(0, weight=1)
            layer_frame.rowconfigure(0, weight=1)
            layer_frame.rowconfigure((1,2), weight=0)

            # Create checkbox with layer details
            if self.is_convolutional(self.hidden_layers[i]):
                checkbox = ctk.CTkCheckBox(
                    layer_frame,
                    text=f"Layer {i + 2}:\n   {self.hidden_layers[i].__class__.__name__}\n  Input: {self.hidden_layers[i].in_channels} Output: {self.hidden_layers[i].out_channels}",
                    font=st.TEXT_FONT
                )
            else:
                checkbox = ctk.CTkCheckBox(
                    layer_frame,
                    text=f"Layer {i + 2}:\n   {self.hidden_layers[i].__class__.__name__}\n   Input: {self.hidden_layers[i].in_features} Output: {self.hidden_layers[i].out_features}",
                    font=st.TEXT_FONT
                )

            checkbox.grid(row=0, column=0, padx=5, pady=2, sticky="w")

            # Associate callback function to checkbox
            checkbox.configure(command=lambda idx=i+1: self.update_checkbox_status(idx))

            aux_model_layers, dropout_name, probability, have_dropout = self.have_dropout(aux_model_layers, i)
            if have_dropout:
                dropout_label = ctk.CTkLabel(
                    layer_frame,
                    text=f"{dropout_name} in Training (p={probability})",
                    font=st.TEXT_FONT
                )
                dropout_label.grid(row=1, column=0, padx=5, pady=2, sticky="we")
                if(self.already_shown):
                    if self.checkboxes_dict[i + 1]["checked"]:
                        checkbox.select()
                else:
                    checkbox.select()
                    self.checkboxes_dict[i + 1]["checked"] = True
                    self.checkboxes_dict[i + 1]["mc_dropout"] = probability
            else:
                dropout_label = ctk.CTkLabel(layer_frame, text="", font=st.TEXT_FONT)
                dropout_label.grid(row=1, column=0, padx=5, pady=5, sticky="we")
                if(self.already_shown):
                    if self.checkboxes_dict[i + 1]["checked"]:
                        checkbox.select()
                    else:
                        checkbox.deselect()
                else:
                    self.checkboxes_dict[i + 1]["checked"] = False
                    
            # Add MC-Dropout probability input
            mc_dropout_frame = ctk.CTkFrame(layer_frame, fg_color="transparent")
            mc_dropout_frame.grid(row=2, column=0, padx=2, pady=2, sticky="we")
            
            mc_dropout_label = ctk.CTkLabel(mc_dropout_frame, text="MC-Dropout Prob:", font=st.TEXT_FONT)
            mc_dropout_label.grid(row=0, column=0, padx=2, pady=2, sticky="e")
            
            mc_dropout_entry = ctk.CTkEntry(mc_dropout_frame, width=50, state="normal" if self.checkboxes_dict[i + 1]["checked"] else "disabled")
            mc_dropout_entry.grid(row=0, column=1, sticky="w")
            if self.checkboxes_dict[i + 1]["checked"]:
                mc_dropout_entry.insert(0, str(self.checkboxes_dict[i + 1]["mc_dropout"]))
            
            # Update MC-Dropout probability when entry changes
            mc_dropout_entry.bind("<FocusOut>", lambda event, idx=i+1: self.update_mc_dropout(event, idx))

            if self.num_hidden_layers > i + 1:
                while aux_model_layers and str(aux_model_layers[0]) != str(self.hidden_layers[i + 1]):
                    aux_model_layers = aux_model_layers[1:]

            self.checkboxes.append((checkbox, mc_dropout_entry))

    def update_checkbox_status(self, idx):
        # Toggle checkbox status in dictionary
        self.checkboxes_dict[idx]["checked"] = not self.checkboxes_dict[idx]["checked"]
        
        # Enable/disable and clear MC-Dropout entry based on checkbox status
        entry = self.checkboxes[idx-1][1]
        if self.checkboxes_dict[idx]["checked"]:
            entry.configure(state="normal")
            if self.checkboxes_dict[idx]["mc_dropout"] > 0:
                entry.delete(0, 'end')
                entry.insert(0, str(self.checkboxes_dict[idx]["mc_dropout"]))
        else:
            entry.configure(state="disabled")
            entry.delete(0, 'end')
            self.checkboxes_dict[idx]["mc_dropout"] = 0.0

    def update_mc_dropout(self, event, idx):
        value = event.widget.get()
        try:
            value = float(value)
            if 0 <= value <= 1:
                self.checkboxes_dict[idx]["mc_dropout"] = value
            else:
                raise ValueError
        except ValueError:
            event.widget.delete(0, 'end')
            self.checkboxes_dict[idx]["mc_dropout"] = 0.0


    def have_dropout(self, aux_model_layers, i):
        if i == self.num_hidden_layers - 1:
            while aux_model_layers:
                if isinstance(aux_model_layers[0], (nn.Dropout, nn.Dropout1d, nn.Dropout2d, nn.Dropout3d)):
                    return aux_model_layers, aux_model_layers[0].__class__.__name__, aux_model_layers[0].p, True
                aux_model_layers = aux_model_layers[1:]
            return aux_model_layers, "No Dropout", 0, False

        while aux_model_layers and str(aux_model_layers[0]) != str(self.hidden_layers[i + 1]):
            if isinstance(aux_model_layers[0], (nn.Dropout, nn.Dropout1d, nn.Dropout2d, nn.Dropout3d)):
                return aux_model_layers, aux_model_layers[0].__class__.__name__, aux_model_layers[0].p, True
            aux_model_layers = aux_model_layers[1:]
        return aux_model_layers, "No Dropout", 0, False

    def configure_grid(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.main_frame.grid_rowconfigure((0, 1, 2, 3), weight=0)
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

            # Remove input widgets and button
            self.input_button_frame.grid_forget()
            self.checkbox_title_label.grid_forget()
            self.error_label.grid_forget()

            # Expand image to fill available space
            self.image_label.configure(image=self.image_ctk, text="")
            self.image_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
            self.main_frame.grid_rowconfigure(0, weight=1)

        except Exception:
            # Handle any errors including those from visualtorch
            self.error_label.configure(
                text="Invalid input shape format or error generating graph. Please try again."
            )
            self.error_label.grid(row=2, column=0, padx=10, pady=5, sticky="n")

    def create_image(self):
        # Adjust layer spacing and node size based on the number of hidden layers
        if self.num_hidden_layers > 10:
            self.loaded_img = visualtorch.graph_view(
                self.model,
                input_shape=self.input_shape,
                layer_spacing=50,
                padding=10,
                node_size=15
            )
        elif self.num_hidden_layers > 5:
            self.loaded_img = visualtorch.graph_view(
                self.model,
                input_shape=self.input_shape,
                layer_spacing=85,
                padding=10,
                node_size=25
            )
        else:
            self.loaded_img = visualtorch.graph_view(
                self.model,
                input_shape=self.input_shape,
                layer_spacing=120,
                padding=10,
                node_size=40
            )

        self.resize_image()

    def try_inference_graph(self):
        try:
            self.try_inference_input_shape()

            self.create_image()

            # Display the image
            self.image_label = ctk.CTkLabel(self.main_frame, image=self.image_ctk, text="")
            self.image_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
            self.main_frame.grid_rowconfigure(0, weight=1)

            return True
        except Exception:
            return False

    def try_inference_input_shape(self):
        # Determine input shape based on the type of input layer
        if isinstance(self.input_layer, nn.Linear):
            self.input_shape = (self.batch_size, self.input_layer.in_features)
        elif self.is_convolutional(self.input_layer):
            self.input_shape = (self.batch_size, self.input_layer.in_channels, 28, 28)
        return

    def is_convolutional(self, layer):
        return isinstance(layer, (nn.Conv1d, nn.Conv2d, nn.Conv3d))

    def update_mc_dropout_values(self):
        for idx, (_, mc_dropout_entry) in enumerate(self.checkboxes, start=1):
            if self.checkboxes_dict[idx]["checked"]:
                try:
                    value = float(mc_dropout_entry.get())
                    if 0 <= value <= 1:
                        self.checkboxes_dict[idx]["mc_dropout"] = value
                    else:
                        self.checkboxes_dict[idx]["mc_dropout"] = 0.0
                except ValueError:
                    self.checkboxes_dict[idx]["mc_dropout"] = 0.0
    
    def on_close(self):
        self.update_mc_dropout_values()
        self.import_widget.set_dropout_checkboxes(self.checkboxes_dict)
        try:
            halting_value = float(self.threshhold_halting_entry.get())
            self.import_widget.set_threshold_halting_criterion(halting_value)
        except ValueError:
            self.import_widget.set_threshold_halting_criterion(0.001)
        
        self.destroy()
