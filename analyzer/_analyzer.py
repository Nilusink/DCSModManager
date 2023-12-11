"""
_analyzer.py
11. December 2023

automatically restarts ssh-tunnels

Author:
Nilusink
"""
import typing as tp
import shutil
import os


def find_uniques[T](a: tp.Iterable[T], b: tp.Iterable[T]) -> list[T]:
    """
    compare two lists and get the unique items from list a

    :param a: list to get the uniques from
    :param b: list to compare to
    """
    return [f for f in a if f not in b]


class Analyzer:
    _directory: str
    _mods_per_sub: dict[str, list[str]]

    def __init__(self, directory: str) -> None:
        self._directory = directory

        self._mods_per_sub = {}

    @property
    def directory(self) -> str:
        return self._directory

    @property
    def mods_per_sub(self) -> dict[str, list[str]]:
        return self._mods_per_sub.copy()

    def parse(self) -> None:
        """
        parse the directory
        """
        sub_folders = [
            f for f in os.listdir(self._directory) if not f.startswith(".")
        ]

        if len(sub_folders) < 1:
            print("no mods found!")
            return

        for sub_folder in sub_folders:
            mods = os.listdir(os.path.join(self._directory, sub_folder))
            mods = [f for f in mods if not f.startswith(".")]

            if len(mods) < 1:
                print(f"no mods found in \"{sub_folder}\"")
                continue

            self._mods_per_sub[sub_folder] = mods

    def diff(
            self, other: tp.Self,
            print_results: bool = False
    ) -> tuple[
        tuple[list[str], dict[str, list[str]]],
        tuple[list[str], dict[str, list[str]]]
    ]:
        """
        compare two directories

        :param other: the Analyzer instance to compare against
        :param print_results: whether to print the results of the analysis

        :returns: (unique sub-folders, unique mods) to self,
            (unique sub-folders, unique mods) to other
        """
        own_sub_folders = self.mods_per_sub.keys()
        other_sub_folders = other.mods_per_sub.keys()

        own_sub_unique = find_uniques(own_sub_folders, other_sub_folders)
        other_sub_unique = find_uniques(other_sub_folders, own_sub_folders)

        common_folders = list(set(own_sub_folders) & set(other_sub_folders))

        own_unique_per_sub: dict[str, list[str]] = {
            sub: [] for sub in common_folders
        }
        other_unique_per_sub: dict[str, list[str]] = {
            sub: [] for sub in common_folders
        }

        if print_results:
            print(f"unique (self): {own_sub_unique}")
            print(f"unique (other): {other_sub_unique}")
            print(f"common: {common_folders}")

        for sub_folder in common_folders:
            own_mods = self.mods_per_sub[sub_folder]
            other_mods = other.mods_per_sub[sub_folder]

            own_mods_unique = find_uniques(own_mods, other_mods)
            other_mods_unique = find_uniques(other_mods, own_mods)

            own_unique_per_sub[sub_folder] = own_mods_unique
            other_unique_per_sub[sub_folder] = other_mods_unique

            if print_results:
                print(f"unique mods in {sub_folder} (self): {own_mods_unique}")
                print(
                    f"unique mods in {sub_folder} (other): {other_mods_unique}"
                )

        return (
            (own_sub_unique, own_unique_per_sub),
            (other_sub_unique, other_unique_per_sub)
        )

    def resolve(self, other: tp.Self) -> None:
        """
        resolve conflicts
        :param other:
        """
        own_changes, other_changes = self.diff(other)

        own_unique_sub, own_unique_mods = own_changes
        other_unique_sub, other_unique_mods = other_changes

        # copy unique sub-folders
        for sub in own_unique_sub:
            origin = os.path.join(self.directory, sub)
            dest = os.path.join(other.directory, sub)

            print(f"copying \"{origin}\" to \"{dest}\"")
            shutil.copytree(origin, dest)

        for sub in other_unique_sub:
            origin = os.path.join(other.directory, sub)
            dest = os.path.join(self.directory, sub)

            print(f"copying \"{origin}\" to \"{dest}\"")
            shutil.copytree(origin, dest)

        # copy mods
        for sub_folder, mods in own_unique_mods.items():
            for mod in mods:
                origin = os.path.join(self.directory, sub_folder, mod)
                dest = os.path.join(other.directory, sub_folder, mod)

                print(f"copying \"{origin}\" to \"{dest}\"")
                shutil.copytree(origin, dest)

        for sub_folder, mods in other_unique_mods.items():
            for mod in mods:
                origin = os.path.join(other.directory, sub_folder, mod)
                dest = os.path.join(self.directory, sub_folder, mod)

                print(f"copying \"{origin}\" to \"{dest}\"")
                shutil.copytree(origin, dest)
