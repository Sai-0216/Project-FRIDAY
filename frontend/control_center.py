import customtkinter as ctk
try:
    from frontend.device_control import list_devices, send_command, broadcast_command
    from frontend.result_control import latest_device_result, format_execution_result
    from frontend.device_monitor import device_signature, detect_device_changes
    from frontend.command_history import history
    from frontend.activity_timeline import build_timeline, format_timeline
    from frontend.persistent_activity import PersistentActivityStore
    from frontend.activity_search import filter_activity
    from frontend.activity_selection import select_activity, activity_labels
    from frontend.activity_navigation import previous_index, next_index, navigation_state
    from frontend.activity_summary import format_activity_summary
    from frontend.activity_export import export_activity_json
    from frontend.activity_refresh import activity_signature, detect_activity_changes
    from frontend.activity_notifications import build_activity_notification, format_activity_notification
    from frontend.notification_manager import NotificationManager
    from frontend.notification_persistence import NotificationPersistence
    from frontend.notification_filter import filter_notifications, available_notification_types
    from frontend.notification_priority import sort_notifications
    from frontend.notification_grouping import group_notifications, format_notification_groups
    from frontend.notification_read_state import mark_notification_read, mark_notification_unread, unread_count, format_read_state
    from frontend.activity_details import format_activity_details
