"""
_gui.py
14. December 2023

GUI for the analyzer

Author:
Nilusink
"""
from concurrent.futures import ThreadPoolExecutor
from ._analyzed_folder import AnalyzedFolder
from ._tooltip_button import TooltipButton
from ._console_popup import ConsolePopup
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

        # top bar
        self.top_bar = ctk.CTkFrame(self, height=80, corner_radius=20)
        self.top_bar.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="nsew",
            padx=20,
            pady=20
        )

        self.top_bar.grid_rowconfigure(0, weight=1)
        self.top_bar.grid_columnconfigure(list(range(20)), weight=1)

        duplicate = ctk.CTkImage(Image.open("./icons/duplicate.png"))
        solution = ctk.CTkImage(Image.open("./icons/problem-solving.png"))
        duplicate_resolve = ctk.CTkImage(Image.open("./icons/duplicate_resolve.png"))
        reload = ctk.CTkImage(Image.open("./icons/reload.png"))

        TooltipButton(
            self.top_bar,
            tip="remove duplicates",
            image=duplicate,
            text="",
            width=60,
            command=self._run_duplicates
        ).grid(
            row=0,
            column=0,
            pady=10,
        )

        TooltipButton(
            self.top_bar,
            tip="resolve uniques & updates",
            image=solution,
            text="",
            width=60,
            command=self._run_resolve
        ).grid(
            row=0,
            column=1,
            pady=10,
        )

        TooltipButton(
            self.top_bar,
            tip="duplicates & resolve",
            image=duplicate_resolve,
            text="",
            width=60,
            command=self._run_all
        ).grid(
            row=0,
            column=2,
            pady=10,
        )

        TooltipButton(
            self.top_bar,
            tip="re-parse and compare",
            image=reload,
            text="",
            width=60,
            command=self.reload_mods
        ).grid(
            row=0,
            column=19,
            pady=10,
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
        double_arrow = Image.open("./icons/right-arrow.png")

        l_arrow = arrow.rotate(180)
        dl_arrow = double_arrow.rotate(180)

        right_arrow = ctk.CTkImage(arrow)
        left_arrow = ctk.CTkImage(l_arrow)

        double_right_arrow = ctk.CTkImage(double_arrow)
        double_left_arrow = ctk.CTkImage(dl_arrow)

        TooltipButton(
            self,
            tip="write to usb & delete uniques",
            image=double_right_arrow,
            text="",
            width=50,
            command=lambda: self._run_oneway(False, True)
        ).grid(
            row=4,
            column=1
        )
        TooltipButton(
            self,
            tip="write to usb",
            image=right_arrow,
            text="",
            width=50,
            command=lambda: self._run_oneway(False, False)
        ).grid(
            row=5,
            column=1
        )
        TooltipButton(
            self,
            tip="write to saved games",
            image=left_arrow,
            text="",
            width=50,
            command=lambda: self._run_oneway(True, False)
        ).grid(
            row=7,
            column=1
        )
        TooltipButton(
            self,
            tip="write to saved games & delete uniques",
            image=double_left_arrow,
            text="",
            width=50,
            command=lambda: self._run_oneway(True, True)
        ).grid(
            row=8,
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

        # reload scrollbars
        # self.dcs_frame.mods_frame._scrollbar.configure(command=self.set_scrollbars)
        # self.usb_frame.mods_frame._scrollbar.configure(command=self.set_scrollbars)
        #
        self.__init_done = True
    #
    # def set_scrollbars(self, *args) -> None:
    #     print(f"(debug): scrolling {args}")
    #     self.dcs_frame.mods_frame._scrollbar.yview(*args)
    #     self.dcs_frame.mods_frame._parent_canvas.yview(*args)
    #
    #     self.usb_frame.mods_frame._scrollbar.yview(*args)
    #     self.usb_frame.mods_frame._parent_canvas.yview(*args)

    def reload_mods(self) -> None:
        """
        forces both analyzers to reload
        """
        for side in self._side_status:
            self._side_status[side] = False

            side.set_path(side.analyzer.directory)

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
        if not self.__init_done:
            return

        if side in self._side_status:
            self._side_status[side] = status

            if all(self._side_status.values()):
                def run_analysis():
                    analysis = self.dcs_frame.analyzer.diff(
                        self.usb_frame.analyzer,
                    )

                    self.dcs_frame.on_analysis(*analysis)
                    self.usb_frame.on_analysis(*analysis[::-1])

                self._run_with_debug(run_analysis)

    def _run_duplicates(self) -> None:
        console_toplevel = ConsolePopup(self, "Resolving Duplicates")

        self._pool.submit(lambda: self.dcs_frame.analyzer.delete_duplicates(
            self.usb_frame.analyzer,
            console_toplevel.print
        ))

    def _run_resolve(self) -> None:
        console_toplevel = ConsolePopup(self, "Resolving Duplicates")

        self._pool.submit(lambda: self.dcs_frame.analyzer.resolve(
            self.usb_frame.analyzer,
            console_toplevel.print
        ))

    def _run_all(self) -> None:
        console_toplevel = ConsolePopup(self, "Resolving Duplicates")

        self._pool.submit(lambda: self.dcs_frame.analyzer.delete_duplicates(
            self.usb_frame.analyzer,
            console_toplevel.print
        ))
        self._pool.submit(lambda: self.dcs_frame.analyzer.resolve(
            self.usb_frame.analyzer,
            console_toplevel.print
        ))

    def _run_with_debug[T, R](
            self,
            func: tp.Callable[[T], R],
            *args: tp.Unpack[T],
            **kwargs: tp.Unpack[T]
    ) -> None:
        def run_func():
            print(f"(debug): running {func.__name__}, "
                  f"args: {args}, kwargs: {kwargs}")
            try:
                func(*args, **kwargs)
                print(f"(debug): {func.__name__} finished successfully")

            except Exception as e:
                print(f"(debug): {func.__name__} exception: {e}")
                raise

        self._pool.submit(run_func)

    def _run_oneway(self, side: bool, delete: bool = True) -> None:
        """
        :param side: 0: Saved Games to USB, 1: USB to Saved Games
        """
        if side == 0:
            console_toplevel = ConsolePopup(
                self,
                "Syncing from Saved Games to USB"
            )

            self._run_with_debug(
                self.dcs_frame.analyzer.sync_one_way,
                self.usb_frame.analyzer,
                delete_unique=delete,
                debug_func=console_toplevel.print
            )

        elif side == 0:
            console_toplevel = ConsolePopup(
                self,
                "Syncing from USB to Saved Games"
            )

            self._run_with_debug(
                self.usb_frame.analyzer.sync_one_way,
                self.dcs_frame.analyzer,
                delete_unique=delete,
                debug_func=console_toplevel.print
            )

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
