"""
_analyzer.py
11. December 2023

analyzes a folder

Author:
Nilusink
"""
from dataclasses import dataclass
from pathlib import Path
import typing as tp
import shutil
import re
import os


# dataclasses
@dataclass(frozen=False)
class Mod:
    name: str
    version: str
    folder_name: str
    size: int


@dataclass(frozen=True)
class ModCollection:
    name: str
    versions: list[str]
    folder_name: str
    size: int

    def __len__(self) -> int:
        return len(self.versions)


# types
type mods_collection_t = dict[str, dict[str, ModCollection]]
type diff_result_t = tuple[
            list[str],
            dict[str, list[ModCollection]],
            dict[str, list[ModCollection]]
]


# helper functions
def find_uniques[T](a: tp.Iterable[T], b: tp.Iterable[T]) -> list[T]:
    """
    compare two lists and get the unique items from list a

    :param a: list to get the uniques from
    :param b: list to compare to
    """
    return [f for f in a if f not in b]


def name_and_version(s: str) -> Mod:
    """
    separate mod name and version

    :param s: version structure: a.b.c
    :return:
    """
    try:
        ver = re.search(r"\d+\.\d+\.\d+", s).group()

    except AttributeError:
        ver = ""

    return Mod(s.strip(ver).lstrip("CH ").rstrip().lstrip(), ver, s, 0)


def max_version(*versions: str) -> str:
    """
    gets the max version
    """
    return ".".join(
        map(str, max((tuple(map(int, v.split(".")))) for v in versions))
    )


def get_directory_size(directory: str) -> int:
    """
    get the size of a directory

        credits: https://stackoverflow.com/users/24718/monkut

    :param directory: starting directory
    """
    root_directory = Path(directory)
    return sum(
        f.stat().st_size for f in root_directory.glob('**/*') if f.is_file()
    )


