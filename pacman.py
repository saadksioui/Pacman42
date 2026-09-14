from pydantic import ValidationError # type: ignore
from paclib.errors import ArgumentError
from paclib import HomePage, CONFIG






def main():
    try:
        HomePage().start()
    except ValidationError as e:
        errors = e.errors()
        for err in errors:
            print(f"Error: {err['loc'][0]} ({err['type']}): {err['msg']}")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
