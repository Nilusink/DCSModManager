"""
_gui.py
14. December 2023

GUI for the analyzer

Author:
Nilusink
"""
from concurrent.futures import ThreadPoolExecutor
from ._analyzed_folder import AnalyzedFolder
from pydantic import BaseModel
import customtkinter as ctk
from PIL import Image
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
        # fixes things
        self.__init_done = False

        self._pool = ThreadPoolExecutor(max_workers=1)

        # load configuration
        self.load_config()

        print(self._settings)

        # window settings
        super().__init__(*args, **kwargs)

        self.title("DCS Mod Manager")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.geometry("1000x800")

        self.grid_columnconfigure((0, 2), weight=1)
        self.grid_rowconfigure(list(range(1, 12)), weight=1)

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
        self.dcs_frame = AnalyzedFolder(
            self,
            self.set_path,
            self._settings.dcs_saved_games_folder,
            corner_radius=20,
        )
        self.dcs_frame.grid(
            row=1,
            column=0,
            rowspan=11,
            sticky="nsew",
            padx=20,
            pady=20
        )

        # center buttons
        arrow = Image.open("./icons/straight-right-arrow.png")
        sync = Image.open("./icons/synchronization.png")
        l_arrow = arrow.rotate(180)

        right_arrow = ctk.CTkImage(arrow)
        left_arrow = ctk.CTkImage(l_arrow)

        sync_arrow = ctk.CTkImage(sync)

        ctk.CTkButton(self, image=right_arrow, text="", width=50).grid(
            row=5,
            column=1
        )
        ctk.CTkButton(self, image=sync_arrow, text="", width=50).grid(
            row=6,
            column=1
        )
        ctk.CTkButton(self, image=left_arrow, text="", width=50).grid(
            row=7,
            column=1
        )

        # usb frame
        self.usb_frame = AnalyzedFolder(
            self,
            self.set_path,
            self._settings.usb_mods_folder,
            corner_radius=20,
        )
        self.usb_frame.grid(
            row=1,
            column=2,
            rowspan=11,
            sticky="nsew",
            padx=20,
            pady=20
        )

        self._side_status = {
            self.dcs_frame: False,
            self.usb_frame: False
        }

        self.__init_done = True

    def set_path(
            self,
            instance: AnalyzedFolder,
            value: str
    ) -> None:
        if self.__init_done:
            if instance is self.dcs_frame:
                self._settings.dcs_saved_games_folder = value

            elif instance is self.usb_frame:
                self._settings.usb_mods_folder = value

            self._save_config()

    def set_side_status(self, side: AnalyzedFolder, status: bool) -> None:
        """
        sets the sides status (if .parse is complete)
        """
        if side in self._side_status:
            self._side_status[side] = status

            if all(self._side_status.values()):
                def run_analysis():
                    analysis = self.dcs_frame.analyzer.diff(
                        self.usb_frame.analyzer
                    )

                    self.dcs_frame.on_analysis(*analysis)
                    self.usb_frame.on_analysis(*analysis[::-1])

                self._pool.submit(run_analysis)

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
