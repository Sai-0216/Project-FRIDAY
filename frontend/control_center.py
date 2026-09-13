import customtkinter as ctk
try:
    from frontend.device_control import list_devices, send_command, broadcast_command
except ModuleNotFoundError:
    from device_control import list_devices, send_command, broadcast_command

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

        if name == "DEVICES":
            self.devices_page()
            return

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

    def devices_page(self):
        ctk.CTkLabel(self.page,text="Connected devices",font=("Arial",22,"bold")).pack(pady=(25,10))
        self.device_status=ctk.CTkLabel(self.page,text="Checking devices...")
        self.device_status.pack(pady=5)
        self.device_list=ctk.CTkTextbox(self.page,height=180,font=("Consolas",13))
        self.device_list.pack(fill="x",padx=25,pady=15)
        self.device_list.configure(state="disabled")
        self.command_device=ctk.StringVar(value="")
        self.command_entry=ctk.CTkEntry(self.page,height=42,placeholder_text="Command, e.g. open notepad")
        self.command_entry.pack(fill="x",padx=25,pady=10)
        ctk.CTkButton(self.page,text="SEND COMMAND",height=42,command=self.send_device_command).pack(anchor="e",padx=25,pady=10)
        self.command_result=ctk.CTkLabel(self.page,text="")
        self.command_result.pack(pady=10)
        self.refresh_devices()

    def refresh_devices(self):
        devices=list_devices()
        if devices is None:
            self.device_status.configure(text="FRIDAY Core unavailable")
            return
        self.device_status.configure(text=f"{len(devices)} device(s) connected")
        self.device_list.configure(state="normal")
        self.device_list.delete("1.0","end")
        if not devices:
            self.device_list.insert("end","No connected devices.")
        else:
            for device in devices:
                device_id=device.get("device_id","unknown") if isinstance(device,dict) else str(device)
                online=device.get("online",False) if isinstance(device,dict) else True
                marker="ONLINE" if online else "OFFLINE"
                self.device_list.insert("end",f"[{marker}] {device_id}\n")
                if not self.command_device.get():
                    self.command_device.set(device_id)
        self.device_list.configure(state="disabled")

    def send_device_command(self):
        command=self.command_entry.get().strip()
        device_id=self.command_device.get().strip()
        if not device_id or not command:
            self.command_result.configure(text="Select a device and enter a command.")
            return
        result=send_command(device_id,command)
        if isinstance(result,dict) and result.get("success") is True:
            self.command_result.configure(text=f"Command sent to {device_id} ✓")
        else:
            self.command_result.configure(text="Command could not be sent.")

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
