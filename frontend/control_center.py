import customtkinter as ctk
try:
    from frontend.device_control import list_devices, send_command, broadcast_command
    from frontend.result_control import latest_device_result, format_execution_result
    from frontend.device_monitor import device_signature, detect_device_changes
    from frontend.command_history import history
except ModuleNotFoundError:
    from device_control import list_devices, send_command, broadcast_command
    from result_control import latest_device_result, format_execution_result
    from device_monitor import device_signature, detect_device_changes

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
        self.monitor_after_id = None
        self.monitor_signature = {}
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

        self.page = ctk.CTkScrollableFrame(self.main, corner_radius=14)
        self.page.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.show_page("CHAT")

    def show_page(self, name):
        if self.page_title.get() == "DEVICES" and name != "DEVICES":
            self.stop_device_monitor()
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
        ctk.CTkLabel(self.page,text='Connected devices',font=('Arial',22,'bold')).pack(pady=(20,8))
        self.device_status=ctk.CTkLabel(self.page,text='Checking devices...')
        self.device_status.pack(pady=5)
        self.device_cards=ctk.CTkScrollableFrame(self.page,height=180)
        self.device_cards.pack(fill='x',padx=20,pady=10)
        self.selected_device=ctk.StringVar(value='')
        ctk.CTkLabel(self.page,text='Selected device',font=('Arial',13,'bold')).pack(anchor='w',padx=25,pady=(10,3))
        self.selected_label=ctk.CTkLabel(self.page,text='None selected')
        self.selected_label.pack(anchor='w',padx=25)
        ctk.CTkLabel(self.page,text='Latest execution result',font=('Arial',13,'bold')).pack(anchor='w',padx=25,pady=(8,3))
        self.execution_result=ctk.CTkLabel(self.page,text='No execution result available.',justify='left',anchor='w',wraplength=800)
        self.execution_result.pack(fill='x',padx=25,pady=(0,8))
        ctk.CTkLabel(self.page,text='Recent command history',font=('Arial',13,'bold')).pack(anchor='w',padx=25,pady=(8,3))
        self.history_box=ctk.CTkTextbox(self.page,height=110)
        self.history_box.pack(fill='x',padx=25,pady=(0,8))
        self.history_box.configure(state='disabled')
        ctk.CTkLabel(self.page,text='Command',font=('Arial',13,'bold')).pack(anchor='w',padx=25,pady=(12,3))
        command_row=ctk.CTkFrame(self.page,fg_color='transparent')
        command_row.pack(fill='x',padx=25,pady=5)
        command_row.grid_columnconfigure(0,weight=1)
        self.command_entry=ctk.CTkEntry(command_row,height=40,placeholder_text='open notepad')
        self.command_entry.grid(row=0,column=0,sticky='ew',padx=(0,10))
        ctk.CTkButton(command_row,text='SEND',width=100,height=40,command=self.send_device_command).grid(row=0,column=1)
        ctk.CTkLabel(self.page,text='Broadcast command',font=('Arial',13,'bold')).pack(anchor='w',padx=25,pady=(12,3))
        broadcast_row=ctk.CTkFrame(self.page,fg_color='transparent')
        broadcast_row.pack(fill='x',padx=25,pady=5)
        broadcast_row.grid_columnconfigure(0,weight=1)
        self.broadcast_entry=ctk.CTkEntry(broadcast_row,height=40,placeholder_text='command for all devices')
        self.broadcast_entry.grid(row=0,column=0,sticky='ew',padx=(0,10))
        ctk.CTkButton(broadcast_row,text='BROADCAST',width=120,height=40,command=self.send_broadcast).grid(row=0,column=1)
        actions=ctk.CTkFrame(self.page,fg_color='transparent')
        actions.pack(fill='x',padx=25,pady=(12,5))
        ctk.CTkButton(actions,text='REFRESH',height=36,command=self.refresh_devices).pack(side='left')
        self.command_result=ctk.CTkLabel(self.page,text='')
        self.command_result.pack(pady=8)
        self.refresh_devices()
        self.start_device_monitor()

    def start_device_monitor(self):
        self.stop_device_monitor()
        self.monitor_signature = device_signature(list_devices() or [])
        self.monitor_after_id = self.root.after(2000, self._poll_device_monitor)

    def stop_device_monitor(self):
        if self.monitor_after_id is not None:
            try:
                self.root.after_cancel(self.monitor_after_id)
            except Exception:
                pass
            self.monitor_after_id = None

    def _poll_device_monitor(self):
        self.monitor_after_id = None
        if self.page_title.get() != "DEVICES":
            return
        try:
            devices = list_devices()
            if devices is not None:
                current = device_signature(devices)
                changes = detect_device_changes(self.monitor_signature, current)
                if changes:
                    self.monitor_signature = current
                    self.refresh_devices()
                else:
                    self.monitor_signature = current
        except Exception as e:
            self.command_result.configure(text=f"Device monitor error: {e}")
        finally:
            if self.page_title.get() == "DEVICES":
                self.monitor_after_id = self.root.after(2000, self._poll_device_monitor)

    def refresh_devices(self):
        devices=list_devices()
        if devices is None:
            self.device_status.configure(text='FRIDAY Core unavailable')
            self.command_result.configure(text='Could not reach FRIDAY Core.')
            return
        self.device_status.configure(text=f'{len(devices)} device(s) connected')
        for widget in self.device_cards.winfo_children():
            widget.destroy()
        if not devices:
            ctk.CTkLabel(self.device_cards,text='No connected devices.').pack(pady=20)
            self.selected_device.set('')
            self.selected_label.configure(text='None selected')
            return
        current=self.selected_device.get()
        available_ids=[]
        for device in devices:
            device_id=device.get('device_id','unknown') if isinstance(device,dict) else str(device)
            online=device.get('online',False) if isinstance(device,dict) else True
            available_ids.append(device_id)
            card=ctk.CTkFrame(self.device_cards,corner_radius=10)
            card.pack(fill='x',padx=5,pady=5)
            state='ONLINE' if online else 'OFFLINE'
            ctk.CTkLabel(card,text=f'{"●" if online else "○"} {device_id}',font=('Arial',15,'bold')).pack(side='left',padx=12,pady=10)
            ctk.CTkLabel(card,text=state).pack(side='left',padx=8)
            ctk.CTkButton(card,text='SELECT',width=90,command=lambda d=device_id:self.select_device(d)).pack(side='right',padx=10,pady=8)
        if current not in available_ids:
            self.select_device(available_ids[0])
        else:
            self.selected_label.configure(text=current)

    def refresh_execution_result(self, device_id=None):
        if device_id is None:
            device_id=self.selected_device.get().strip()
        if not device_id:
            self.execution_result.configure(text="Select a device to view execution results.")
            return
        try:
            result=latest_device_result(device_id)
            self.execution_result.configure(text=format_execution_result(result))
        except Exception as e:
            self.execution_result.configure(text=f"Could not load execution result: {e}")

    def select_device(self,device_id):
        self.selected_device.set(device_id)
        self.selected_label.configure(text=device_id)
        self.command_result.configure(text=f'Selected {device_id}')
        self.refresh_execution_result(device_id)

    def refresh_command_history(self, device_id=None):
        if device_id is None:
            device_id = self.selected_device.get().strip()
        if not device_id:
            return
        items = history.recent(device_id, limit=8)
        lines = []
        for item in reversed(items):
            result = item.get("result") or {}
            outcome = result.get("outcome", "pending")
            command = item.get("command", "")
            lines.append("[{}] {}".format(outcome, command))
        text = "\n".join(lines) if lines else "No commands recorded yet."
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        self.history_box.insert("1.0", text)
        self.history_box.configure(state="disabled")

    def record_command_history(self, device_id, command):
        try:
            result = latest_device_result(device_id) or {}
            history.add(device_id, command, result)
            self.refresh_command_history(device_id)
        except Exception as e:
            self.command_result.configure(text="History error: {}".format(e))

    def send_device_command(self):
        device_id=self.selected_device.get().strip()
        command=self.command_entry.get().strip()
        if not device_id or not command:
            self.command_result.configure(text='Select a device and enter a command.')
            return
        result=send_command(device_id,command)
        if isinstance(result,dict) and result.get('success') is True:
            self.command_result.configure(text=f'Command sent to {device_id} ✓')
            self.root.after(900, lambda: (self.refresh_execution_result(device_id), self.record_command_history(device_id, command)))
        else:
            self.command_result.configure(text='Command could not be sent.')

    def send_broadcast(self):
        command=self.broadcast_entry.get().strip()
        if not command:
            self.command_result.configure(text='Enter a broadcast command.')
            return
        result=broadcast_command(command)
        if isinstance(result,dict) and result.get('success') is True:
            self.command_result.configure(text='Broadcast sent to connected devices ✓')
            device_id=self.selected_device.get().strip()
            if device_id:
                self.root.after(700, lambda: self.refresh_execution_result(device_id))
        else:
            self.command_result.configure(text='Broadcast could not be sent.')

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
