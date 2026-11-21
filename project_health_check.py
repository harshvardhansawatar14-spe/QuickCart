
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# Important project files
required_files = [
    "main.py",
    "config.py",
    "data_generator.py",
    "data_cleaning.py",
    "data_validation.py",
    "database.py",
    "sql_analysis.py",
    "requirements.txt",
    "README.md",
]

print("=" * 45)
print("QUICKCART PROJECT HEALTH CHECK")
print("=" * 45)

missing_files = []

for file_name in required_files:
    file_path = BASE_DIR / file_name

    if file_path.exists():
        print(f"[OK] {file_name}")
    else:
        print(f"[MISSING] {file_name}")
        missing_files.append(file_name)

print("-" * 45)

if missing_files:
    print(f"Health Status: FAILED")
    print(f"Missing files: {len(missing_files)}")
else:
    print("Health Status: PASSED")
    print("All required files are available.")

print("=" * 45)
