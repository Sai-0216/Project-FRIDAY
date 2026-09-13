import customtkinter as ctk

PAGES = ("CHAT", "DEVICES", "GOALS", "TASKS", "AGENTS", "SYSTEM")


class FridayControlCenter:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("FRIDAY Control Center")
        self.root.geometry("1280x780")
        self.root.minsize(1050, 650)

        self.page_title = ctk.StringVar(value="CHAT")
        self._build()

    def _build(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self.root, width=210, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="FRIDAY",
            font=("Arial", 30, "bold"),
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            sidebar,
            text="CONTROL CENTER",
            font=("Arial", 11, "bold"),
        ).pack(pady=(0, 25))

        for name in PAGES:
            ctk.CTkButton(
                sidebar,
                text=name,
                height=42,
                command=lambda page=name: self.show_page(page),
            ).pack(fill="x", padx=18, pady=5)

        self.main = ctk.CTkFrame(self.root, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.main,
            textvariable=self.page_title,
            font=("Arial", 28, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=20)

        self.page = ctk.CTkFrame(self.main, corner_radius=14)
        self.page.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.show_page("CHAT")

    def show_page(self, name):
        if name not in PAGES:
            name = "CHAT"

        self.page_title.set(name)

        for widget in self.page.winfo_children():
            widget.destroy()

        if name == "CHAT":
            ctk.CTkLabel(
                self.page,
                text="FRIDAY conversation",
                font=("Arial", 24, "bold"),
            ).pack(pady=(100, 10))
            ctk.CTkLabel(
                self.page,
                text="Chat integration will connect to the existing FRIDAY brain.",
            ).pack()
            return

        ctk.CTkLabel(
            self.page,
            text=f"{name} module",
            font=("Arial", 24, "bold"),
        ).pack(pady=100)
        ctk.CTkLabel(
            self.page,
            text="Frontend foundation ready.",
        ).pack()

    def run(self):
        self.root.mainloop()


def self_test():
    return {
        "pages": list(PAGES),
        "page_count": len(PAGES),
        "valid": True,
    }


if __name__ == "__main__":
    FridayControlCenter().run()
