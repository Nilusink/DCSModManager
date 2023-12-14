"""
cli.py
11. December 2023

automatically syncs two folders (in this case for DCS)

Author:
Nilusink
"""
from analyzer import Analyzer
from tkinter import filedialog
import os


CLR_RESET = "\033[1;0m"
STL_BOLD = "\033[1;1m"
CLR_RED = "\033[0;31m"
CLR_GREEN = "\033[0;32m"
CLR_BLUE = "\033[0;34m"


def main() -> int:
    os.system("color")  # enable colored terminal on windows

    dcs_valid = True
    usb_valid = True

    dcs_directory: str = filedialog.askdirectory(title="DCS Saved Games Directory")
    usb_directory: str = filedialog.askdirectory(title="Mods USB Directory")

    # check if directories exist
    if not os.path.exists(dcs_directory):
        print("invalid DCS directory")
        dcs_valid = False

    if not os.path.exists(usb_directory):
        print("invalid USB directory")
        usb_valid = False

    if dcs_valid and usb_valid:
        dcs = Analyzer(dcs_directory)
        usb = Analyzer(usb_directory)

        print("parsing DCS...")
        dcs.parse()

        print("parsing USB...")
        usb.parse()

        # compare
        dcs_diff, usb_diff = dcs.diff(usb, True)

        # print duplicates
        print(f"\n\n##### analysis result #####\n")
        if sum(
                [len(mod) for sub in dcs_diff.duplicates
                 for mod in dcs_diff.duplicates[sub]]
                + [len(mod) for sub in usb_diff.duplicates
                   for mod in usb_diff.duplicates[sub]]
        ) > 0:
            print(f"##### duplicates #####\n")
            print("(DCS)")
            for sub in dcs_diff.duplicates:
                print(f"\t* {sub}")
                for mod in dcs_diff.duplicates [sub]:
                    print(f"{CLR_BLUE}\t\t- {mod.name} "
                          f"({', '.join(mod.versions)}){CLR_RESET}")

            print("\n(USB)")
            for sub in usb_diff.duplicates:
                print(f"\t* {sub}")
                for mod in usb_diff.duplicates[sub]:
                    print(f"{CLR_BLUE}\t\t- {mod.name} "
                          f"({', '.join(mod.versions)}){CLR_RESET}")

            while True:
                ans = input("\nAutomatically resolve duplicates? (y/n): ")

                if ans.lower() == "y":
                    print("\ndeleting duplicates...")
                    dcs.delete_duplicates(usb)

                    # re-run the analysis
                    print("parsing DCS...")
                    dcs.parse()

                    print("parsing USB...")
                    usb.parse()

                    dcs_diff, usb_diff = dcs.diff(usb, False)

                    print(f"\n{CLR_GREEN}duplicates resolved "
                          f"successfully!{CLR_RESET}")
                    break

                elif ans.lower() == "n":
                    print("leaving... ")
                    break

                else:
                    print("please type either \"y\" to continue, "
                          "or \"n\" to cancel")

        # print results
        # print unique folders
        if len(dcs_diff.unique_subs) + len(usb_diff.unique_subs) < 1:
            if all([
                sum([len(dcs_diff.unique_per_sub[sub]) for sub in dcs_diff.unique_per_sub]) < 1,
                sum([len(usb_diff.unique_per_sub[sub]) for sub in usb_diff.unique_per_sub]) < 1,
                sum([len(dcs_diff.updates[sub]) for sub in dcs_diff.updates]) < 1,
                sum([len(usb_diff.updates[sub]) for sub in usb_diff.updates]) < 1,
            ]):
                print(f"\n{CLR_GREEN}Everything synced!{CLR_RESET}")
                return 0

        print(f"\n\n##### unsynced #####\n")
        for sub in dcs_diff.unique_per_sub:
            print(f"{CLR_GREEN}\t+ {sub}{CLR_RESET}")

        for sub in usb_diff.unique_per_sub:
            print(f"{CLR_RED}\t- {sub}{CLR_RESET}")

        # print mod differences
        for sub in dcs_diff.unique_per_sub.keys():
            print(f"\t* {sub}")
            for mod in dcs_diff.unique_per_sub[sub]:
                print(
                    f"{CLR_GREEN}\t\t+ {mod.name} "
                    f"({round(mod.size / (1024**3), 2)} GB){CLR_RESET}"
                )

            for update in usb_diff.updates[sub]:
                print(
                    f"{CLR_GREEN}\t\t+ {update[1].name} "
                    f"({','.join(update[1].versions)}) => {update[0].version} "
                    f"({round(update[0].size / (1024**3), 2)} GB){CLR_RESET}"
                )

            for mod in usb_diff.unique_per_sub[sub]:
                print(
                    f"{CLR_RED}\t\t- {mod.name} "
                    f"({round(mod.size / (1024**3), 2)} GB){CLR_RESET}"
                )

            for update in dcs_diff.updates[sub]:
                print(
                    f"{CLR_RED}\t\t+ {update[1].name} "
                    f"({','.join(update[1].versions)}) => {update[0].version} "
                    f"({round(update[0].size / (1024**3), 2)} GB){CLR_RESET}"
                )

        total_changed_size = sum([
            *[mod.size for sub in dcs_diff.unique_per_sub
              for mod in usb_diff.unique_per_sub[sub]],
            *[mod.size for sub in usb_diff.unique_per_sub
              for mod in dcs_diff.unique_per_sub[sub]],
        ])

        while True:
            ans = input(
                f"\nAutomatically resolve your changes "
                f"(total: {round(total_changed_size / (1024**3), 2)} GB)? "
                f"(y/n): "
            )

            if ans.lower() == "y":
                print("\nstarting copy")
                dcs.resolve(usb)
                print(f"\n{CLR_GREEN}resolved successfully{CLR_RESET}")
                return 0

            elif ans.lower() == "n":
                print("leaving... ")
                return 0

            else:
                print("please type either \"y\" to continue, "
                      "or \"n\" to cancel")

    return 1


if __name__ == "__main__":
    rc = main()

    input("\n\nPress enter to exit")
    exit(rc)

