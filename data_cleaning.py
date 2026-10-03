"""
QUICKCART - Data Cleaning Module

Cleans and standardizes raw QuickCart datasets.

Input:
    data/raw/*.csv

Output:
    data/processed/*.csv

The module performs:
- Missing-value handling
- Duplicate removal
- Data type correction
- ID validation
- Numeric validation
- Date validation
- Referential integrity cleaning
- Business-rule validation
- Standardized column ordering
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

import config


# ============================================================
# LOGGING
# ============================================================

LOGGER = logging.getLogger("QuickCart.DataCleaning")

if not LOGGER.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


# ============================================================
# PATHS
# ============================================================

RAW_DIR = Path(config.RAW_DATA_DIR)
PROCESSED_DIR = Path(config.PROCESSED_DATA_DIR)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)
# ============================================================
# GENERAL HELPERS
# ============================================================

def load_csv(filename: str) -> pd.DataFrame:
    """Load a raw CSV file."""

    path = RAW_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Required raw file not found: {path}"
        )

    LOGGER.info(
        "Loading %s",
        path,
    )

    return pd.read_csv(
        path,
        low_memory=False,
    )

def save_cleaned(
    dataframe: pd.DataFrame,
    filename: str,
) -> None:
    """Save cleaned dataframe to processed directory."""

    path = PROCESSED_DIR / filename

    dataframe.to_csv(
        path,
        index=False,
        encoding="utf-8-sig",
    )

    LOGGER.info(
        "Saved cleaned dataset: %s rows -> %s",
        len(dataframe),
        path,
    )


def remove_duplicates(
    dataframe: pd.DataFrame,
    subset: list[str] | None = None,
) -> pd.DataFrame:
    """Remove duplicate rows."""

    before = len(dataframe)

    if subset:
        dataframe = dataframe.drop_duplicates(
            subset=subset,
            keep="first",
        )
    else:
        dataframe = dataframe.drop_duplicates(
            keep="first",
        )

    removed = before - len(dataframe)

    if removed:
        LOGGER.info(
            "Removed %s duplicate rows",
            removed,
        )

    return dataframe


def strip_string_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Remove unnecessary whitespace from text columns."""

    for column in dataframe.columns:

        if dataframe[column].dtype == "object":

            dataframe[column] = (
                dataframe[column]
                .astype("string")
                .str.strip()
            )

    return dataframe


