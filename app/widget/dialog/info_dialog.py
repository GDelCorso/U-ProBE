import customtkinter as ctk
from config import AppStyles as st
import os

class InfoDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Information")
        
        # Set icon for the window
        icon_path = os.path.join(os.path.dirname(__file__), "../../../assets/icon.ico")
        self.after(250, lambda: self.iconbitmap(icon_path))
        
        # Forza dimensioni fisse della finestra
        self.geometry("600x520")
        
        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Titolo principale per tutta la pagina
        self.page_title = ctk.CTkLabel(
            self.main_frame,
            text="Application Information",
            font=st.HEADER_FONT,  # Un font più grande per il titolo
            justify="center"
        )
        self.page_title.pack(padx=10, pady=(10, 20), anchor="n")
        
        # Frame scrollabile per la prima sezione: "What the application do"
        self.what_scroll_frame = ctk.CTkScrollableFrame(self.main_frame, width=550, height=180)
        self.what_scroll_frame.pack(padx=10, pady=(5,5), fill="both", expand=False)
        
        # Titolo della prima sezione
        self.what_label = ctk.CTkLabel(
            self.what_scroll_frame,
            text="What the application do",
            font=st.HEADER_FONT,
            justify="left"
        )
        self.what_label.pack(padx=10, pady=(10,5), anchor="w")
        
        # Contenuto della prima sezione
        self.what_content = ctk.CTkLabel(
            self.what_scroll_frame,
            text="U-ProBE is a desktop application that makes it easy to apply post-hoc techniques—non-intrusive methods that operate on the inference of neural networks and provide data related to the uncertainty of results—on PyTorch image classification models. Developed by Lorenzo Bandini and still under development. Code contributions can be made at https://github.com/lorenzobandini/U-ProBE.",
            font=st.TEXT_FONT,
            wraplength=520,
            justify="left"
        )
        self.what_content.pack(padx=10, pady=(0,15), anchor="w")
        
        # Frame scrollabile per la seconda sezione: "How to use"
        self.how_scroll_frame = ctk.CTkScrollableFrame(self.main_frame, width=550, height=180)
        self.how_scroll_frame.pack(padx=10, pady=(5, 10), fill="both", expand=False)
        
        # Titolo della seconda sezione
        self.how_label = ctk.CTkLabel(
            self.how_scroll_frame,
            text="How to use",
            font=st.HEADER_FONT,
            justify="left"
        )
        self.how_label.pack(padx=10, pady=(10,5), anchor="w")
        
        # Contenuto della seconda sezione
        self.how_content = ctk.CTkLabel(
            self.how_scroll_frame,
            text="To use the application, prepare the input data: specifically, the model must be in `.pt` format with the weights included. You must also provide the model class renamed to **`CustomModel`**, which defines its structure, a dataloader for preprocessing the data renamed to **`CustomLoader`**, and a dataset in `.csv` format that must include columns for **`id`** and **`split`** (indicating the data type: training/testing). After loading the model class, it is possible to visualize the network structure through the designated button. Once all inputs are loaded, you can proceed with inference by selecting the techniques you wish to apply.  Upon completing the inference, a brief summary of the model and its statistics will be displayed along with a chart showing its performance. If you wish to use the obtained data for other purposes, you can export it in `.csv` format using the corresponding button.",
            font=st.TEXT_FONT,
            wraplength=520,
            justify="left"
        )
        self.how_content.pack(padx=10, pady=(0,15), anchor="w")
        
        # Bottone "Close"
        self.ok_button = ctk.CTkButton(
            self.main_frame,
            text="Close",
            command=self.on_close,
            font=st.BUTTON_FONT
        )
        self.ok_button.pack(pady=(10, 20), padx=10, anchor="center")  # Ridotto il margine sotto
        
        # Credits (in basso, leggermente distanziati a destra e dal fondo)
        self.credits = ctk.CTkLabel(
            self.main_frame,
            text="Created by Lorenzo Bandini",
            font=("Helvetica", 10),
            text_color="gray"
        )
        self.credits.pack(pady=(0, 10), padx=(0, 20), anchor="se")  # Margini inferiori e laterali ridotti
        
        # Bind del protocollo di chiusura finestra
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Centra la finestra
        self.after(100, self.center_window)
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)
        
    def center_window(self):
        self.update_idletasks()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        
        self.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
    
    def on_close(self):
        self.destroy()
