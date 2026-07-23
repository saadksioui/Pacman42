import sys
import paclib


if len(sys.argv) != 2:
    if len(sys.argv) == 1:
        print("no config file was provided")
    else:
        print("the program take exactly one argument")
    exit(1)


config = paclib.Config.get_config(sys.argv[1])
if config is None:
    exit(1)
