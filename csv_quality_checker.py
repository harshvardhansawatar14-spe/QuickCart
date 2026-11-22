import pandas as pd


def check_csv_quality(file_path):
    """Generate a detailed data quality report for a CSV file."""

    try:
        df = pd.read_csv(file_path)

        total_rows, total_columns = df.shape
        duplicate_rows = int(df.duplicated().sum())
        missing_values = df.isnull().sum()
        missing_total = int(missing_values.sum())

        print("=" * 50)
        print("QUICKCART - CSV DATA QUALITY REPORT")
        print("=" * 50)

        print(f"File            : {file_path}")
        print(f"Total Rows      : {total_rows:,}")
        print(f"Total Columns   : {total_columns}")
        print(f"Duplicate Rows  : {duplicate_rows:,}")
        print(f"Missing Cells   : {missing_total:,}")

        if total_rows > 0 and total_columns > 0:
            missing_percentage = (
                missing_total / (total_rows * total_columns)
            ) * 100
        else:
            missing_percentage = 0

        print(f"Missing Rate    : {missing_percentage:.2f}%")

        print("\nCOLUMN-WISE QUALITY")
        print("-" * 50)

        report = pd.DataFrame({
            "Column": df.columns,
            "DataType": df.dtypes.astype(str).values,
            "MissingValues": missing_values.values,
            "MissingPercent": (
                missing_values.values / max(total_rows, 1) * 100
            ).round(2),
            "UniqueValues": df.nunique().values
        })

        print(report.to_string(index=False))

        empty_columns = report.loc[
            report["UniqueValues"] == 0, "Column"
        ].tolist()

        print("\nEMPTY COLUMNS")
        if empty_columns:
            for column in empty_columns:
                print(f"- {column}")
        else:
            print("No completely empty columns found.")

        print("\nQUALITY SUMMARY")
        print("-" * 50)

        print(
            "Duplicate Check:",
            "PASS" if duplicate_rows == 0 else "WARNING"
        )

        print(
            "Missing Values:",
            "PASS" if missing_total == 0 else "WARNING"
        )

        print(
            "Empty Columns:",
            "PASS" if not empty_columns else "WARNING"
        )

        print("\nReport completed successfully.")

        return report

    except FileNotFoundError:
        print(f"File not found: {file_path}")

    except pd.errors.EmptyDataError:
        print("Error: CSV file is empty.")

    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    print("QuickCart CSV Quality Checker")
    print("Usage: check_csv_quality('your_file.csv')")import pandas as pd


def check_csv_quality(file_path):
    """Generate a detailed data quality report for a CSV file."""

    try:
        df = pd.read_csv(file_path)

        total_rows, total_columns = df.shape
        duplicate_rows = int(df.duplicated().sum())
        missing_values = df.isnull().sum()
        missing_total = int(missing_values.sum())

        print("=" * 50)
        print("QUICKCART - CSV DATA QUALITY REPORT")
        print("=" * 50)

        print(f"File            : {file_path}")
        print(f"Total Rows      : {total_rows:,}")
        print(f"Total Columns   : {total_columns}")
        print(f"Duplicate Rows  : {duplicate_rows:,}")
        print(f"Missing Cells   : {missing_total:,}")

        if total_rows > 0 and total_columns > 0:
            missing_percentage = (
                missing_total / (total_rows * total_columns)
            ) * 100
        else:
            missing_percentage = 0

        print(f"Missing Rate    : {missing_percentage:.2f}%")

        print("\nCOLUMN-WISE QUALITY")
        print("-" * 50)

        report = pd.DataFrame({
            "Column": df.columns,
            "DataType": df.dtypes.astype(str).values,
            "MissingValues": missing_values.values,
            "MissingPercent": (
                missing_values.values / max(total_rows, 1) * 100
            ).round(2),
            "UniqueValues": df.nunique().values
        })

        print(report.to_string(index=False))

        empty_columns = report.loc[
            report["UniqueValues"] == 0, "Column"
        ].tolist()

        print("\nEMPTY COLUMNS")
        if empty_columns:
            for column in empty_columns:
                print(f"- {column}")
        else:
            print("No completely empty columns found.")

        print("\nQUALITY SUMMARY")
        print("-" * 50)

        print(
            "Duplicate Check:",
            "PASS" if duplicate_rows == 0 else "WARNING"
        )

        print(
            "Missing Values:",
            "PASS" if missing_total == 0 else "WARNING"
        )

        print(
            "Empty Columns:",
            "PASS" if not empty_columns else "WARNING"
        )

        print("\nReport completed successfully.")

        return report

    except FileNotFoundError:
        print(f"File not found: {file_path}")

    except pd.errors.EmptyDataError:
        print("Error: CSV file is empty.")

    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    print("QuickCart CSV Quality Checker")
    print("Usage: check_csv_quality('your_file.csv')")import pandas as pd


def check_csv_quality(file_path):
    """Generate a detailed data quality report for a CSV file."""

    try:
        df = pd.read_csv(file_path)

        total_rows, total_columns = df.shape
        duplicate_rows = int(df.duplicated().sum())
        missing_values = df.isnull().sum()
        missing_total = int(missing_values.sum())

        print("=" * 50)
        print("QUICKCART - CSV DATA QUALITY REPORT")
        print("=" * 50)

        print(f"File            : {file_path}")
        print(f"Total Rows      : {total_rows:,}")
        print(f"Total Columns   : {total_columns}")
        print(f"Duplicate Rows  : {duplicate_rows:,}")
        print(f"Missing Cells   : {missing_total:,}")

        if total_rows > 0 and total_columns > 0:
            missing_percentage = (
                missing_total / (total_rows * total_columns)
            ) * 100
        else:
            missing_percentage = 0

        print(f"Missing Rate    : {missing_percentage:.2f}%")

        print("\nCOLUMN-WISE QUALITY")
        print("-" * 50)

        report = pd.DataFrame({
            "Column": df.columns,
            "DataType": df.dtypes.astype(str).values,
            "MissingValues": missing_values.values,
            "MissingPercent": (
                missing_values.values / max(total_rows, 1) * 100
            ).round(2),
            "UniqueValues": df.nunique().values
        })

        print(report.to_string(index=False))

        empty_columns = report.loc[
            report["UniqueValues"] == 0, "Column"
        ].tolist()

        print("\nEMPTY COLUMNS")
        if empty_columns:
            for column in empty_columns:
                print(f"- {column}")
        else:
            print("No completely empty columns found.")

        print("\nQUALITY SUMMARY")
        print("-" * 50)

        print(
            "Duplicate Check:",
            "PASS" if duplicate_rows == 0 else "WARNING"
        )

        print(
            "Missing Values:",
            "PASS" if missing_total == 0 else "WARNING"
        )

        print(
            "Empty Columns:",
            "PASS" if not empty_columns else "WARNING"
        )

        print("\nReport completed successfully.")

        return report

    except FileNotFoundError:
        print(f"File not found: {file_path}")

    except pd.errors.EmptyDataError:
        print("Error: CSV file is empty.")

    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    print("QuickCart CSV Quality Checker")
    print("Usage: check_csv_quality('your_file.csv')")
