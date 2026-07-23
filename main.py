import sys



if len(sys.argv) != 2:
    if len(sys.argv) == 1:
        print("no config file was provided")
    else:
        print("the program take exactly one argument")
    exit(1)
