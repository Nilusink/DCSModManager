"""
_console_popup.py
18. December 2023

just what it sounds like: a pop-up window with a console

Author:
Nilusink
"""
import customtkinter as ctk


class ConsolePopup(ctk.CTkToplevel):
    def __init__(
            self,
            parent,
            title: str,
            *args,
            **kwargs
    ) -> None:
        self.parent = parent

        super().__init__(parent, *args, **kwargs)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.geometry("600x1000")
        self.title(title)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=title,
            font=("Helvetica", 20)
        ).grid(row=0, column=0, pady=10)

        self._text = ctk.CTkTextbox(self)
        self._text.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )
        self._text.configure(state="disabled")

    def print(self, *args: str, end="\n") -> None:
        """
        prints into the textbox
        """
        for string in args:
            self._text.configure(state="normal")
            self._text.insert(ctk.END, string + end)
            self._text.configure(state="disabled")

    def on_close(self) -> None:
        """
        tell parent to reload on close
        """
        self.parent.reload_mods()

        self.destroy()
