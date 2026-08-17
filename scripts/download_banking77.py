from pathlib import Path
import requests
import pandas as pd


OUTPUT_DIR = Path("datasets/banking77")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


FILES = {
    "train": "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/train.csv",
    "test": "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/test.csv",
}


def download_file(name, url):
    output_path = OUTPUT_DIR / f"{name}.csv"

    print(f"\nDownloading {name} dataset...")
    print(f"URL: {url}")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    output_path.write_bytes(response.content)

    print(f"Saved to: {output_path}")
    print(f"Size: {output_path.stat().st_size:,} bytes")


def verify_dataset():
    print("\nVerifying dataset...")

    train = pd.read_csv(OUTPUT_DIR / "train.csv")
    test = pd.read_csv(OUTPUT_DIR / "test.csv")

    print(f"\nTrain examples: {len(train)}")
    print(f"Test examples:  {len(test)}")

    print("\nColumns:")
    print(train.columns.tolist())

    print("\nFirst 5 training examples:")
    print(train.head())

    print("\nNumber of unique intents:")
    print(train["category"].nunique())


def main():
    print("BANKING77 Downloader")
    print("=" * 40)

    for name, url in FILES.items():
        download_file(name, url)

    verify_dataset()

    print("\nBANKING77 downloaded successfully!")


if __name__ == "__main__":
    main()