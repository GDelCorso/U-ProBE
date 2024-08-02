import customtkinter as ctk
from PIL import Image
import os

class ImageDialog(ctk.CTkToplevel):
    def __init__(self, master, image):
        super().__init__(master)
        self.title("Model Graph")
        
        self.load_icon()
        self.loaded_img = image
        self.max_width = 1920
        self.max_height = 1080

        self.resize_image()
        self.create_widgets()
        self.configure_grid()
        self.set_geometry()
        
        self.lift()
        self.grab_set()
        self.minsize(400, 300)

    def load_icon(self):
        script_dir = os.path.dirname(__file__)
        parent_dir = os.path.dirname(script_dir)
        icon_path = os.path.join(parent_dir, "assets", "icon.ico")
        
        if os.path.isfile(icon_path):
            self.iconbitmap(icon_path)
        else:
            print(f"Icon file not found: {icon_path}")

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
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.image_frame = ctk.CTkFrame(self.main_frame)
        self.image_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        
        self.image_label = ctk.CTkLabel(self.image_frame, image=self.image_ctk)
        self.image_label.grid(row=0, column=0, sticky="nsew")
        
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.close_button = ctk.CTkButton(self.button_frame, text="Close", command=self.destroy)
        self.close_button.grid(row=0, column=0, padx=10, pady=10)

    def configure_grid(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.image_frame.grid_rowconfigure(0, weight=1)
        self.image_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_rowconfigure(0, weight=0)
        self.button_frame.grid_columnconfigure(0, weight=1)

    def set_geometry(self):
        self.geometry(f"{min(self.loaded_img.width + 20, self.max_width)}x{min(self.loaded_img.height + 80, self.max_height)}")
