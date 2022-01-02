import json


def read_settings():
    with open("algorand-settings.json") as json_file:
        data = json.load(json_file)
        return data


def main():
    settings = read_settings()
    print(settings)


if __name__ == "__main__":
    main()
