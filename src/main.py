import sys

import main_training
import main_search
import main_monitor


def launch_mode(mode):
    if mode == 1:
        print("Entering Training Mode")
        main_training.main()
        sys.exit()
    elif mode == 2:
        print("Entering Search & Record Mode")
        main_search.main()
        sys.exit()
    elif mode == 3:
        print("Entering Monitoring & Analysis mode")
        main_monitor.main()
        sys.exit()
    elif mode == 9:
        print("Quitting")
        sys.exit()
    else:
        print("Your choice was not recognized.\n Please retry")


print("_" * 40)
print("Welcome in WoW Backend Interface")
print("Please choose an execution mode : ")
print("1. Train ML Algorithm")
print("2. Search & Record water areas")
print("3. Monitor & Analyse water area")
print("9. Quit")

while True:
    try:
        exec_mode = int(input("Please choose execution mode \n"))
        launch_mode(exec_mode)
    except ValueError:
        print("Your choice was not recognized.\n Please retry")