def replace_empty_strings(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Convert empty strings to missing values."""

    dataframe = dataframe.replace(
        {
            "": np.nan,
            " ": np.nan,
            "NA": np.nan,
            "N/A": np.nan,
            "null": np.nan,
            "None": np.nan,
        }
    )

    return dataframe


# ============================================================
# LOCATIONS
# ============================================================

def clean_locations() -> pd.DataFrame:
    """Clean location dimension."""

    df = load_csv("locations.csv")

    df = strip_string_columns(df)
    df = replace_empty_strings(df)

    df = remove_duplicates(
        df,
        subset=["LocationID"],
    )

    required_columns = [
        "LocationID",
        "City",
        "State",
        "Region",
        "Tier",
    ]

    for column in required_columns:

        if column not in df.columns:
            raise ValueError(
                f"Missing Locations column: {column}"
            )

    df["LocationID"] = (
        df["LocationID"]
        .astype("string")
    )

    df["City"] = (
        df["City"]
        .fillna("Unknown")
        .astype("string")
    )

    df["State"] = (
        df["State"]
        .fillna("Unknown")
        .astype("string")
    )

    df["Region"] = (
        df["Region"]
        .fillna("Unknown")
        .astype("string")
    )

    df["Tier"] = (
        df["Tier"]
        .fillna("Tier 2")
        .astype("string")
    )

    return df


# ============================================================
# CUSTOMERS
# ============================================================

def clean_customers(
    locations: pd.DataFrame,
) -> pd.DataFrame:
    """Clean customer master data."""

    df = load_csv("customers.csv")

    df = strip_string_columns(df)
    df = replace_empty_strings(df)

    df = remove_duplicates(
        df,
        subset=["CustomerID"],
    )

    required_columns = [
        "CustomerID",
        "Name",
        "Gender",
        "Age",
        "City",
        "State",
        "SignupDate",
        "CustomerSegment",
    ]

    for column in required_columns:

        if column not in df.columns:
            raise ValueError(
                f"Missing Customers column: {column}"
            )

    # IDs
    df["CustomerID"] = (
        df["CustomerID"]
        .astype("string")
    )

    # Names
    df["Name"] = (
        df["Name"]
        .fillna("Unknown Customer")
        .astype("string")
    )

    # Gender
    valid_genders = [
        "Male",
        "Female",
        "Other",
    ]

    df.loc[
        ~df["Gender"].isin(valid_genders),
        "Gender",
    ] = "Other"

    df["Gender"] = (
        df["Gender"]
        .fillna("Other")
        .astype("string")
    )

    # Age
    df["Age"] = pd.to_numeric(
        df["Age"],
        errors="coerce",
    )

    df["Age"] = (
        df["Age"]
        .fillna(30)
        .clip(
            lower=18,
            upper=80,
        )
        .astype(int)
    )

    # Dates
    df["SignupDate"] = pd.to_datetime(
        df["SignupDate"],
        errors="coerce",
    )

    fallback_signup = pd.Timestamp(
        config.DATA_START_DATE
    )

    df["SignupDate"] = (
        df["SignupDate"]
        .fillna(fallback_signup)
    )

    # City / State
    df["City"] = (
        df["City"]
        .fillna("Unknown")
        .astype("string")
    )

    df["State"] = (
        df["State"]
        .fillna("Unknown")
        .astype("string")
    )

    # Customer segment is intentionally retained
    # as Pending RFM until rfm_segmentation.py.
    df["CustomerSegment"] = (
        df["CustomerSegment"]
        .fillna("Pending RFM")
        .astype("string")
    )

    # Keep only cities available in location dimension.
    valid_cities = set(
        locations["City"].astype(str)
    )

    unknown_city_mask = (
        ~df["City"].astype(str).isin(
            valid_cities
        )
    )

    if unknown_city_mask.any():

        LOGGER.warning(
            "%s customers contain unknown cities.",
            int(unknown_city_mask.sum()),
        )

    return df


# ============================================================
# PRODUCTS
# ============================================================

def clean_products() -> pd.DataFrame:
    """Clean product master data."""

    df = load_csv("products.csv")

    df = strip_string_columns(df)
    df = replace_empty_strings(df)

    df = remove_duplicates(
        df,
        subset=["ProductID"],
    )

    required_columns = [
        "ProductID",
        "ProductName",
        "Category",
        "SubCategory",
        "Brand",
        "UnitPrice",
        "CostPrice",
        "Margin",
        "StockQuantity",
        "Supplier",
    ]

    for column in required_columns:

        if column not in df.columns:
            raise ValueError(
                f"Missing Products column: {column}"
            )

    df["ProductID"] = (
        df["ProductID"]
        .astype("string")
    )

    text_columns = [
        "ProductName",
        "Category",
        "SubCategory",
        "Brand",
        "Supplier",
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .fillna("Unknown")
            .astype("string")
        )

    numeric_columns = [
        "UnitPrice",
        "CostPrice",
        "Margin",
        "StockQuantity",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        df[column] = (
            df[column]
            .fillna(0)
        )

    # Business validation
    df["UnitPrice"] = (
        df["UnitPrice"]
        .clip(lower=0.01)
    )

    df["CostPrice"] = (
        df["CostPrice"]
        .clip(lower=0)
    )

    df["CostPrice"] = np.minimum(
        df["CostPrice"],
        df["UnitPrice"],
    )

    df["Margin"] = (
        df["UnitPrice"]
        - df["CostPrice"]
    )

    df["StockQuantity"] = (
        df["StockQuantity"]
        .clip(lower=0)
        .round()
        .astype(int)
    )

    return df


# ============================================================
# ORDERS
# ============================================================

def clean_orders(
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Clean order-level transaction data."""

    df = load_csv("orders.csv")

    df = strip_string_columns(df)
    df = replace_empty_strings(df)

    df = remove_duplicates(
        df,
        subset=["OrderID"],
    )

    required_columns = [
        "OrderID",
        "CustomerID",
        "OrderDate",
        "City",
        "State",
        "PaymentMethod",
        "OrderStatus",
        "DeliveryTime",
        "ReturnStatus",
        "CancellationStatus",
    ]

    for column in required_columns:

        if column not in df.columns:
            raise ValueError(
                f"Missing Orders column: {column}"
            )

    df["OrderID"] = (
        df["OrderID"]
        .astype("string")
    )

    df["CustomerID"] = (
        df["CustomerID"]
        .astype("string")
    )

    df["OrderDate"] = pd.to_datetime(
        df["OrderDate"],
        errors="coerce",
    )

    df["OrderDate"] = (
        df["OrderDate"]
        .fillna(
            pd.Timestamp(
                config.DATA_START_DATE
            )
        )
    )

    # Valid customers only.
    valid_customer_ids = set(
        customers["CustomerID"]
    )

    before = len(df)

    df = df[
        df["CustomerID"].isin(
            valid_customer_ids
        )
    ].copy()

    removed = before - len(df)

    if removed:
        LOGGER.warning(
            "Removed %s orders with invalid CustomerID.",
            removed,
        )

    # Text columns.
    for column in [
        "City",
        "State",
        "PaymentMethod",
        "OrderStatus",
        "ReturnStatus",
        "CancellationStatus",
    ]:

        df[column] = (
            df[column]
            .fillna("Unknown")
            .astype("string")
        )

    # DeliveryTime can be null for cancelled orders.
    df["DeliveryTime"] = pd.to_numeric(
        df["DeliveryTime"],
        errors="coerce",
    )

    df.loc[
        df["DeliveryTime"] < 0,
        "DeliveryTime",
    ] = np.nan

    return df


# ============================================================
# ORDER ITEMS
# ============================================================

def clean_order_items(
    orders: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Clean order item transactions."""

    df = load_csv("order_items.csv")

    df = strip_string_columns(df)
    df = replace_empty_strings(df)

    df = remove_duplicates(
        df,
        subset=["OrderItemID"],
    )

    required_columns = [
        "OrderItemID",
        "OrderID",
        "ProductID",
        "Quantity",
        "UnitPrice",
        "Discount",
        "DiscountPercent",
        "Tax",
        "TaxRate",
        "Revenue",
        "NetRevenue",
        "CostAmount",
    ]

    for column in required_columns:

        if column not in df.columns:
            raise ValueError(
                f"Missing Order Items column: {column}"
            )

    df["OrderItemID"] = (
        df["OrderItemID"]
        .astype("string")
    )

    df["OrderID"] = (
        df["OrderID"]
        .astype("string")
    )

    df["ProductID"] = (
        df["ProductID"]
        .astype("string")
    )

    valid_order_ids = set(
        orders["OrderID"]
    )

    valid_product_ids = set(
        products["ProductID"]
    )

    before = len(df)

    df = df[
        df["OrderID"].isin(valid_order_ids)
        & df["ProductID"].isin(valid_product_ids)
    ].copy()

    removed = before - len(df)

    if removed:
        LOGGER.warning(
            "Removed %s invalid order-item rows.",
            removed,
        )

    numeric_columns = [
        "Quantity",
        "UnitPrice",
        "Discount",
        "DiscountPercent",
        "Tax",
        "TaxRate",
        "Revenue",
        "NetRevenue",
        "CostAmount",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        df[column] = (
            df[column]
            .fillna(0)
        )

    # Quantity must be positive.
    df["Quantity"] = (
        df["Quantity"]
        .clip(lower=1)
        .round()
        .astype(int)
    )

    df["UnitPrice"] = (
        df["UnitPrice"]
        .clip(lower=0)
    )

    df["Discount"] = (
        df["Discount"]
        .clip(lower=0)
    )

    df["DiscountPercent"] = (
        df["DiscountPercent"]
        .clip(
            lower=0,
            upper=1,
        )
    )

    df["Tax"] = (
        df["Tax"]
        .clip(lower=0)
    )

    df["TaxRate"] = (
        df["TaxRate"]
        .clip(
            lower=0,
            upper=1,
        )
    )

    df["Revenue"] = (
        df["Revenue"]
        .clip(lower=0)
    )

    df["CostAmount"] = (
        df["CostAmount"]
        .clip(lower=0)
    )

    # Recalculate business values from trusted
    # quantity and unit price.
    df["Revenue"] = (
        df["Quantity"]
        * df["UnitPrice"]
    ).round(2)

    df["Discount"] = np.minimum(
        df["Discount"],
        df["Revenue"],
    )

    taxable_amount = (
        df["Revenue"]
        - df["Discount"]
    )

    df["Tax"] = (
        taxable_amount
        * df["TaxRate"]
    ).round(2)

    df["NetRevenue"] = (
        taxable_amount
        + df["Tax"]
    ).round(2)

    return df


# ============================================================
# PAYMENTS
# ============================================================

def clean_payments(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Clean payment transactions."""

    df = load_csv("payments.csv")

    df = strip_string_columns(df)
    df = replace_empty_strings(df)

    df = remove_duplicates(
        df,
        subset=["PaymentID"],
    )

    required_columns = [
        "PaymentID",
        "OrderID",
        "PaymentDate",
        "PaymentMethod",
        "Amount",
        "PaymentStatus",
        "TransactionID",
    ]

    for column in required_columns:

        if column not in df.columns:
            raise ValueError(
                f"Missing Payments column: {column}"
            )

    df["PaymentID"] = (
        df["PaymentID"]
        .astype("string")
    )

    df["OrderID"] = (
        df["OrderID"]
        .astype("string")
    )

    df["TransactionID"] = (
        df["TransactionID"]
        .astype("string")
    )

    valid_orders = set(
        orders["OrderID"]
    )

    before = len(df)

    df = df[
        df["OrderID"].isin(valid_orders)
    ].copy()

    removed = before - len(df)

    if removed:
        LOGGER.warning(
            "Removed %s payments with invalid OrderID.",
            removed,
        )

    df["PaymentDate"] = pd.to_datetime(
        df["PaymentDate"],
        errors="coerce",
    )

    df["PaymentDate"] = (
        df["PaymentDate"]
        .fillna(
            pd.Timestamp(
                config.DATA_START_DATE
            )
        )
    )

    df["PaymentMethod"] = (
        df["PaymentMethod"]
        .fillna("Unknown")
        .astype("string")
    )

    df["PaymentStatus"] = (
        df["PaymentStatus"]
        .fillna("Completed")
        .astype("string")
    )

    df["Amount"] = pd.to_numeric(
        df["Amount"],
        errors="coerce",
    )

    df["Amount"] = (
        df["Amount"]
        .fillna(0)
        .clip(lower=0)
        .round(2)
    )

    return df


# ============================================================
# RETURNS
# ============================================================

def clean_returns(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Clean return transactions."""

    df = load_csv("returns.csv")

    df = strip_string_columns(df)
    df = replace_empty_strings(df)

    if df.empty:

        LOGGER.info(
            "Returns dataset is empty."
        )

        return df

    df = remove_duplicates(
        df,
        subset=["ReturnID"],
    )

    required_columns = [
        "ReturnID",
        "OrderID",
        "ReturnDate",
        "ReturnReason",
        "RefundAmount",
        "ReturnStatus",
    ]

    for column in required_columns:

        if column not in df.columns:
            raise ValueError(
                f"Missing Returns column: {column}"
            )

    df["ReturnID"] = (
        df["ReturnID"]
        .astype("string")
    )

    df["OrderID"] = (
        df["OrderID"]
        .astype("string")
    )

    valid_orders = set(
        orders["OrderID"]
    )

    df = df[
        df["OrderID"].isin(valid_orders)
    ].copy()

    df["ReturnDate"] = pd.to_datetime(
        df["ReturnDate"],
        errors="coerce",
    )

    df["ReturnReason"] = (
        df["ReturnReason"]
        .fillna("Other")
        .astype("string")
    )

    df["RefundAmount"] = pd.to_numeric(
        df["RefundAmount"],
        errors="coerce",
    )

    df["RefundAmount"] = (
        df["RefundAmount"]
        .fillna(0)
        .clip(lower=0)
        .round(2)
    )

    df["ReturnStatus"] = (
        df["ReturnStatus"]
        .fillna("Approved")
        .astype("string")
    )

    return df


# ============================================================
# DELIVERIES
# ============================================================

def clean_deliveries(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Clean delivery transactions."""

    df = load_csv("deliveries.csv")

    df = strip_string_columns(df)
    df = replace_empty_strings(df)

    df = remove_duplicates(
        df,
        subset=["DeliveryID"],
    )

    required_columns = [
        "DeliveryID",
        "OrderID",
        "DeliveryPartner",
        "DeliveryStatus",
        "DeliveryTimeMinutes",
        "TargetDeliveryMinutes",
        "DeliveredAt",
    ]

    for column in required_columns:

        if column not in df.columns:
            raise ValueError(
                f"Missing Deliveries column: {column}"
            )

    df["DeliveryID"] = (
        df["DeliveryID"]
        .astype("string")
    )

    df["OrderID"] = (
        df["OrderID"]
        .astype("string")
    )

    valid_orders = set(
        orders["OrderID"]
    )

    df = df[
        df["OrderID"].isin(valid_orders)
    ].copy()

    df["DeliveryPartner"] = (
        df["DeliveryPartner"]
        .fillna("Unknown")
        .astype("string")
    )

    df["DeliveryStatus"] = (
        df["DeliveryStatus"]
        .fillna("Unknown")
        .astype("string")
    )

    df["DeliveryTimeMinutes"] = pd.to_numeric(
        df["DeliveryTimeMinutes"],
        errors="coerce",
    )

    df["TargetDeliveryMinutes"] = pd.to_numeric(
        df["TargetDeliveryMinutes"],
        errors="coerce",
    )

    df["DeliveryTimeMinutes"] = (
        df["DeliveryTimeMinutes"]
        .clip(lower=0)
    )

    df["TargetDeliveryMinutes"] = (
        df["TargetDeliveryMinutes"]
        .clip(lower=0)
    )

    df["DeliveredAt"] = pd.to_datetime(
        df["DeliveredAt"],
        errors="coerce",
    )

    return df


# ============================================================
# INVENTORY
# ============================================================

def clean_inventory(
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Clean inventory snapshots."""

    df = load_csv("inventory.csv")

    df = strip_string_columns(df)
    df = replace_empty_strings(df)

    df = remove_duplicates(
        df,
        subset=["InventoryID"],
    )

    required_columns = [
        "InventoryID",
        "SnapshotDate",
        "ProductID",
        "OpeningStock",
        "ReceivedQuantity",
        "SoldQuantity",
        "ClosingStock",
        "UnitCost",
        "InventoryValue",
        "InventoryStatus",
    ]

    for column in required_columns:

        if column not in df.columns:
            raise ValueError(
                f"Missing Inventory column: {column}"
            )

    df["InventoryID"] = (
        df["InventoryID"]
        .astype("string")
    )

    df["ProductID"] = (
        df["ProductID"]
        .astype("string")
    )

    valid_products = set(
        products["ProductID"]
    )

    df = df[
        df["ProductID"].isin(
            valid_products
        )
    ].copy()

    df["SnapshotDate"] = pd.to_datetime(
        df["SnapshotDate"],
        errors="coerce",
    )

    numeric_columns = [
        "OpeningStock",
        "ReceivedQuantity",
        "SoldQuantity",
        "ClosingStock",
        "UnitCost",
        "InventoryValue",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        df[column] = (
            df[column]
            .fillna(0)
            .clip(lower=0)
        )

    integer_columns = [
        "OpeningStock",
        "ReceivedQuantity",
        "SoldQuantity",
        "ClosingStock",
    ]

    for column in integer_columns:

        df[column] = (
            df[column]
            .round()
            .astype(int)
        )

    # Recalculate inventory value.
    df["InventoryValue"] = (
        df["ClosingStock"]
        * df["UnitCost"]
    ).round(2)

    # Recalculate inventory status.
    df["InventoryStatus"] = np.select(
        [
            df["ClosingStock"] <= 0,
            df["ClosingStock"]
            <= config.LOW_STOCK_THRESHOLD,
        ],
        [
            "Out of Stock",
            "Low Stock",
        ],
        default="Healthy Stock",
    )

    return df


# ============================================================
# DATE DIMENSION
# ============================================================

def clean_date_dimension() -> pd.DataFrame:
    """Clean the generated date dimension."""

    path = PROCESSED_DIR / "dim_date.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Date dimension not found: {path}"
        )

    df = pd.read_csv(
        path,
        low_memory=False,
    )

    df = strip_string_columns(df)

    df = remove_duplicates(
        df,
        subset=["DateKey"],
    )

    df["DateKey"] = pd.to_numeric(
        df["DateKey"],
        errors="coerce",
    ).astype("Int64")

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
    )

    numeric_columns = [
        "Year",
        "MonthNumber",
        "WeekNumber",
        "DayOfMonth",
        "DayOfWeek",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    return df


# ============================================================
# DATA QUALITY SUMMARY
# ============================================================

def create_cleaning_summary(
    datasets: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Create a summary of cleaned datasets."""

    rows = []

    for name, dataframe in datasets.items():

        missing_values = int(
            dataframe.isna()
            .sum()
            .sum()
        )

        duplicate_rows = int(
            dataframe.duplicated()
            .sum()
        )

        rows.append(
            {
                "Dataset": name,
                "Rows": len(dataframe),
                "Columns": len(dataframe.columns),
                "MissingValues": missing_values,
                "DuplicateRows": duplicate_rows,
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# MAIN CLEANING PIPELINE
# ============================================================

def clean_all_data() -> Dict[str, pd.DataFrame]:
    """
    Execute complete QuickCart data-cleaning pipeline.
    """

    print()
    print("=" * 90)
    print(" QUICKCART DATA CLEANING PIPELINE")
    print("=" * 90)

    LOGGER.info(
        "Starting QuickCart data cleaning."
    )

    # --------------------------------------------------------
    # 1. Locations
    # --------------------------------------------------------

    print("\n[1/10] Cleaning locations...")

    locations = clean_locations()

    save_cleaned(
        locations,
        "dim_location.csv",
    )

    print(
        f"  Clean locations: {len(locations):,}"
    )

    # --------------------------------------------------------
    # 2. Customers
    # --------------------------------------------------------

    print("\n[2/10] Cleaning customers...")

    customers = clean_customers(
        locations
    )

    save_cleaned(
        customers,
        "dim_customers.csv",
    )

    print(
        f"  Clean customers: {len(customers):,}"
    )

    # --------------------------------------------------------
    # 3. Products
    # --------------------------------------------------------

    print("\n[3/10] Cleaning products...")

    products = clean_products()

    save_cleaned(
        products,
        "dim_products.csv",
    )

    print(
        f"  Clean products: {len(products):,}"
    )

    # --------------------------------------------------------
    # 4. Orders
    # --------------------------------------------------------

    print("\n[4/10] Cleaning orders...")

    orders = clean_orders(
        customers
    )

    save_cleaned(
        orders,
        "fact_orders.csv",
    )

    print(
        f"  Clean orders: {len(orders):,}"
    )

    # --------------------------------------------------------
    # 5. Order Items
    # --------------------------------------------------------

    print("\n[5/10] Cleaning order items...")

    order_items = clean_order_items(
        orders,
        products,
    )

    save_cleaned(
        order_items,
        "fact_order_items.csv",
    )

    print(
        f"  Clean order items: "
        f"{len(order_items):,}"
    )

    # --------------------------------------------------------
    # 6. Payments
    # --------------------------------------------------------

    print("\n[6/10] Cleaning payments...")

    payments = clean_payments(
        orders
    )

    save_cleaned(
        payments,
        "fact_payments.csv",
    )

    print(
        f"  Clean payments: {len(payments):,}"
    )

    # --------------------------------------------------------
    # 7. Returns
    # --------------------------------------------------------

    print("\n[7/10] Cleaning returns...")

    returns = clean_returns(
        orders
    )

    save_cleaned(
        returns,
        "fact_returns.csv",
    )

    print(
        f"  Clean returns: {len(returns):,}"
    )

    # --------------------------------------------------------
    # 8. Deliveries
    # --------------------------------------------------------

    print("\n[8/10] Cleaning deliveries...")

    deliveries = clean_deliveries(
        orders
    )

    save_cleaned(
        deliveries,
        "fact_deliveries.csv",
    )

    print(
        f"  Clean deliveries: "
        f"{len(deliveries):,}"
    )

    # --------------------------------------------------------
    # 9. Inventory
    # --------------------------------------------------------

    print("\n[9/10] Cleaning inventory...")

    inventory = clean_inventory(
        products
    )

    save_cleaned(
        inventory,
        "fact_inventory.csv",
    )

    print(
        f"  Clean inventory: "
        f"{len(inventory):,}"
    )

    # --------------------------------------------------------
    # 10. Date
    # --------------------------------------------------------

    print("\n[10/10] Cleaning date dimension...")

    date_dimension = clean_date_dimension()

    save_cleaned(
        date_dimension,
        "dim_date.csv",
    )

    print(
        f"  Clean date records: "
        f"{len(date_dimension):,}"
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    datasets = {
        "dim_location": locations,
        "dim_customers": customers,
        "dim_products": products,
        "fact_orders": orders,
        "fact_order_items": order_items,
        "fact_payments": payments,
        "fact_returns": returns,
        "fact_deliveries": deliveries,
        "fact_inventory": inventory,
        "dim_date": date_dimension,
    }

    summary = create_cleaning_summary(
        datasets
    )

    save_cleaned(
        summary,
        "data_cleaning_summary.csv",
    )

    print()
    print("=" * 90)
    print(" DATA CLEANING COMPLETED")
    print("=" * 90)

    print(
        summary.to_string(
            index=False
        )
    )

    print("=" * 90)

    LOGGER.info(
        "QuickCart data cleaning completed successfully."
    )

    return datasets


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

clean_data = clean_all_data
run = clean_all_data


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    try:
        clean_all_data()

    except Exception as exc:

        LOGGER.exception(
            "Data cleaning failed: %s",
            exc,
        )

        print()
        print("=" * 90)
        print(" DATA CLEANING FAILED")
        print("=" * 90)
        print(
            f"Error: {exc}"
        )
        print("=" * 90)

        raise
