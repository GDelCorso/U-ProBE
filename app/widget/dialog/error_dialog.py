import customtkinter as ctk
import os
from config import AppStyles as st

class ErrorDialog(ctk.CTkToplevel):
    def __init__(self, master, error_message):
        super().__init__(master)
        self.title("Error")

        # Set icon for the window
        icon_path = os.path.join(os.path.dirname(__file__), "../../../assets/icon.ico")
        self.after(250, lambda: self.iconbitmap(icon_path))

        # Forza dimensioni fisse della finestra
        self.geometry("600x400")

        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Scrollable frame per il messaggio di errore
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, width=550, height=250)
        self.scrollable_frame.pack(padx=10, pady=(5, 10), fill="both", expand=True)

        # Etichetta per il messaggio di errore all'interno del frame scrollabile
        self.error_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=error_message,
            font=st.TEXT_FONT,
            text_color=st.ERROR_COLOR,
            wraplength=520,
            justify="left"  
        )
        self.error_label.pack(padx=10, pady=10, anchor="w")

        # Bottone "Close"
        self.ok_button = ctk.CTkButton(
            self.main_frame,
            text="Close",
            command=self.on_close,
            font=st.BUTTON_FONT
        )
        self.ok_button.pack(pady=(10, 10), padx=10, anchor="s")

        # Bind del protocollo di chiusura finestra
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Centra la finestra sullo schermo dopo che ha stabilito la sua dimensione effettiva
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
