"""
_analyzed_folder.py
14. December 2023

displays the mods

Author:
Nilusink
"""
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog
import customtkinter as ctk
import typing as tp
import os

from .._analyzer import Analyzer, DiffResult
from ._mod_slides import *


if tp.TYPE_CHECKING:
    from ._gui import ModManagerGUI


class AnalyzedFolder(ctk.CTkFrame):
    analyzer: Analyzer

    def __init__(
            self,
            master: "ModManagerGUI",
            set_path: tp.Callable[[tp.Self, str], None],
            path: str | None = None,
            **kwargs
    ) -> None:
        self.parent = master
        self.path = path
        self._path_exists: bool = False

        self._set_path_callback = set_path

        # create thread pool (for parsing directories)
        self._pool = ThreadPoolExecutor(max_workers=1)

        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.path_entry = ctk.CTkEntry(self)
        self.path_entry.grid(
            row=0,
            column=0,
            padx=40,
            pady=20,
            sticky="ew"
        )

        if path is not None:
            self.path_entry.insert(0, path)

        def choose_folder(*_):
            value = filedialog.askdirectory(title="DCS Saved Games Directory")
            self.set_path(value)

        ctk.CTkButton(
            self,
            text="Choose",
            command=choose_folder
        ).grid(
            row=0,
            column=1,
            padx=40,
            pady=20
        )

        # statistics
        self.statistics_text = ctk.StringVar(value="")
        ctk.CTkLabel(self, textvariable=self.statistics_text).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            pady=1,
            padx=50
        )

        self.analyzer = Analyzer(...)
        self.set_path(path)

        # mods
        self.mods_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=self.cget("corner_radius")
        )
        self.mods_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=20,
            pady=20,
        )

    def set_path(self, value: str) -> None:
        """
        set a new path
        """
        if value != self.path:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, value)
            self._set_path_callback(self, value)
            self.path = value

        if os.path.isdir(value):
            self.analyzer.directory = value
            self._path_exists = True

            self.statistics_text.set("analysing...")

            def change_on_done() -> None:
                """
                change content when the thread is done
                """
                try:
                    self.analyzer.parse()

                except Exception as e:
                    print(f"thread exception: {e}")
                    raise

                # parse information
                total_size = 0
                all_mods: list = []

                for sub in self.analyzer.mods_per_sub:
                    for mod in self.analyzer.mods_per_sub[sub].values():
                        all_mods.append(total_size)

                        total_size += mod.size

                # statistics label
                self.statistics_text.set(
                    f"Installed Mods: {len(all_mods)} "
                    f"({round(total_size / 1024**3, 2)} GB)"
                )

                self.parent.set_side_status(self, True)

            self._pool.submit(change_on_done)

            return

        else:
            self.statistics_text.set("not found")
            self.parent.set_side_status(self, False)

            # automatically check if the directory exists in 2 seconds
            # -> could be an usb-stick that isn't yet plugged in
            self.after(2000, lambda *_: self.set_path(value))

        self._path_exists = False

    def on_analysis(
            self,
            own: DiffResult,
            other: DiffResult
    ) -> None:
        """
        Show changes between two folders.
        Since .diff is ran by the parent, the results need to be passed.
        """
        # delete all old widgets
        for child in self.mods_frame.children.values():
            child.pack_forget()

        all_sub_folders = list(
            set(own.unique_per_sub.keys())
            | set(other.unique_per_sub.keys())
        )
        all_sub_folders.sort()

        changes_per_sub: dict[str, int] = {}
        for sub in all_sub_folders:
            total = len(own.unique_per_sub[sub])
            total += len(other.unique_per_sub[sub])
            total += len(own.updates[sub])
            total += len(other.updates[sub])
            total += len(own.duplicates[sub])
            total += len(other.duplicates[sub])

            changes_per_sub[sub] = total

        for sub_folder in all_sub_folders:
            if changes_per_sub[sub_folder] > 0:
                SubFolder(
                    sub_folder,
                    self.mods_frame
                ).pack(
                    side="top",
                    fill="x"
                )

                own_uniques_dict = {
                    mod.name: mod for mod in own.unique_per_sub[sub_folder]
                }
                own_updates_dict = {
                    mod[0].name: mod for mod in own.updates[sub_folder]
                }
                own_duplicates_dict = {
                    mod.name: mod for mod in own.duplicates[sub_folder]
                }

                other_uniques_dict = {
                    mod.name: mod for mod in other.unique_per_sub[sub_folder]
                }
                other_updates_dict = {
                    mod[0].name: mod for mod in other.updates[sub_folder]
                }
                other_duplicates_dict = {
                    mod.name: mod for mod in other.duplicates[sub_folder]
                }

                all_in_sub = list(
                    set(own_uniques_dict.keys())
                    | set(own_updates_dict.keys())
                    | set(own_duplicates_dict.keys())
                    | set(other_uniques_dict.keys())
                    | set(other_updates_dict.keys())
                    | set(other_duplicates_dict.keys())
                )
                all_in_sub.sort()

                print(f"{sub_folder}, all: {all_in_sub}")

                for mod in all_in_sub:
                    widget: ctk.CTkFrame

                    if mod in own_uniques_dict:
                        widget = UniqueMod(
                            own_uniques_dict[mod],
                            self.mods_frame
                        )

                    elif mod in other_uniques_dict:
                        widget = MissingMod(
                            other_uniques_dict[mod],
                            self.mods_frame
                        )

                    elif mod in own_updates_dict:
                        widget = UpdateProvider(
                            own_updates_dict[mod][0],
                            self.mods_frame
                        )

                    elif mod in other_updates_dict:
                        widget = UpdateConsumer(
                            other_updates_dict[mod][1],
                            self.mods_frame
                        )

                    elif mod in own_duplicates_dict:
                        widget = Duplicate(
                            own_duplicates_dict[mod],
                            self.mods_frame
                        )

                    elif mod in other_duplicates_dict:
                        widget = Placeholder(
                            self.mods_frame
                        )

                    else:
                        continue

                    widget.pack(
                        side="top",
                        fill="x",
                        pady=(5, 0)
                    )
