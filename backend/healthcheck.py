from urllib.request import urlopen


def main():
    with urlopen(
        "http://127.0.0.1:5000/api/health",
        timeout=5,
    ) as response:
        if response.status != 200:
            raise SystemExit(1)


if __name__ == "__main__":
    main()