"""
Project FRIDAY
Memory Module
"""

import json
from pathlib import Path

from command_manager import manager


class Memory:

    def __init__(self):

        self.file = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "memory.json"
        )

        # ========================================
        # CREATE DATA DIRECTORY
        # ========================================

        self.file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # ========================================
        # CREATE MEMORY FILE
        # ========================================

        if not self.file.exists():

            self.save({})

    # ========================================
    # LOAD MEMORY
    # ========================================

    def load(self):

        try:

            with open(
                self.file,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

                if isinstance(
                    data,
                    dict
                ):

                    return data

                return {}

        except (
            json.JSONDecodeError,
            FileNotFoundError
        ):

            return {}

    # ========================================
    # SAVE MEMORY
    # ========================================

    def save(
        self,
        data
    ):

        with open(
            self.file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

    # ========================================
    # REMEMBER
    # ========================================

    def remember(
        self,
        key,
        value
    ):

        key = clean_key(
            key
        )

        value = str(
            value
        ).strip()

        if not key or not value:

            return False

        data = self.load()

        data[key] = value

        self.save(
            data
        )

        return True

    # ========================================
    # RECALL
    # ========================================

    def recall(
        self,
        key
    ):

        key = clean_key(
            key
        )

        data = self.load()

        return data.get(
            key
        )

    # ========================================
    # FORGET
    # ========================================

    def forget(
        self,
        key
    ):

        key = clean_key(
            key
        )

        data = self.load()

        if key not in data:

            return False

        del data[key]

        self.save(
            data
        )

        return True

    # ========================================
    # ALL MEMORIES
    # ========================================

    def all(self):

        return self.load()


# ============================================
# MEMORY KEY CLEANER
# ============================================

def clean_key(
    text
):

    text = str(
        text
    ).strip().lower()

    # Remove punctuation from the end.
    #
    # Example:
    #
    # project?
    # project.
    # project!
    #
    # becomes:
    #
    # project

    text = text.rstrip(
        ".,!?;:"
    )

    return text.strip()


# ============================================
# MEMORY INSTANCE
# ============================================

memory = Memory()


# ============================================
# REMEMBER COMMAND
# ============================================

def remember_command(
    argument
):

    argument = str(
        argument
    ).strip()

    if not argument:

        return (
            "Tell me what you want me "
            "to remember."
        )

    text = argument

    # ----------------------------------------
    # Remove common prefixes
    # ----------------------------------------

    prefixes = [
        "that ",
        "this ",
    ]

    for prefix in prefixes:

        if text.lower().startswith(
            prefix
        ):

            text = text[
                len(prefix):
            ].strip()

    # ----------------------------------------
    # "X is Y"
    # ----------------------------------------

    if " is " in text:

        key, value = text.split(
            " is ",
            1
        )

    # ----------------------------------------
    # "X = Y"
    # ----------------------------------------

    elif "=" in text:

        key, value = text.split(
            "=",
            1
        )

    else:

        return (
            "Tell me what to remember "
            "using 'is'."
        )

    key = clean_key(
        key
    )

    value = str(
        value
    ).strip()

    if not key or not value:

        return (
            "I couldn't determine what "
            "to remember."
        )

    if memory.remember(
        key,
        value
    ):

        return (
            f"I'll remember that "
            f"{key} is {value}."
        )

    return (
        "I couldn't save that memory."
    )


# ============================================
# RECALL COMMAND
# ============================================

def recall_command(
    argument
):

    key = clean_key(
        argument
    )

    if not key:

        return (
            "Tell me what you want "
            "me to recall."
        )

    # ========================================
    # TRY EXACT KEY
    # ========================================

    value = memory.recall(
        key
    )

    # ========================================
    # TRY "MY <KEY>"
    # ========================================
    #
    # Example:
    #
    # User says:
    # "What is my project?"
    #
    # CommandManager sends:
    # "project?"
    #
    # clean_key() gives:
    # "project"
    #
    # But memory contains:
    # "my project"
    #
    # So we try both.
    #
    # ========================================

    if value is None:

        my_key = (
            f"my {key}"
        )

        value = memory.recall(
            my_key
        )

        if value is not None:

            key = my_key

    # ========================================
    # MEMORY NOT FOUND
    # ========================================

    if value is None:

        return (
            f"I don't have a memory "
            f"for {key}."
        )

    # ========================================
    # MEMORY FOUND
    # ========================================

    return (
        f"{key} is {value}."
    )


# ============================================
# FORGET COMMAND
# ============================================

def forget_command(
    argument
):

    key = clean_key(
        argument
    )

    if not key:

        return (
            "Tell me what you want "
            "me to forget."
        )

    # ========================================
    # TRY EXACT KEY
    # ========================================

    success = memory.forget(
        key
    )

    # ========================================
    # TRY "MY <KEY>"
    # ========================================

    if not success:

        my_key = (
            f"my {key}"
        )

        success = memory.forget(
            my_key
        )

        if success:

            key = my_key

    # ========================================
    # RESULT
    # ========================================

    if success:

        return (
            f"I've forgotten {key}."
        )

    return (
        f"I don't have a memory "
        f"for {key}."
    )


# ============================================
# SHOW ALL MEMORIES
# ============================================

def all_memory_command(
    argument=""
):

    data = memory.all()

    if not data:

        return (
            "I don't have any "
            "saved memories."
        )

    items = []

    for key, value in data.items():

        items.append(
            f"{key} is {value}"
        )

    return (
        "I remember: "
        + ", ".join(items)
        + "."
    )


# ============================================
# AUTOMATIC FACT CAPTURE
# ============================================

def remember_statement(text):

    text = str(text).strip()

    if not text.lower().startswith("my "):
        return False

    if " is " not in text.lower():
        return False

    left, value = text.split(" is ", 1)
    key = clean_key(left)
    value = str(value).strip()

    if not key or not value:
        return False

    if len(key) > 60 or len(value) > 120:
        return False

    # Avoid treating questions as facts.
    if "?" in value or key.endswith("?"):
        return False

    return memory.remember(key, value)


# ============================================
# COMMAND REGISTRATION
# ============================================

manager.register_prefix(
    "remember ",
    remember_command
)

manager.register_prefix(
    "save ",
    remember_command
)

manager.register_prefix(
    "recall ",
    recall_command
)

manager.register_prefix(
    "what is my ",
    recall_command
)

manager.register_prefix(
    "whats my ",
    recall_command
)

manager.register_prefix(
    "what's my ",
    recall_command
)

manager.register_prefix(
    "forget ",
    forget_command
)

manager.register_exact(
    "what do you remember",
    all_memory_command
)

manager.register_exact(
    "what do you remember about me",
    all_memory_command
)

manager.register_exact(
    "show my memories",
    all_memory_command
)