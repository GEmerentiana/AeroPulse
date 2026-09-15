import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/raw")

print("===================================")
print("AeroPulse Data Source Inspection")
print("===================================")

print("Raw data directory:")
print(DATA_PATH.resolve())

files = list(DATA_PATH.glob("*"))

print("\nFiles found:")

if not files:
    print("No data files yet.")
else:
    for file in files:
        print("-", file.name)

print("\n===================================")
print("Inspection complete.")
print("===================================")