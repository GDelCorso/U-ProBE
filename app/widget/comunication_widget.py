import customtkinter as ctk
from config import AppStyles as st

class CommunicationSection:
    def __init__(self, master):
        self.master = master
        
        # Create a label for status messages
        self.message_label = ctk.CTkLabel(self.master, text="No messages", font=st.STATUS_FONT, text_color=st.COMUNICATION_COLOR)
        self.message_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # Create a progress bar
        self.progress_bar = ctk.CTkProgressBar(self.master, mode="indeterminate")
        self.progress_bar.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    def display_message(self, message, color):
        self.message_label.configure(text=message, text_color=color)
        self.master.update()  

    def start_progress(self):
        self.progress_bar.start()  # Start the progress animation
        self.master.update() 

    def stop_progress(self):
        self.progress_bar.stop()  # Stop the progress animation

