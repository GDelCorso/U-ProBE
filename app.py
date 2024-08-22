import os   
import customtkinter as ctk
from pages.uprobe_page import UprobePage

# Set the application theme
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window title and size
        self.title("U-ProBE")
        self.geometry("1024x600")

        # Set application icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets/icon.ico")
        self.iconbitmap(icon_path)

        # Configure the main grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create and place the UprobePage instance
        self.inference_page = UprobePage(self)
        self.inference_page.frame.grid(row=0, column=0, sticky="nsew")
        
        self.minsize(720, 420)
        
        # Bring the window to the front
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)

# Run the application
app = App()
app.mainloop()