except ModuleNotFoundError:
    from device_control import list_devices, send_command, broadcast_command
    from result_control import latest_device_result, format_execution_result
    from device_monitor import device_signature, detect_device_changes
    from command_history import history
    from activity_timeline import build_timeline, format_timeline
    from persistent_activity import PersistentActivityStore
    from activity_search import filter_activity
    from activity_selection import select_activity, activity_labels
    from activity_navigation import previous_index, next_index, navigation_state
    from activity_summary import format_activity_summary
    from activity_export import export_activity_json
    from activity_refresh import activity_signature, detect_activity_changes
    from activity_notifications import build_activity_notification, format_activity_notification
    from notification_manager import NotificationManager
    from notification_persistence import NotificationPersistence
    from notification_filter import filter_notifications, available_notification_types
    from notification_priority import sort_notifications
    from notification_grouping import group_notifications, format_notification_groups
    from notification_read_state import mark_notification_read, mark_notification_unread, unread_count, format_read_state
    from activity_details import format_activity_details

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
        self.activity_monitor_after_id = None
        self.activity_monitor_signature = ()
        self.activity_notification = None
        self.notification_manager = NotificationManager()
        self.notification_query = ""
        self.notification_type = "ALL"
        self.notification_sort = "HIGH"
        self.notification_grouped = True
        self.notification_persistence = NotificationPersistence()
        for item in self.notification_persistence.load():
            self.notification_manager.add(item)
        self.monitor_signature = {}
        self.persistent_history = PersistentActivityStore()
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
            self.stop_activity_monitor()
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
        ctk.CTkLabel(self.page,text="Activity search",font=("Arial",13,"bold")).pack(anchor="w",padx=25,pady=(8,3))
        search_row=ctk.CTkFrame(self.page,fg_color="transparent")
        search_row.pack(fill="x",padx=25,pady=4)
        search_row.grid_columnconfigure(0,weight=1)
        self.activity_query=ctk.CTkEntry(search_row,placeholder_text="search commands or responses")
        self.activity_query.grid(row=0,column=0,sticky="ew",padx=(0,8))
        self.activity_filter=ctk.CTkOptionMenu(search_row,values=["ALL","completed","failed","pending"],width=120,command=lambda _: self.refresh_command_history())
        self.activity_filter.set("ALL")
        self.activity_filter.grid(row=0,column=1,padx=(0,8))
        ctk.CTkButton(search_row,text="SEARCH",width=90,command=self.refresh_command_history).grid(row=0,column=2)
        ctk.CTkLabel(self.page,text="Activity summary",font=( "Arial",13,"bold")).pack(anchor="w",padx=25,pady=(8,3))
        self.activity_summary_label=ctk.CTkLabel(self.page,text="Total: 0 | Completed: 0 | Failed: 0 | Pending: 0",anchor="w",justify="left")
        self.activity_summary_label.pack(fill="x",padx=25,pady=(0,5))
        self.activity_notification_label=ctk.CTkLabel(self.page,text="No new activity.",anchor="w",justify="left")
        self.activity_notification_label.pack(fill="x",padx=25,pady=(0,5))
        self.notification_count_label=ctk.CTkLabel(self.page,text="Notifications: 0 - Unread: 0",anchor="w")
        self.notification_count_label.pack(fill="x",padx=25,pady=(0,3))
        notification_filter_row=ctk.CTkFrame(self.page,fg_color="transparent")
        notification_filter_row.pack(fill="x",padx=25,pady=(0,5))
        notification_filter_row.grid_columnconfigure(0,weight=1)
        self.notification_query_entry=ctk.CTkEntry(notification_filter_row,placeholder_text="search notifications")
        self.notification_query_entry.grid(row=0,column=0,sticky="ew",padx=(0,8))
        self.notification_type_menu=ctk.CTkOptionMenu(notification_filter_row,values=["ALL"],width=120,command=lambda _: self.refresh_notification_panel())
        self.notification_type_menu.set("ALL")
        self.notification_type_menu.grid(row=0,column=1,padx=(0,8))
        self.notification_sort_menu=ctk.CTkOptionMenu(notification_filter_row,values=["HIGH","LOW"],width=120,command=lambda _: self.refresh_notification_panel())
        self.notification_sort_menu.set("HIGH")
        self.notification_sort_menu.grid(row=0,column=2,padx=(0,8))
        self.notification_group_menu=ctk.CTkOptionMenu(notification_filter_row,values=["GROUPED","INDIVIDUAL"],width=130,command=lambda _: self.refresh_notification_panel())
        self.notification_group_menu.set("GROUPED")
        self.notification_group_menu.grid(row=0,column=3,padx=(0,8))
        ctk.CTkButton(notification_filter_row,text="SEARCH",width=90,command=self.refresh_notification_panel).grid(row=0,column=4)
        self.notification_box=ctk.CTkTextbox(self.page,height=90)
        self.notification_box.pack(fill="x",padx=25,pady=(0,5))
        self.notification_box.configure(state="disabled")
        notification_actions=ctk.CTkFrame(self.page,fg_color="transparent")
        notification_actions.pack(fill="x",padx=25,pady=(0,8))
        ctk.CTkButton(notification_actions,text="MARK LATEST READ",width=150,height=34,command=lambda: self.set_latest_notification_read(True)).pack(side="left",padx=(0,8))
        ctk.CTkButton(notification_actions,text="MARK LATEST UNREAD",width=165,height=34,command=lambda: self.set_latest_notification_read(False)).pack(side="left",padx=(0,8))
        ctk.CTkButton(notification_actions,text="DISMISS LATEST",width=140,height=34,command=self.dismiss_latest_notification).pack(side="left",padx=(0,8))
        ctk.CTkButton(notification_actions,text="CLEAR ALL",width=110,height=34,command=self.clear_notifications).pack(side="left")
        ctk.CTkLabel(self.page,text="Activity timeline",font=("Arial",13,"bold")).pack(anchor="w",padx=25,pady=(8,3))
        self.timeline_box=ctk.CTkTextbox(self.page,height=120)
        self.timeline_box.pack(fill="x",padx=25,pady=(0,8))
        self.timeline_box.configure(state="disabled")
        ctk.CTkButton(self.page,text="LATEST DETAILS",height=36,command=self.show_latest_activity_details).pack(anchor="w",padx=25,pady=(2,10))
        self.activity_selector=ctk.CTkOptionMenu(self.page,values=["No activity"],width=360,command=self.select_activity_from_label)
        self.activity_selector.set("No activity")
        self.activity_selector.pack(anchor="w",padx=25,pady=(2,5))
        navigation_row=ctk.CTkFrame(self.page,fg_color="transparent")
        navigation_row.pack(fill="x",padx=25,pady=(2,5))
        self.previous_activity_button=ctk.CTkButton(navigation_row,text="PREVIOUS",width=110,height=34,command=self.show_previous_activity)
        self.previous_activity_button.pack(side="left",padx=(0,8))
        self.activity_position_label=ctk.CTkLabel(navigation_row,text="0 / 0",width=90)
        self.activity_position_label.pack(side="left",padx=8)
        self.next_activity_button=ctk.CTkButton(navigation_row,text="NEXT",width=110,height=34,command=self.show_next_activity)
        self.next_activity_button.pack(side="left",padx=8)
        ctk.CTkButton(self.page,text="SELECTED DETAILS",height=36,command=self.show_selected_activity_details).pack(anchor="w",padx=25,pady=(0,10))
        ctk.CTkButton(self.page,text="EXPORT JSON",height=36,command=self.export_current_activity).pack(anchor="w",padx=25,pady=(0,10))
        self.refresh_devices()
        self.start_device_monitor()
        self.start_activity_monitor()

    def start_activity_monitor(self):
        self.stop_activity_monitor()
        device_id=self.selected_device.get().strip()
        items=self.persistent_history.recent(device_id, limit=100) if device_id else []
        self.activity_monitor_signature=activity_signature(items)
        self.activity_monitor_after_id=self.root.after(2000, self._poll_activity_monitor)

    def stop_activity_monitor(self):
        if self.activity_monitor_after_id is not None:
            try:
                self.root.after_cancel(self.activity_monitor_after_id)
            except Exception:
                pass
            self.activity_monitor_after_id=None

    def _poll_activity_monitor(self):
        self.activity_monitor_after_id=None
        if self.page_title.get() != "DEVICES":
            return
        try:
            device_id=self.selected_device.get().strip()
            items=self.persistent_history.recent(device_id, limit=100) if device_id else []
            current=activity_signature(items)
            if detect_activity_changes(self.activity_monitor_signature,current):
                notification=build_activity_notification(self.activity_monitor_signature,current)
                self.activity_notification=notification
                self.notification_manager.add(notification)
                self.notification_persistence.save(self.notification_manager.recent(limit=100))
                if hasattr(self,"activity_notification_label"):
                    self.activity_notification_label.configure(text=format_activity_notification(notification))
                self.activity_monitor_signature=current
                self.refresh_command_history(device_id)
            else:
                self.activity_monitor_signature=current
        except Exception as e:
            self.command_result.configure(text="Activity monitor error: {}".format(e))
        finally:
            if self.page_title.get() == "DEVICES":
                self.activity_monitor_after_id=self.root.after(2000,self._poll_activity_monitor)

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
        self.refresh_command_history(device_id)
        items=self.persistent_history.recent(device_id, limit=100)
        self.activity_monitor_signature=activity_signature(items)

    def refresh_command_history(self, device_id=None):
        if device_id is None:
            device_id = self.selected_device.get().strip()
        if not device_id:
            return
        items = self.persistent_history.recent(device_id, limit=100)
        query = self.activity_query.get().strip() if hasattr(self, "activity_query") else ""
        selected_outcome = self.activity_filter.get() if hasattr(self, "activity_filter") else "ALL"
        items = filter_activity(items, query=query, outcome=None if selected_outcome == "ALL" else selected_outcome)
        items = items[-8:]
        self.activity_items = list(items)
        if hasattr(self, "activity_summary_label"):
            self.activity_summary_label.configure(text=format_activity_summary(self.activity_items))
        self.activity_labels = activity_labels(self.activity_items)
        self.activity_index = len(self.activity_items) - 1 if self.activity_items else None
        if hasattr(self, "activity_selector"):
            self.activity_selector.configure(values=self.activity_labels or ["No activity"])
            self.activity_selector.set(self.activity_labels[self.activity_index] if self.activity_index is not None else "No activity")
            self.update_activity_navigation()
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
        timeline=build_timeline(items, limit=8)
        self.timeline_box.configure(state="normal")
        self.timeline_box.delete("1.0", "end")
        self.timeline_box.insert("1.0", format_timeline(timeline))
        self.timeline_box.configure(state="disabled")

    def show_latest_activity_details(self):
        if not self.activity_items:
            self.command_result.configure(text="No activity details available.")
            return
        popup=ctk.CTkToplevel(self.root)
        popup.title("FRIDAY Activity Details")
        popup.geometry("650x380")
        popup.transient(self.root)
        ctk.CTkLabel(popup,text="Activity Details",font=("Arial",20,"bold")).pack(pady=(20,10))
        box=ctk.CTkTextbox(popup,height=260)
        box.pack(fill="both",expand=True,padx=20,pady=10)
        box.insert("1.0",format_activity_details(self.activity_items[-1]))
        box.configure(state="disabled")
        ctk.CTkButton(popup,text="CLOSE",width=100,command=popup.destroy).pack(pady=(0,15))
    def update_activity_navigation(self):
        state=navigation_state(self.activity_index if self.activity_index is not None else 0,len(self.activity_items))
        if hasattr(self,"activity_position_label"):
            position="0 / 0" if state["index"] is None else "{} / {}".format(state["index"]+1,state["count"])
            self.activity_position_label.configure(text=position)
        if hasattr(self,"previous_activity_button"):
            self.previous_activity_button.configure(state="normal" if state["has_previous"] else "disabled")
        if hasattr(self,"next_activity_button"):
            self.next_activity_button.configure(state="normal" if state["has_next"] else "disabled")

    def select_activity_from_label(self, label):
        labels=getattr(self,"activity_labels",[])
        if label in labels:
            self.activity_index=labels.index(label)
            self.update_activity_navigation()

    def show_previous_activity(self):
        if self.activity_index is None:
            return
        self.activity_index=previous_index(self.activity_index,len(self.activity_items))
        self.update_selected_activity_view()

    def show_next_activity(self):
        if self.activity_index is None:
            return
        self.activity_index=next_index(self.activity_index,len(self.activity_items))
        self.update_selected_activity_view()

    def update_selected_activity_view(self):
        if self.activity_index is None or not self.activity_items:
            self.update_activity_navigation()
            return
        label=self.activity_labels[self.activity_index]
        self.activity_selector.set(label)
        self.update_activity_navigation()

    def refresh_notification_panel(self):
        all_items=self.notification_manager.recent(limit=100)
        sort_mode=self.notification_sort_menu.get() if hasattr(self,"notification_sort_menu") else "HIGH"
        all_items=sort_notifications(all_items, descending=sort_mode=="HIGH")
        types=available_notification_types(all_items)
        values=["ALL"]+types
        if hasattr(self,"notification_type_menu"):
            self.notification_type_menu.configure(values=values)
            current=self.notification_type_menu.get()
            if current not in values:
                self.notification_type_menu.set("ALL")
        query=self.notification_query_entry.get().strip() if hasattr(self,"notification_query_entry") else ""
        selected_type=self.notification_type_menu.get() if hasattr(self,"notification_type_menu") else "ALL"
        items=filter_notifications(all_items,query=query,notification_type=None if selected_type=="ALL" else selected_type)
        self.notification_count_label.configure(text="Notifications: {} - Unread: {}".format(self.notification_manager.count(), unread_count(all_items)))
        grouped=hasattr(self,"notification_group_menu") and self.notification_group_menu.get()=="GROUPED"
        if grouped:
            groups=group_notifications(items)
            text=format_notification_groups(groups)
        else:
            lines=[]
            for item in reversed(items):
                lines.append("[{}] {}".format(format_read_state(item), format_activity_notification(item)))
            text=chr(10).join(lines) if lines else "No matching notifications."
        self.notification_box.configure(state="normal")
        self.notification_box.delete("1.0","end")
        self.notification_box.insert("1.0",text if text else "No matching notifications.")
        self.notification_box.configure(state="disabled")

    def set_latest_notification_read(self, read=True):
        count=self.notification_manager.count()
        if count <= 0:
            self.command_result.configure(text="No notifications to update.")
            return
        latest=self.notification_manager.recent(limit=1)[0]
        updated=mark_notification_read(latest) if read else mark_notification_unread(latest)
        latest.clear()
        latest.update(updated)
        self.notification_persistence.save(self.notification_manager.recent(limit=100))
        self.refresh_notification_panel()
        self.command_result.configure(text="Latest notification marked {}.".format("read" if read else "unread"))

    def dismiss_latest_notification(self):
        count=self.notification_manager.count()
        if count <= 0:
            self.command_result.configure(text="No notifications to dismiss.")
            return
        self.notification_manager.dismiss(count-1)
        self.notification_persistence.save(self.notification_manager.recent(limit=100))
        self.refresh_notification_panel()
        self.command_result.configure(text="Latest notification dismissed.")

    def clear_notifications(self):
        removed=self.notification_manager.clear()
        self.notification_persistence.clear()
        self.refresh_notification_panel()
        self.command_result.configure(text="Cleared {} notification{}.".format(len(removed),"" if len(removed)==1 else "s"))

    def export_current_activity(self):
        from pathlib import Path
        output=Path("data/frontend_activity_export.json")
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(export_activity_json(getattr(self,"activity_items",[])),encoding="utf-8")
        self.command_result.configure(text="Activity exported: {}".format(output))

    def show_selected_activity_details(self):
        label = self.activity_selector.get().strip()
        labels = getattr(self, "activity_labels", [])
        if not label or label == "No activity" or label not in labels:
            self.command_result.configure(text="Select an activity to view details.")
            return
        index = labels.index(label)
        item = select_activity(self.activity_items, index)
        if item is None:
            self.command_result.configure(text="Selected activity is unavailable.")
            return
        popup=ctk.CTkToplevel(self.root)
        popup.title("FRIDAY Activity Details")
        popup.geometry("650x380")
        popup.transient(self.root)
        ctk.CTkLabel(popup,text="Selected Activity",font=("Arial",20,"bold")).pack(pady=(20,10))
        box=ctk.CTkTextbox(popup,height=260)
        box.pack(fill="both",expand=True,padx=20,pady=10)
        box.insert("1.0",format_activity_details(item))
        box.configure(state="disabled")
        ctk.CTkButton(popup,text="CLOSE",width=100,command=popup.destroy).pack(pady=(0,15))
    def record_command_history(self, device_id, command):
        try:
            result = latest_device_result(device_id) or {}
            history.add(device_id, command, result)
            self.persistent_history.add(device_id, command, result)
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
