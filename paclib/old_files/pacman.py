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


choice: str | None = "play"

while choice != "exit":
    choice = paclib.HomePage.start()
