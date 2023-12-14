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


@dataclass(frozen=True)
class DiffResult:
    unique_subs: list[str]
    unique_per_sub: dict[str, list[ModCollection]]
    duplicates: dict[str, list[ModCollection]]
    updates: dict[str, list[tuple[Mod, ModCollection]]]


# helper functions
def max_version(*versions: str) -> str:
    """
    gets the max version
    """
    return ".".join(
        map(str, max((tuple(map(int, v.split(".")))) for v in versions))
    )


def find_uniques[T](a: tp.Iterable[T], b: tp.Iterable[T]) -> list[T]:
    """
    compare two lists and get the unique items from list a

    :param a: list to get the uniques from
    :param b: list to compare to
    """
    return [f for f in a if f not in b]


def filter_list[T](li: tp.Iterable[T], item: str) -> list:
    """
    ([<class: a=1, b=2>, <class: a=4, b=3>], a) => [1, 2]

    :param li: input list
    :param item: item to filter
    """
    return [element.__getattribute__(item) for element in li]


def find_uniques_and_updates(
        a: tp.Iterable[ModCollection],
        b: tp.Iterable[ModCollection]
) -> tuple[
    tuple[list[ModCollection], list[tuple[Mod, ModCollection]]],
    tuple[list[ModCollection], list[tuple[Mod, ModCollection]]]
]:
    """
    find uniques and updates

    :returns: ( (a_uniques, a_updates), (b_uniques, b_updates) )
    """
    # prerequisites
    a_names: list[str] = filter_list(a, "name")
    b_names: list[str] = filter_list(b, "name")

    all_mods = list(set(a_names) | set(b_names))
    both = list(set(a_names) & set(b_names))

    a_dict: dict[str, ModCollection] = {
        name: value for name, value in zip(a_names, a)
    }
    b_dict: dict[str, ModCollection] = {
        name: value for name, value in zip(b_names, b)
    }

    # filter uniques and updates
    a_uniques: list[ModCollection] = []
    b_uniques: list[ModCollection] = []

    a_updates: list[tuple[Mod, ModCollection]] = []
    b_updates: list[tuple[Mod, ModCollection]] = []

    for mod_name in all_mods:
        a_mod = a_dict[mod_name]
        b_mod = b_dict[mod_name]

        if mod_name not in a_names:
            b_uniques.append(b_mod)

        if mod_name not in b_names:
            a_uniques.append(a_mod)

        # check for updates
        if mod_name in both:
            a_versions = set(a_mod.versions)
            b_versions = set(b_mod.versions)

            # different versions
            if a_versions != b_versions:
                # check who has the highest version
                highest = max_version(
                    *a_versions,
                    *b_versions
                )

                # both have the same highest version
                if highest in a_versions and highest in b_versions:
                    continue

                if highest in a_versions:
                    # set correct folder path (version number)
                    folder_name = a_mod.folder_name.replace(
                        a_mod.versions[0],
                        highest
                    )

                    a_updates.append((
                        Mod(a_mod.name, highest, folder_name, a_mod.size),
                        b_mod
                    ))

                if highest in b_versions:
                    # set correct folder path (version number)
                    folder_name = b_mod.folder_name.replace(
                        b_mod.versions[0],
                        highest
                    )

                    b_updates.append((
                        Mod(b_mod.name, highest, folder_name, b_mod.size),
                        a_mod
                    ))

    return (
        (a_uniques, a_updates),
        (b_uniques, b_updates)
    )


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

    __is_parsed: bool

    def __init__(self, directory: str) -> None:
        self.__is_parsed = False
        self._directory = directory
        self._mods_per_sub = {}

    @property
    def directory(self) -> str:
        return self._directory

    @directory.setter
    def directory(self, value: str) -> None:
        self._directory = value
        self.__is_parsed = False

    @property
    def mods_per_sub(self) -> mods_collection_t:
        return self._mods_per_sub.copy()

    @property
    def is_parsed(self) -> bool:
        """
        returns true if `parse` has at least been called once
        """
        return self.__is_parsed

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

        self.__is_parsed = True

    def diff(
            self, other: tp.Self,
            print_results: bool = False
    ) -> tuple[DiffResult, DiffResult]:
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
        own_updates_per_sub: dict[str, list[tuple[Mod, ModCollection]]] = {
            sub: [] for sub in common_folders
        }

        other_unique_per_sub = own_unique_per_sub.copy()
        other_updates_per_sub = own_updates_per_sub.copy()

        for sub_folder in common_folders:
            own_mods = self.mods_per_sub[sub_folder]
            other_mods = other.mods_per_sub[sub_folder]

            # find uniques (using the folders name)
            match_result = find_uniques_and_updates(
                own_mods.values(),
                other_mods.values()
            )

            own_mods_unique, own_updates = match_result[0]
            other_mods_unique, other_updates = match_result[1]

            own_unique_per_sub[sub_folder] = own_mods_unique
            own_updates_per_sub[sub_folder] = own_updates

            other_unique_per_sub[sub_folder] = other_mods_unique
            other_updates_per_sub[sub_folder] = other_updates

            if print_results:
                print(
                    f"unique mods in {sub_folder} (self): {own_mods_unique}\n"
                    f"updates in {sub_folder} (self): {own_updates}"
                )
                print(
                    f"unique mods in {sub_folder} (other): {other_mods_unique}\n"
                    f"updates in {sub_folder} (other): {other_updates}"
                )

        own = DiffResult(
            own_sub_unique,
            own_unique_per_sub,
            own_duplicates,
            own_updates_per_sub
        )

        other = DiffResult(
            other_sub_unique,
            other_unique_per_sub,
            other_duplicates,
            other_updates_per_sub
        )

        return own, other

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

        own_unique_sub = own_changes.unique_subs
        own_unique_mods = own_changes.unique_per_sub

        other_unique_sub = other_changes.unique_subs
        other_unique_mods = other_changes.unique_per_sub

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
