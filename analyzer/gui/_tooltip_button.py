"""
_tooltip_button.py
20. December 2023

a button with a tooltip

Author:
Nilusink
"""
import customtkinter as ctk
import tkinter as tk


class TooltipButton(ctk.CTkButton):
    def __init__(self, parent, tip: str, *args, **kwargs) -> None:
        self.tip = tip
        self.parent = parent
        self._menu: tk.Menu = ...

        super().__init__(parent, *args, **kwargs)

        self.bind("<Enter>", self.show)
        self.bind("<Leave>", self.hide)
        self.bind("<ButtonPress>", self.hide)

    def show(self, event) -> None:
        if self._menu is not ...:
            self.hide()

        x, y, cx, cy = self.bbox("insert")
        x += self.winfo_rootx() + 25 + event.x
        y += self.winfo_rooty() + 5 + event.y

        self._menu = tk.Toplevel(self)
        # Leaves only the label and removes the app window
        self._menu.wm_overrideredirect(True)
        self._menu.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            self._menu,
            text=self.tip,
            justify='left',
            background="#ffffff",
            relief='solid',
            borderwidth=1
        )
        label.pack(ipadx=1)

    def hide(self, *_event) -> None:
        if self._menu is not ...:
            self._menu.destroy()
            self._menu = ...


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("400x300")

    btn = TooltipButton(root, text="hellow", tip="this is a tooltip")
    btn.pack()

    root.mainloop()
