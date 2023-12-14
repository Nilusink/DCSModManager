"""
_gui.py
14. December 2023

GUI for the analyzer

Author:
Nilusink
"""
from pydantic import BaseModel
from .._analyzer import Analyzer
from tkinter import filedialog
import customtkinter as ctk
import typing as tp
import os


class Settings(BaseModel):
    """
    Settings for the GUI
    """
    dcs_saved_games_folder: tp.Optional[str] = None
    usb_mods_folder: tp.Optional[str] = None


class ModManagerGUI(ctk.CTk):
    settings_file: str = "settings.json"
    __ctk_initialized: bool = False

    _settings: Settings

    def __new__(cls, *args, **kwargs):
        # initialize CTK once
        if not cls.__ctk_initialized:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("dark-blue")

        return super().__new__(cls)

    def __init__(self, *args, **kwargs) -> None:
        # load configuration
        self.load_config()

        print(self._settings)

        # window settings
        super().__init__(*args, **kwargs)

        self.title("DCS Mod Manager")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.geometry("1000x800")

        self.grid_columnconfigure((0, 2), weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.top_bar = ctk.CTkFrame(self, height=80, corner_radius=20)
        self.top_bar.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="nsew",
            padx=20,
            pady=20
        )

        # dcs frame
        self.dcs_frame = ctk.CTkFrame(self, corner_radius=20)
        self.dcs_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=20
        )

        self.dcs_frame.grid_columnconfigure(0, weight=1)

        self.dcs_path_entry = ctk.CTkEntry(self.dcs_frame)
        self.dcs_path_entry.grid(
            row=0,
            column=0,
            padx=40,
            pady=20,
            sticky="ew"
        )

        if self._settings.dcs_saved_games_folder is not None:
            self.dcs_path_entry.insert(0, self._settings.dcs_saved_games_folder)

        def choose_dcs_folder(*_):
            self.set_path(
                "dcs",
                filedialog.askdirectory(title="DCS Saved Games Directory")
            )

        ctk.CTkButton(
            self.dcs_frame,
            text="Choose",
            command=choose_dcs_folder
        ).grid(
            row=0,
            column=1,
            padx=40,
            pady=20
        )

        # usb frame
        self.usb_frame = ctk.CTkFrame(self, corner_radius=20)
        self.usb_frame.grid(
            row=1,
            column=2,
            sticky="nsew",
            padx=20,
            pady=20
        )

    def set_path(self, f: tp.Literal["dcs", "usb"], value: str) -> None:
        if f == "dcs":
            self._settings.dcs_saved_games_folder = value
            self.dcs_path_entry.delete(0, ctk.END)
            self.dcs_path_entry.insert(0, value)

        elif f == "usb":
            self._settings.usb_saved_games_folder = value

        self._save_config()

    def load_config(self, path: str = ...) -> bool:
        """
        load settings from a file

        :param path: (optional): path to config file
        :return: True if the config was loaded successfully
        """
        self._settings = Settings()

        if path is ...:
            path = self.settings_file

        if not os.path.exists(path):
            return False

        with open(path, "r") as f:
            self._settings = Settings.model_validate_json(f.read())

        return True

    def _save_config(self) -> None:
        """
        save the current settings (called automatically)
        """
        with open(self.settings_file, "w") as f:
            f.write(self._settings.model_dump_json(indent=4))

    def close(self) -> None:
        """
        closes the mod manager (and saves)
        """
        self._save_config()
        self.destroy()
        exit(0)
