"""
_mod_slides.py
14. December 2023

one single mod

Author:
Nilusink
"""
from .._analyzer import ModCollection, Mod
import customtkinter as ctk


class SubFolder(ctk.CTkFrame):
    def __init__(
            self,
            name: str,
            parent: ctk.CTkScrollableFrame,
            *args,
            **kwargs
    ) -> None:
        self.name = name
        self.parent = parent

        if "fg_color" in kwargs:
            kwargs.pop("fg_color")

        super().__init__(
            parent,
            *args,
            fg_color=self.parent.cget("fg_color"),
            **kwargs
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text=name).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=5
        )


class MissingMod(ctk.CTkFrame):
    def __init__(
            self,
            mod: ModCollection,
            parent: ctk.CTkScrollableFrame,
            *args,
            **kwargs
    ) -> None:
        self.mod = mod
        self.parent = parent

        if "fg_color" in kwargs:
            kwargs.pop("fg_color")

        super().__init__(
            parent,
            *args,
            fg_color="red",
            **kwargs
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=mod.name,
            text_color="white"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=5
        )

        ctk.CTkLabel(
            self,
            text="missing",
            text_color="white",
        ).grid(
            row=0,
            column=1,
            sticky="e",
            padx=20,
            pady=5
        )

        ctk.CTkLabel(
            self,
            text="",
            text_color="white",
            width=50
        ).grid(
            row=0,
            column=2,
            sticky="e",
            padx=20,
            pady=5
        )


class UniqueMod(ctk.CTkFrame):
    def __init__(
            self,
            mod: ModCollection,
            parent: ctk.CTkScrollableFrame,
            *args,
            **kwargs
    ) -> None:
        self.mod = mod
        self.parent = parent

        if "fg_color" in kwargs:
            kwargs.pop("fg_color")

        super().__init__(
            parent,
            *args,
            fg_color="green",
            **kwargs
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=mod.name,
            text_color="white"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=5
        )

        ctk.CTkLabel(
            self,
            text="unique",
            text_color="white",
        ).grid(
            row=0,
            column=1,
            sticky="e",
            padx=20,
            pady=5
        )

        ctk.CTkLabel(
            self,
            text=",".join(mod.versions),
            text_color="white",
            width=50
        ).grid(
            row=0,
            column=2,
            sticky="e",
            padx=20,
            pady=5
        )


class UpdateProvider(ctk.CTkFrame):
    def __init__(
            self,
            mod: Mod,
            parent: ctk.CTkScrollableFrame,
            *args,
            **kwargs
    ) -> None:
        self.mod = mod
        self.parent = parent

        if "fg_color" in kwargs:
            kwargs.pop("fg_color")

        super().__init__(
            parent,
            *args,
            fg_color="green",
            **kwargs
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=mod.name,
            text_color="white"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=5
        )

        ctk.CTkLabel(
            self,
            text="new version",
            text_color="white",
        ).grid(
            row=0,
            column=1,
            sticky="e",
            padx=20,
            pady=5
        )

        ctk.CTkLabel(
            self,
            text=mod.version,
            text_color="white",
            width=50
        ).grid(
            row=0,
            column=2,
            sticky="e",
            padx=20,
            pady=5
        )


class UpdateConsumer(ctk.CTkFrame):
    def __init__(
            self,
            mod: ModCollection,
            parent: ctk.CTkScrollableFrame,
            *args,
            **kwargs
    ) -> None:
        self.mod = mod
        self.parent = parent

        if "fg_color" in kwargs:
            kwargs.pop("fg_color")

        super().__init__(
            parent,
            *args,
            fg_color="blue",
            **kwargs
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=mod.name,
            text_color="white"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=5
        )

        ctk.CTkLabel(
            self,
            text="old version",
            text_color="white",
        ).grid(
            row=0,
            column=1,
            sticky="e",
            padx=20,
            pady=5
        )

        ctk.CTkLabel(
            self,
            text=",".join(mod.versions),
            text_color="white",
            width=50
        ).grid(
            row=0,
            column=2,
            sticky="e",
            padx=20,
            pady=5
        )


class Duplicate(ctk.CTkFrame):
    def __init__(
            self,
            mod: ModCollection,
            parent: ctk.CTkScrollableFrame,
            *args,
            **kwargs
    ) -> None:
        self.mod = mod
        self.parent = parent

        if "fg_color" in kwargs:
            kwargs.pop("fg_color")

        super().__init__(
            parent,
            *args,
            fg_color="orange",
            **kwargs
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=mod.name,
            text_color="white"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=5
        )

        ctk.CTkLabel(
            self,
            text="duplicate",
            text_color="white",
        ).grid(
            row=0,
            column=1,
            sticky="e",
            padx=20,
            pady=5
        )

        ctk.CTkLabel(
            self,
            text=",".join(mod.versions),
            text_color="white",
            width=50
        ).grid(
            row=0,
            column=2,
            sticky="e",
            padx=20,
            pady=5
        )


class Placeholder(ctk.CTkFrame):
    def __init__(
            self,
            parent: ctk.CTkScrollableFrame,
            *args,
            **kwargs
    ) -> None:
        self.parent = parent

        if "fg_color" in kwargs:
            kwargs.pop("fg_color")

        super().__init__(
            parent,
            *args,
            fg_color=self.parent.cget("fg_color"),
            **kwargs
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="",
            text_color="white"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=5
        )
