import customtkinter as ctk


class FridayGUI:

    def __init__(self):

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("FRIDAY")
        self.root.geometry("900x650")

        title = ctk.CTkLabel(
            self.root,
            text="FRIDAY",
            font=("Arial", 36, "bold")
        )
        title.pack(pady=20)

        self.status = ctk.CTkLabel(
            self.root,
            text="Status : Idle",
            font=("Arial", 18)
        )
        self.status.pack()

        self.chat = ctk.CTkTextbox(
            self.root,
            width=820,
            height=420
        )

        self.chat.pack(pady=20)
        self.chat.configure(state="disabled")

    def add_message(self, sender, message):

        self.chat.configure(state="normal")

        self.chat.insert(
            "end",
            f"{sender}: {message}\n\n"
        )

        self.chat.configure(state="disabled")
        self.chat.see("end")

    def set_status(self, status):
        self.status.configure(text=f"Status : {status}")

    def run(self):
        self.root.mainloop()


gui = FridayGUI()