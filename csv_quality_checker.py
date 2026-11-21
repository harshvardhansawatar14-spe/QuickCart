
import pandas as pd


def check_csv_quality(file_path):
    """Check basic data quality of a CSV file."""

    try:
        df = pd.read_csv(file_path)

        print("=" * 40)
        print("QUICKCART CSV QUALITY REPORT")
        print("=" * 40)

        # Dataset information
        print(f"Total Rows      : {df.shape[0]}")
        print(f"Total Columns   : {df.shape[1]}")
        print(f"Duplicate Rows  : {df.duplicated().sum()}")

        # Missing values
        print("\nMissing Values:")
        missing_values = df.isnull().sum()

        if missing_values.sum() == 0:
            print("No missing values found.")
        else:
            print(missing_values[missing_values > 0])

        # Column data types
        print("\nColumn Data Types:")
        print(df.dtypes)

        print("\nQuality Check Completed!")

    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")

    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    print("CSV Quality Checker is ready.")
    print("Use check_csv_quality('your_file.csv') to analyze a dataset.")