class Analyzer:
    _directory: str

    # structure: {"sub_module": {"mod": <Mod: name, version, folder_name}}
    _mods_per_sub: mods_collection_t

    def __init__(self, directory: str) -> None:
        self._directory = directory

        self._mods_per_sub = {}

    @property
    def directory(self) -> str:
        return self._directory

    @property
    def mods_per_sub(self) -> mods_collection_t:
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

            self._mods_per_sub[sub_folder] = {}

            for mod in mods:
                vmod = name_and_version(mod)
                vmod.size = get_directory_size(os.path.join(
                    self._directory,
                    sub_folder,
                    vmod.folder_name
                ))

                if vmod.name in self._mods_per_sub[sub_folder]:
                    self._mods_per_sub[sub_folder][vmod.name].versions.append(
                        vmod.version
                    )
                    continue

                self._mods_per_sub[sub_folder][vmod.name] = ModCollection(
                    vmod.name, [vmod.version], vmod.folder_name, vmod.size
                )

    def diff(
            self, other: tp.Self,
            print_results: bool = False
    ) -> tuple[diff_result_t, diff_result_t]:
        """
        compare two directories

        :param other: the Analyzer instance to compare against
        :param print_results: whether to print the results of the analysis

        :returns: (unique sub-folders, unique mods, duplicates) to self,
            (unique sub-folders, unique mods, duplicates) to other
        """
        own_sub_folders = self.mods_per_sub.keys()
        other_sub_folders = other.mods_per_sub.keys()

        own_sub_unique = find_uniques(own_sub_folders, other_sub_folders)
        other_sub_unique = find_uniques(other_sub_folders, own_sub_folders)

        common_folders = list(set(own_sub_folders) & set(other_sub_folders))

        # find duplicates
        own_duplicates: dict[str, list[ModCollection]] = {
            sub: [] for sub in common_folders
        }
        other_duplicates: dict[str, list[ModCollection]] = {
            sub: [] for sub in common_folders
        }

        for sub_folder in own_sub_folders:
            for mod in self.mods_per_sub[sub_folder]:
                if len(self.mods_per_sub[sub_folder][mod].versions) > 1:
                    own_duplicates[sub_folder].append(
                        self.mods_per_sub[sub_folder][mod]
                    )

        for sub_folder in other_sub_folders:
            for mod in other.mods_per_sub[sub_folder]:
                if len(other.mods_per_sub[sub_folder][mod].versions) > 1:
                    other_duplicates[sub_folder].append(
                        other.mods_per_sub[sub_folder][mod]
                    )

        if print_results:
            print(f"unique (self): {own_sub_unique}")
            print(f"unique (other): {other_sub_unique}")
            print(f"common: {common_folders}")

        # cross-match mods
        own_unique_per_sub: dict[str, list[ModCollection]] = {
            sub: [] for sub in common_folders
        }
        other_unique_per_sub: dict[str, list[ModCollection]] = {
            sub: [] for sub in common_folders
        }
        for sub_folder in common_folders:
            own_mods = self.mods_per_sub[sub_folder]
            other_mods = other.mods_per_sub[sub_folder]

            # find uniques (using the folders name)
            tmp_own_mods_unique = find_uniques(
                [mod.name for mod in own_mods.values()],
                [mod.name for mod in other_mods.values()]
            )
            tmp_other_mods_unique = find_uniques(
                [mod.name for mod in other_mods.values()],
                [mod.name for mod in own_mods.values()]
            )

            # replace the name with the classes
            own_mods_unique: list = []
            other_mods_unique: list = []

            for mod in own_mods.values():
                if mod.name in tmp_own_mods_unique:
                    own_mods_unique.append(mod)

            for mod in other_mods.values():
                if mod.name in tmp_other_mods_unique:
                    other_mods_unique.append(mod)

            own_unique_per_sub[sub_folder] = own_mods_unique
            other_unique_per_sub[sub_folder] = other_mods_unique

            if print_results:
                print(f"unique mods in {sub_folder} (self): {own_mods_unique}")
                print(
                    f"unique mods in {sub_folder} (other): {other_mods_unique}"
                )

        return (
            (own_sub_unique, own_unique_per_sub, own_duplicates),
            (other_sub_unique, other_unique_per_sub, other_duplicates)
        )

    def delete_duplicates(self, other: tp.Self) -> None:
        """
        delete all duplicates
        """
        (*_, own_duplicates), (*_, other_duplicates) = self.diff(other)
        other_duplicates: dict[str, list[ModCollection]]
        own_duplicates: dict[str, list[ModCollection]]

        for sub_folder, mods in own_duplicates.items():
            for mod in mods:
                highest_version = max_version(*mod.versions)

                for version in mod.versions:
                    if version != highest_version:
                        folder_path = os.path.join(
                            self.directory,
                            sub_folder,
                            mod.folder_name.replace(mod.versions[0], version)
                        )

                        print(f"deleting {folder_path}")
                        shutil.rmtree(folder_path)

        for sub_folder, mods in other_duplicates.items():
            for mod in mods:
                highest_version = max_version(*mod.versions)

                for version in mod.versions:
                    if version != highest_version:
                        folder_path = os.path.join(
                            other.directory,
                            sub_folder,
                            mod.folder_name.replace(mod.versions[0], version)
                        )

                        print(f"deleting {folder_path}")
                        shutil.rmtree(folder_path)

    def resolve(self, other: tp.Self) -> None:
        """
        resolve conflicts
        """
        own_changes, other_changes = self.diff(other)

        own_unique_sub, own_unique_mods, _ = own_changes
        other_unique_sub, other_unique_mods, _ = other_changes

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
                origin = os.path.join(
                    self.directory,
                    sub_folder,
                    mod.folder_name
                )
                dest = os.path.join(
                    other.directory,
                    sub_folder,
                    mod.folder_name
                )

                print(
                    f"copying \"{origin}\" to \"{dest}\" "
                    f"(size: {round(mod.size / (1024**3), 2)} GB)"
                )
                shutil.copytree(origin, dest)

        for sub_folder, mods in other_unique_mods.items():
            for mod in mods:
                origin = os.path.join(
                    other.directory,
                    sub_folder,
                    mod.folder_name
                )
                dest = os.path.join(
                    self.directory,
                    sub_folder,
                    mod.folder_name
                )

                print(
                    f"copying \"{origin}\" to \"{dest}\" "
                    f"(size: {round(mod.size / (1024**3), 2)} GB)"
                )
                shutil.copytree(origin, dest)


if __name__ == "__main__":
    print(max_version("1.1.0", "0.1.0", "1.2.0", "2.0.0", "2.0.1", "2.1.0"))
