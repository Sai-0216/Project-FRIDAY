"""
Project FRIDAY
Graphical User Interface
"""

import customtkinter as ctk

from datetime import date



class FridayGUI:

    # ============================================
    # INITIALIZATION
    # ============================================

    def __init__(self):

        # ----------------------------------------
        # Appearance
        # ----------------------------------------

        ctk.set_appearance_mode(
            "dark"
        )

        ctk.set_default_color_theme(
            "blue"
        )

        # ----------------------------------------
        # Main Window
        # ----------------------------------------

        self.root = ctk.CTk()

        self.root.title(
            "FRIDAY"
        )

        self.root.geometry(
            "1200x750"
        )

        self.root.minsize(
            1000,
            650
        )

        # ----------------------------------------
        # Title
        # ----------------------------------------

        title = ctk.CTkLabel(
            self.root,
            text="FRIDAY",
            font=("Arial", 36, "bold")
        )

        title.pack(
            pady=(20, 5)
        )

        # ----------------------------------------
        # Status
        # ----------------------------------------

        self.status = ctk.CTkLabel(
            self.root,
            text="Status : Idle",
            font=("Arial", 18)
        )

        self.status.pack(
            pady=(0, 15)
        )

        # ----------------------------------------
        # Main Content
        # ----------------------------------------

        self.content = ctk.CTkFrame(
            self.root,
            corner_radius=15
        )

        self.content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.content.grid_columnconfigure(
            0,
            weight=3
        )

        self.content.grid_columnconfigure(
            1,
            weight=1
        )

        self.content.grid_rowconfigure(
            0,
            weight=1
        )

        # ========================================
        # CHAT SECTION
        # ========================================

        self.chat_frame = ctk.CTkFrame(
            self.content,
            corner_radius=12
        )

        self.chat_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(10, 5),
            pady=10
        )

        chat_title = ctk.CTkLabel(
            self.chat_frame,
            text="Conversation",
            font=("Arial", 20, "bold")
        )

        chat_title.pack(
            pady=(15, 5)
        )

        self.chat = ctk.CTkTextbox(
            self.chat_frame,
            width=700,
            height=550,
            font=("Arial", 14)
        )

        self.chat.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(5, 15)
        )

        self.chat.configure(
            state="disabled"
        )

        # ========================================
        # HABIT SECTION
        # ========================================

        self.habit_frame = ctk.CTkFrame(
            self.content,
            corner_radius=12
        )

        self.habit_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(5, 10),
            pady=10
        )

        habit_title = ctk.CTkLabel(
            self.habit_frame,
            text="📅 HABITS",
            font=("Arial", 22, "bold")
        )

        habit_title.pack(
            pady=(15, 5)
        )

        self.progress_label = ctk.CTkLabel(
            self.habit_frame,
            text="Today's Progress: 0 / 0",
            font=("Arial", 14)
        )

        self.progress_label.pack(
            pady=(5, 10)
        )

        # ----------------------------------------
        # Habit List
        # ----------------------------------------

        self.habit_list = ctk.CTkScrollableFrame(
            self.habit_frame,
            width=300,
            height=400
        )

        self.habit_list.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        # ----------------------------------------
        # Refresh Button
        # ----------------------------------------

        refresh_button = ctk.CTkButton(
            self.habit_frame,
            text="🔄 Refresh",
            command=self.refresh_habits
        )

        refresh_button.pack(
            fill="x",
            padx=10,
            pady=(5, 15)
        )

        # ----------------------------------------
        # Initial Habit Load
        # ----------------------------------------

        self.refresh_habits()

    # ============================================
    # CHAT
    # ============================================

    def add_message(
        self,
        sender,
        message
    ):

        self.chat.configure(
            state="normal"
        )

        self.chat.insert(
            "end",
            f"{sender}: {message}\n\n"
        )

        self.chat.configure(
            state="disabled"
        )

        self.chat.see(
            "end"
        )

    # ============================================
    # THREAD-SAFE CHAT
    # ============================================

    def add_message_threadsafe(
        self,
        sender,
        message
    ):

        try:

            self.root.after(
                0,
                lambda: self.add_message(
                    sender,
                    message
                )
            )

        except Exception as e:

            print(
                "[GUI] Thread-safe message error:",
                repr(e)
            )

    # ============================================
    # STATUS
    # ============================================

    def set_status(
        self,
        status
    ):

        try:

            self.status.configure(
                text=f"Status : {status}"
            )

        except Exception as e:

            print(
                "[GUI] Status error:",
                repr(e)
            )

    # ============================================
    # THREAD-SAFE STATUS
    # ============================================

    def set_status_threadsafe(
        self,
        status
    ):

        try:

            self.root.after(
                0,
                lambda: self.set_status(
                    status
                )
            )

        except Exception as e:

            print(
                "[GUI] Thread-safe status error:",
                repr(e)
            )

    # ============================================
    # CONFIRMATION DIALOG
    # ============================================

    def confirm(
        self,
        message
    ):

        # Brain runs in the assistant background thread.
        # Tkinter must create/update widgets on the GUI
        # main thread, so schedule the dialog with after().
        import threading

        result = {
            "confirmed": False
        }

        finished = threading.Event()
        expired = threading.Event()
        dialog_ref = {"dialog": None}

        def show_dialog():

            if expired.is_set():
                finished.set()
                return

            dialog = ctk.CTkToplevel(
                self.root
            )
            dialog_ref["dialog"] = dialog

            dialog.title(
                "FRIDAY Confirmation"
            )

            dialog.geometry(
                "520x250"
            )

            dialog.resizable(
                False,
                False
            )

            dialog.transient(
                self.root
            )

            dialog.grab_set()

            # ----------------------------------------
            # Message
            # ----------------------------------------

            title = ctk.CTkLabel(
                dialog,
                text="FRIDAY",
                font=("Arial", 24, "bold")
            )

            title.pack(
                pady=(25, 10)
            )

            question = ctk.CTkLabel(
                dialog,
                text=message,
                font=("Arial", 16),
                wraplength=450,
                justify="center"
            )

            question.pack(
                padx=25,
                pady=(0, 20)
            )

            # ----------------------------------------
            # Button handlers
            # ----------------------------------------

            def finish(
                confirmed
            ):

                if expired.is_set():
                    confirmed = False

                result["confirmed"] = confirmed

                try:

                    dialog.grab_release()

                except Exception:

                    pass

                dialog.destroy()

                finished.set()

            # ----------------------------------------
            # Buttons
            # ----------------------------------------

            button_frame = ctk.CTkFrame(
                dialog,
                fg_color="transparent"
            )

            button_frame.pack(
                fill="x",
                padx=30,
                pady=(0, 20)
            )

            no_button = ctk.CTkButton(
                button_frame,
                text="NO",
                height=40,
                command=lambda: finish(
                    False
                )
            )

            no_button.pack(
                side="left",
                expand=True,
                fill="x",
                padx=(0, 10)
            )

            yes_button = ctk.CTkButton(
                button_frame,
                text="YES",
                height=40,
                command=lambda: finish(
                    True
                )
            )

            yes_button.pack(
                side="right",
                expand=True,
                fill="x",
                padx=(10, 0)
            )

            dialog.protocol(
                "WM_DELETE_WINDOW",
                lambda: finish(False)
            )

            yes_button.focus_set()

        try:

            self.root.after(
                0,
                show_dialog
            )

            # Wait in the assistant thread, but never indefinitely.
            # An expired confirmation always fails closed.
            if not finished.wait(timeout=120):

                expired.set()

                def close_expired_dialog():

                    dialog = dialog_ref.get("dialog")

                    if dialog is not None:
                        try:
                            if dialog.winfo_exists():
                                dialog.grab_release()
                                dialog.destroy()
                        except Exception:
                            pass

                    result["confirmed"] = False
                    finished.set()

                try:
                    self.root.after(
                        0,
                        close_expired_dialog
                    )
                except Exception as e:
                    print(
                        "[GUI] Could not close expired confirmation:",
                        repr(e)
                    )

                return False

            return bool(
                result["confirmed"]
            )

        except Exception as e:

            print(
                "[GUI] Confirmation error:",
                repr(e)
            )

            return False

    # ============================================
    # SAFE GUI REFRESH
    # ============================================

    def refresh_habits_safe(
        self
    ):

        try:

            self.root.after(
                0,
                self.refresh_habits
            )

        except Exception as e:

            print(
                "[GUI] Habit refresh error:",
                repr(e)
            )

    # ============================================
    # REFRESH HABITS
    # ============================================

    def refresh_habits(
        self
    ):

        for widget in self.habit_list.winfo_children():

            widget.destroy()

        empty = ctk.CTkLabel(
            self.habit_list,
            text=(
                "Habit system unavailable.\n\n"
                "habit_tracker.py is not installed."
            ),
            font=("Arial", 13),
            justify="center"
        )

        empty.pack(
            pady=40
        )

        self.progress_label.configure(
            text="Today's Progress: 0 / 0"
        )

    # ============================================
    # HABIT CARD
    # ============================================

    def create_habit_card(
        self,
        name,
        habit,
        today
    ):

        card = ctk.CTkFrame(
            self.habit_list,
            corner_radius=10
        )

        card.pack(
            fill="x",
            pady=5,
            padx=2
        )

        completed = (
            habit.get(
                "last_completed"
            ) == today
        )

        # ----------------------------------------
        # Status
        # ----------------------------------------

        status = (
            "✅"
            if completed
            else "⬜"
        )

        title = ctk.CTkLabel(
            card,
            text=f"{status} {name}",
            font=("Arial", 15, "bold"),
            anchor="w"
        )

        title.pack(
            fill="x",
            padx=10,
            pady=(8, 2)
        )

        # ----------------------------------------
        # Streak
        # ----------------------------------------

        streak = ctk.CTkLabel(
            card,
            text=(
                f"🔥 "
                f"{habit.get('streak', 0)} "
                f"day streak"
            ),
            font=("Arial", 12),
            anchor="w"
        )

        streak.pack(
            fill="x",
            padx=10
        )

        # ----------------------------------------
        # Total
        # ----------------------------------------

        total = ctk.CTkLabel(
            card,
            text=(
                f"Completed: "
                f"{habit.get('total_completed', 0)} "
                f"times"
            ),
            font=("Arial", 11),
            anchor="w"
        )

        total.pack(
            fill="x",
            padx=10,
            pady=(0, 5)
        )

        # ----------------------------------------
        # Complete Button
        # ----------------------------------------

        if not completed:

            complete_button = ctk.CTkButton(
                card,
                text="✅ Complete",
                height=30,
                command=lambda h=name: (
                    self.complete_habit(h)
                )
            )

            complete_button.pack(
                fill="x",
                padx=10,
                pady=(0, 8)
            )

        else:

            done_label = ctk.CTkLabel(
                card,
                text="Completed today ✓",
                font=("Arial", 12)
            )

            done_label.pack(
                pady=(0, 8)
            )

    # ============================================
    # COMPLETE HABIT
    # ============================================

    def complete_habit(
        self,
        name
    ):

        self.add_message_threadsafe(
            "🤖 FRIDAY",
            "The habit system is not installed, Sir."
        )

    # ============================================
    # RUN GUI
    # ============================================

    def run(
        self
    ):

        self.root.mainloop()


# ============================================
# GLOBAL GUI INSTANCE
# ============================================

gui = FridayGUI()