import customtkinter as ctk
from config import AppStyles as st
import os
from PIL import Image  # Importa PIL per caricare l'immagine PNG
from widget.dialog.info_dialog import InfoDialog

class CommunicationSection:
    def __init__(self, master):
        self.master = master
        
        # Frame principale
        self.frame = ctk.CTkFrame(self.master)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure((0, 1), weight=0)
        
        # Progress bar sopra tutto (copre l'intera larghezza)
        self.progress_bar = ctk.CTkProgressBar(self.frame, mode="indeterminate")
        self.progress_bar.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,0), sticky="ew")
        
        # Frame per la riga di messaggio e bottone
        self.content_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5,10))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=0)
        
        # Label del messaggio (centrata)
        self.message_label = ctk.CTkLabel(
            self.content_frame,
            text="No messages",
            font=st.STATUS_FONT,
            text_color=st.COMUNICATION_COLOR
        )
        self.message_label.grid(row=0, column=0, sticky="ew", padx=10)
        
        # Carica l'immagine PNG
        try:
            png_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "info-circle.png")  # Percorso dell'immagine PNG
            
            # Usa CTkImage per caricare l'immagine PNG
            png_image = ctk.CTkImage(Image.open(png_path), size=(20, 20))  # Dimensioni dell'immagine
            
            # Info button con l'icona PNG
            self.info_button = ctk.CTkButton(
                self.content_frame,
                text="",  # Rimuovi il testo "i"
                image=png_image,
                width=20,  # Dimensione fissa del bottone
                height=20,
                fg_color="transparent",
                hover_color=("gray75", "gray25"),
                command=self.show_info,
                corner_radius=15
            )
        except Exception as e:
            # Fallback al bottone con "i"
            self.info_button = ctk.CTkButton(
                self.content_frame,
                text="i",
                width=30,
                height=30,
                fg_color="transparent",
                hover_color=("gray75", "gray25"),
                command=self.show_info,
                font=("Helvetica", 14, "italic"),
                corner_radius=15
            )
            
        self.info_button.grid(row=0, column=1, padx=(0,10), sticky="e")
        
        # Configura la dimensione minima del frame
        self.frame.configure(height=70)
    
    def display_message(self, message, color):
        self.message_label.configure(text=message, text_color=color)
        self.master.update()
    
    def start_progress(self):
        self.progress_bar.start()
        self.master.update()
        
    def stop_progress(self):
        self.progress_bar.stop()
        self.master.update()
        
    def show_info(self):
        InfoDialog(self.master)
