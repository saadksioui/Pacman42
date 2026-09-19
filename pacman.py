from paclib import HomePage


def main():
    try:
        HomePage().start()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
