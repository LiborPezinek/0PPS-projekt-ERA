import customtkinter as ctk


class LogPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.text = ctk.CTkTextbox(self, height=120)
        self.text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        self.write("Log ready.")

    def write(self, msg: str):
        self.text.insert("end", msg + "\n")
        self.text.see("end")
