"""
main.py
11. December 2023

automatically syncs two folders (in this case for DCS)

Author:
Nilusink
"""
from analyzer import Analyzer
import os


CLR_RESET = "\033[1;0m"
STL_BOLD = "\033[1;1m"
CLR_RED = "\033[0;31m"
CLR_GREEN = "\033[0;32m"
CLR_BLUE = "\033[0;34m"


def main():
    dcs_valid = True
    usb_valid = True

    dcs_directory: str = input("DCS Saved Games Directory: ")
    usb_directory: str = input("Mods USB Directory: ")

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

        dcs.parse()
        usb.parse()

        # compare
        res = dcs.diff(usb)
        (dcs_sub_diff, dcs_mod_diff), (usb_sub_diff, usb_mod_diff) = res

        # print results
        print(f"\n\n##### analysis result #####")
        for sub in dcs_sub_diff:
            print(f"{CLR_GREEN}\t+ {sub}{CLR_RESET}")

        for sub in usb_sub_diff:
            print(f"{CLR_RED}\t- {sub}{CLR_RESET}")

        for sub in dcs_mod_diff.keys():
            print(f"\t* {sub}")
            for mod in dcs_mod_diff[sub]:
                print(f"{CLR_GREEN}\t\t+ {mod}{CLR_RESET}")

            for mod in usb_mod_diff[sub]:
                print(f"{CLR_RED}\t\t- {mod}{CLR_RESET}")

        while True:
            ans = input("\nAutomatically resolve your changes? (y/n): ")

            if ans.lower() == "y":
                print("\nstarting copy")
                dcs.resolve(usb)
                print(f"\n{CLR_GREEN}resolved successfully{CLR_RESET}")
                exit(0)

            elif ans.lower() == "n":
                print("leaving... ")
                exit(0)

            else:
                print("please type either \"y\" to continue, or \"n\" to cancel")


if __name__ == "__main__":
    main()
