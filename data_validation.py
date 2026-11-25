"""
QUICKCART - Data Validation Module

Validates the processed QuickCart datasets and creates:
    data/processed/validation_report.csv
    data/processed/validation_summary.csv

Run:
    python data_validation.py
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

import config


# ============================================================
# LOGGING AND PATHS
# ============================================================

LOGGER = logging.getLogger("QuickCart.DataValidation")

if not LOGGER.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

PROCESSED_DIR = Path(config.PROCESSED_DATA_DIR)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

VALIDATION_RESULTS: List[dict] = []


def add_result(
    check_name: str,
    dataset: str,
    status: str,
    message: str,
    affected_rows: int = 0,
) -> None:
    """Add one validation result."""
    VALIDATION_RESULTS.append(
        {
            "CheckName": check_name,
            "Dataset": dataset,
            "Status": status,
            "AffectedRows": int(affected_rows),
            "Message": str(message),
        }
    )


def record_count(
    check_name: str,
    dataset: str,
    invalid_count: int,
    message: str,
    failure_status: str = "FAIL",
) -> None:
    """Record a PASS when invalid_count is zero; otherwise record an issue."""
    status = "PASS" if invalid_count == 0 else failure_status
    add_result(
        check_name,
        dataset,
        status,
        message,
        invalid_count,
    )


# ============================================================
# DATASET DEFINITIONS
# ============================================================

REQUIRED_COLUMNS = {
    "dim_location": [
        "LocationID", "City", "State", "Region", "Tier",
    ],
    "dim_customers": [
        "CustomerID", "Name", "Gender", "Age", "City", "State",
        "SignupDate", "CustomerSegment",
    ],
    "dim_products": [
        "ProductID", "ProductName", "Category", "SubCategory",
        "Brand", "UnitPrice", "CostPrice", "Margin",
        "StockQuantity", "Supplier",
    ],
    "dim_date": [
        "DateKey", "Date", "Year", "Quarter", "MonthNumber",
        "MonthName", "MonthShort", "WeekNumber", "DayOfMonth",
        "DayName", "DayOfWeek", "IsWeekend",
    ],
    "fact_orders": [
        "OrderID", "CustomerID", "OrderDate", "City", "State",
        "PaymentMethod", "OrderStatus", "DeliveryTime",
        "ReturnStatus", "CancellationStatus",
    ],
    "fact_order_items": [
        "OrderItemID", "OrderID", "ProductID", "Quantity",
        "UnitPrice", "Discount", "DiscountPercent", "Tax",
        "TaxRate", "Revenue", "NetRevenue", "CostAmount",
    ],
    "fact_payments": [
        "PaymentID", "OrderID", "PaymentDate", "PaymentMethod",
        "Amount", "PaymentStatus", "TransactionID",
    ],
    "fact_returns": [
        "ReturnID", "OrderID", "ReturnDate", "ReturnReason",
        "RefundAmount", "ReturnStatus",
    ],
    "fact_deliveries": [
        "DeliveryID", "OrderID", "DeliveryPartner",
        "DeliveryStatus", "DeliveryTimeMinutes",
        "TargetDeliveryMinutes", "DeliveredAt",
    ],
    "fact_inventory": [
        "InventoryID", "SnapshotDate", "ProductID",
        "OpeningStock", "ReceivedQuantity", "SoldQuantity",
        "ClosingStock", "UnitCost", "InventoryValue",
        "InventoryStatus",
    ],
}

PRIMARY_KEYS = {
    "dim_location": "LocationID",
    "dim_customers": "CustomerID",
    "dim_products": "ProductID",
    "dim_date": "DateKey",
    "fact_orders": "OrderID",
    "fact_order_items": "OrderItemID",
    "fact_payments": "PaymentID",
    "fact_returns": "ReturnID",
    "fact_deliveries": "DeliveryID",
    "fact_inventory": "InventoryID",
}


# ============================================================
# LOAD DATA
# ============================================================

def load_processed(filename: str) -> pd.DataFrame:
    """Load one processed CSV file."""
    path = PROCESSED_DIR / filename

    if not path.is_file():
        raise FileNotFoundError(f"Processed file not found: {path}")

    return pd.read_csv(path, low_memory=False)


def load_all_datasets() -> Dict[str, pd.DataFrame]:
    """Load all ten processed QuickCart datasets."""
    return {
        name: load_processed(f"{name}.csv")
        for name in REQUIRED_COLUMNS
    }


# ============================================================
# REQUIRED COLUMNS AND PRIMARY KEYS
# ============================================================

def validate_required_columns(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    for dataset_name, required_columns in REQUIRED_COLUMNS.items():
        dataframe = datasets[dataset_name]
        missing = [
            column for column in required_columns
            if column not in dataframe.columns
        ]

        record_count(
            "Required Columns",
            dataset_name,
            len(missing),
            (
                "All required columns are present."
                if not missing
                else "Missing columns: " + ", ".join(missing)
            ),
        )


def validate_primary_keys(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    for dataset_name, primary_key in PRIMARY_KEYS.items():
        dataframe = datasets[dataset_name]

        if primary_key not in dataframe.columns:
            add_result(
                "Primary Key",
                dataset_name,
                "WARNING",
                f"Cannot validate missing column: {primary_key}.",
                0,
            )
            continue

        missing_count = int(dataframe[primary_key].isna().sum())
        duplicate_count = int(
            dataframe[primary_key].dropna().duplicated().sum()
        )

        record_count(
            "Primary Key Missing",
            dataset_name,
            missing_count,
            (
                f"No missing {primary_key} values."
                if missing_count == 0
                else f"{missing_count} missing {primary_key} values."
            ),
        )
        record_count(
            "Primary Key Duplicate",
            dataset_name,
            duplicate_count,
            (
                f"{primary_key} values are unique."
                if duplicate_count == 0
                else f"{duplicate_count} duplicate {primary_key} values."
            ),
        )


# ============================================================
# MISSING VALUES
# ============================================================

def validate_missing_values(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    """
    Count missing cells. DeliveryTime on cancelled orders and
    missing delivery attributes on cancelled deliveries are allowed.
    """
    for dataset_name, dataframe in datasets.items():
        total_missing = int(dataframe.isna().sum().sum())
        allowed_missing = 0

        if (
            dataset_name == "fact_orders"
            and {"OrderStatus", "DeliveryTime"}.issubset(dataframe.columns)
        ):
            cancelled = dataframe["OrderStatus"].eq("Cancelled")
            allowed_missing = int(
                dataframe.loc[cancelled, "DeliveryTime"].isna().sum()
            )

        elif (
            dataset_name == "fact_deliveries"
            and "DeliveryStatus" in dataframe.columns
        ):
            cancelled = dataframe["DeliveryStatus"].eq("Cancelled")
            allowed_missing = int(
                dataframe.loc[cancelled].isna().sum().sum()
            )

        unexpected_missing = max(0, total_missing - allowed_missing)

        add_result(
            "Missing Values",
            dataset_name,
            "PASS" if unexpected_missing == 0 else "WARNING",
            (
                f"Total missing cells: {total_missing}; "
                f"allowed missing cells: {allowed_missing}; "
                f"unexpected missing cells: {unexpected_missing}."
            ),
            unexpected_missing,
        )


# ============================================================
# FOREIGN KEYS
# ============================================================

def validate_foreign_key(
    child_df: pd.DataFrame,
    parent_df: pd.DataFrame,
    child_column: str,
    parent_column: str,
    relationship_name: str,
) -> None:
    """Check non-null child keys against non-null parent keys."""
    if child_column not in child_df.columns:
        add_result(
            "Foreign Key", relationship_name, "WARNING",
            f"Child column {child_column} is missing.", 0,
        )
        return

    if parent_column not in parent_df.columns:
        add_result(
            "Foreign Key", relationship_name, "WARNING",
            f"Parent column {parent_column} is missing.", 0,
        )
        return

    child_values = child_df[child_column]
    parent_values = set(parent_df[parent_column].dropna())

    non_null_child = child_values.notna()
    invalid_mask = (
        non_null_child
        & ~child_values.isin(parent_values)
    )
    invalid_count = int(invalid_mask.sum())

    record_count(
        "Foreign Key",
        relationship_name,
        invalid_count,
        (
            f"{child_column} references valid {parent_column} values."
            if invalid_count == 0
            else f"{invalid_count} non-null child keys have no parent match."
        ),
    )


def validate_all_foreign_keys(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    relationships = [
        ("fact_orders", "dim_customers", "CustomerID", "CustomerID",
         "Orders -> Customers"),
        ("fact_order_items", "fact_orders", "OrderID", "OrderID",
         "Order Items -> Orders"),
        ("fact_order_items", "dim_products", "ProductID", "ProductID",
         "Order Items -> Products"),
        ("fact_payments", "fact_orders", "OrderID", "OrderID",
         "Payments -> Orders"),
        ("fact_returns", "fact_orders", "OrderID", "OrderID",
         "Returns -> Orders"),
        ("fact_deliveries", "fact_orders", "OrderID", "OrderID",
         "Deliveries -> Orders"),
        ("fact_inventory", "dim_products", "ProductID", "ProductID",
         "Inventory -> Products"),
    ]

    for child, parent, child_col, parent_col, label in relationships:
        validate_foreign_key(
            datasets[child],
            datasets[parent],
            child_col,
            parent_col,
            label,
        )


# ============================================================
# NUMERIC RULES
# ============================================================

def validate_non_negative(
    dataframe: pd.DataFrame,
    dataset_name: str,
    column: str,
) -> None:
    if column not in dataframe.columns:
        add_result(
            "Non-Negative Values", dataset_name, "WARNING",
            f"Cannot validate missing column {column}.", 0,
        )
        return

    values = pd.to_numeric(dataframe[column], errors="coerce")
    invalid_count = int((values < 0).sum())

    record_count(
        "Non-Negative Values",
        dataset_name,
        invalid_count,
        (
            f"{column} contains no negative values."
            if invalid_count == 0
            else f"{invalid_count} negative values found in {column}."
        ),
    )


def validate_numeric_fields(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    numeric_rules = {
        "dim_products": [
            "UnitPrice", "CostPrice", "Margin", "StockQuantity",
        ],
        "fact_order_items": [
            "Quantity", "UnitPrice", "Discount", "Tax",
            "Revenue", "NetRevenue", "CostAmount",
        ],
        "fact_payments": ["Amount"],
        "fact_inventory": [
            "OpeningStock", "ReceivedQuantity", "SoldQuantity",
            "ClosingStock", "UnitCost", "InventoryValue",
        ],
        "fact_deliveries": [
            "DeliveryTimeMinutes", "TargetDeliveryMinutes",
        ],
    }

    for dataset_name, columns in numeric_rules.items():
        for column in columns:
            validate_non_negative(
                datasets[dataset_name],
                dataset_name,
                column,
            )


# ============================================================
# BUSINESS CALCULATIONS
# ============================================================

def validate_product_margin(products: pd.DataFrame) -> None:
    required = {"UnitPrice", "CostPrice", "Margin"}
    if not required.issubset(products.columns):
        add_result(
            "Product Margin", "dim_products", "WARNING",
            "Required margin columns are missing.", 0,
        )
        return

    expected = (
        pd.to_numeric(products["UnitPrice"], errors="coerce")
        - pd.to_numeric(products["CostPrice"], errors="coerce")
    )
    actual = pd.to_numeric(products["Margin"], errors="coerce")
    invalid = int(
        ((expected - actual).abs() > 0.01).fillna(True).sum()
    )

    record_count(
        "Product Margin",
        "dim_products",
        invalid,
        (
            "Margin matches UnitPrice - CostPrice."
            if invalid == 0
            else f"{invalid} products have an incorrect or missing margin."
        ),
    )


def validate_order_item_calculations(order_items: pd.DataFrame) -> None:
    required = {
        "Quantity", "UnitPrice", "Revenue",
        "Discount", "Tax", "NetRevenue",
    }
    if not required.issubset(order_items.columns):
        add_result(
            "Order Item Calculations", "fact_order_items", "WARNING",
            "One or more calculation columns are missing.", 0,
        )
        return

    quantity = pd.to_numeric(order_items["Quantity"], errors="coerce")
    price = pd.to_numeric(order_items["UnitPrice"], errors="coerce")
    revenue = pd.to_numeric(order_items["Revenue"], errors="coerce")
    discount = pd.to_numeric(order_items["Discount"], errors="coerce")
    tax = pd.to_numeric(order_items["Tax"], errors="coerce")
    net_revenue = pd.to_numeric(
        order_items["NetRevenue"], errors="coerce"
    )

    expected_revenue = quantity * price
    invalid_revenue = int(
        ((expected_revenue - revenue).abs() > 0.05).fillna(True).sum()
    )
    record_count(
        "Revenue Calculation",
        "fact_order_items",
        invalid_revenue,
        (
            "Revenue matches Quantity × UnitPrice."
            if invalid_revenue == 0
            else f"{invalid_revenue} rows have incorrect or missing Revenue."
        ),
    )

    expected_net = revenue - discount + tax
    invalid_net = int(
        ((expected_net - net_revenue).abs() > 0.05).fillna(True).sum()
    )
    record_count(
        "Net Revenue Calculation",
        "fact_order_items",
        invalid_net,
        (
            "NetRevenue matches Revenue - Discount + Tax."
            if invalid_net == 0
            else f"{invalid_net} rows have incorrect or missing NetRevenue."
        ),
    )


# ============================================================
# ORDER, RETURN, PAYMENT AND DELIVERY RULES
# ============================================================

def validate_order_status(orders: pd.DataFrame) -> None:
    valid_statuses = {"Delivered", "Cancelled", "Returned"}
    invalid_status = int(
        (~orders["OrderStatus"].isin(valid_statuses)).sum()
    )
    record_count(
        "Order Status", "fact_orders", invalid_status,
        (
            "All order statuses are valid."
            if invalid_status == 0
            else f"{invalid_status} invalid order statuses."
        ),
    )

    cancelled_mismatch = int(
        (
            orders["OrderStatus"].eq("Cancelled")
            & ~orders["CancellationStatus"].eq("Cancelled")
        ).sum()
    )
    record_count(
        "Cancellation Status", "fact_orders", cancelled_mismatch,
        (
            "Cancelled orders have the correct cancellation status."
            if cancelled_mismatch == 0
            else f"{cancelled_mismatch} cancelled orders have inconsistent status."
        ),
    )

    return_mismatch = int(
        (
            orders["OrderStatus"].eq("Returned")
            & ~orders["ReturnStatus"].eq("Returned")
        ).sum()
    )
    record_count(
        "Return Status", "fact_orders", return_mismatch,
        (
            "Returned orders have the correct return status."
            if return_mismatch == 0
            else f"{return_mismatch} returned orders have inconsistent status."
        ),
    )


def validate_returns(
    orders: pd.DataFrame,
    returns: pd.DataFrame,
) -> None:
    if returns.empty:
        add_result(
            "Return Records", "fact_returns", "WARNING",
            "No return records found.", 0,
        )
        return

    returned_ids = set(
        orders.loc[
            orders["OrderStatus"].eq("Returned"), "OrderID"
        ].dropna()
    )
    invalid = int(
        (~returns["OrderID"].isin(returned_ids)).sum()
    )
    record_count(
        "Return Order Status",
        "fact_returns",
        invalid,
        (
            "All return records belong to Returned orders."
            if invalid == 0
            else f"{invalid} return records belong to non-returned orders."
        ),
    )


def validate_payments(
    orders: pd.DataFrame,
    payments: pd.DataFrame,
) -> None:
    order_ids = set(orders["OrderID"].dropna())
    payment_ids = set(payments["OrderID"].dropna())

    missing_payment = len(order_ids - payment_ids)
    extra_payment = len(payment_ids - order_ids)

    record_count(
        "Payment Coverage",
        "fact_payments",
        missing_payment + extra_payment,
        (
            f"Payment order IDs cover all {len(order_ids):,} orders."
            if missing_payment + extra_payment == 0
            else (
                f"{missing_payment} orders have no payment record; "
                f"{extra_payment} payment order IDs are not in orders."
            )
        ),
        failure_status="WARNING",
    )

    duplicate_orders = int(
        payments["OrderID"].dropna().duplicated().sum()
    )
    record_count(
        "Payment Per Order",
        "fact_payments",
        duplicate_orders,
        (
            "No order has multiple payment records."
            if duplicate_orders == 0
            else f"{duplicate_orders} duplicate payment-order links."
        ),
        failure_status="WARNING",
    )


def validate_deliveries(
    orders: pd.DataFrame,
    deliveries: pd.DataFrame,
) -> None:
    cancelled_order_ids = set(
        orders.loc[
            orders["OrderStatus"].eq("Cancelled"), "OrderID"
        ].dropna()
    )
    cancelled_delivery_ids = set(
        deliveries.loc[
            deliveries["DeliveryStatus"].eq("Cancelled"), "OrderID"
        ].dropna()
    )
    missing_mapping = len(cancelled_order_ids - cancelled_delivery_ids)

    record_count(
        "Cancelled Delivery Mapping",
        "fact_deliveries",
        missing_mapping,
        (
            "Cancelled orders are marked as cancelled in delivery records."
            if missing_mapping == 0
            else f"{missing_mapping} cancelled orders need delivery review."
        ),
        failure_status="WARNING",
    )

    active = deliveries["DeliveryStatus"].ne("Cancelled")
    missing_time = int(
        deliveries.loc[active, "DeliveryTimeMinutes"].isna().sum()
    )
    record_count(
        "Delivery Time",
        "fact_deliveries",
        missing_time,
        (
            "Active deliveries have delivery times."
            if missing_time == 0
            else f"{missing_time} active deliveries have missing delivery time."
        ),
    )


# ============================================================
# INVENTORY, DATES AND COVERAGE
# ============================================================

def validate_inventory(inventory: pd.DataFrame) -> None:
    expected_closing = (
        inventory["OpeningStock"]
        + inventory["ReceivedQuantity"]
        - inventory["SoldQuantity"]
    ).clip(lower=0)

    closing_difference = (
        expected_closing - inventory["ClosingStock"]
    ).abs()
    invalid_closing = int((closing_difference > 0.01).sum())

    record_count(
        "Inventory Calculation",
        "fact_inventory",
        invalid_closing,
        (
            "ClosingStock follows OpeningStock + ReceivedQuantity - SoldQuantity."
            if invalid_closing == 0
            else f"{invalid_closing} inventory records have incorrect closing stock."
        ),
        failure_status="WARNING",
    )

    expected_value = (
        inventory["ClosingStock"] * inventory["UnitCost"]
    ).round(2)
    actual_value = inventory["InventoryValue"].round(2)
    invalid_value = int(
        ((expected_value - actual_value).abs() > 0.05).sum()
    )

    record_count(
        "Inventory Value",
        "fact_inventory",
        invalid_value,
        (
            "InventoryValue matches ClosingStock × UnitCost."
            if invalid_value == 0
            else f"{invalid_value} inventory values are incorrect."
        ),
    )


def validate_dates(datasets: Dict[str, pd.DataFrame]) -> None:
    start_date = pd.Timestamp(config.DATA_START_DATE)
    end_date = pd.Timestamp(config.DATA_END_DATE)

    orders = datasets["fact_orders"].copy()
    orders["OrderDate"] = pd.to_datetime(
        orders["OrderDate"], errors="coerce"
    )

    outside_period = (
        orders["OrderDate"].isna()
        | orders["OrderDate"].lt(start_date)
        | orders["OrderDate"].gt(end_date)
    )
    invalid_dates = int(outside_period.sum())

    record_count(
        "Order Date Range",
        "fact_orders",
        invalid_dates,
        (
            "All order dates are valid and within the configured business period."
            if invalid_dates == 0
            else f"{invalid_dates} order dates are missing, invalid, or outside the configured period."
        ),
    )

    customers = datasets["dim_customers"].copy()
    customers["SignupDate"] = pd.to_datetime(
        customers["SignupDate"], errors="coerce"
    )

    signup_lookup = customers.set_index("CustomerID")["SignupDate"]
    order_signup = orders["CustomerID"].map(signup_lookup)
    before_signup = (
        orders["OrderDate"].notna()
        & order_signup.notna()
        & orders["OrderDate"].lt(order_signup)
    )
    invalid_signup_orders = int(before_signup.sum())

    record_count(
        "Signup Before Order",
        "fact_orders",
        invalid_signup_orders,
        (
            "Customers do not place orders before signup."
            if invalid_signup_orders == 0
            else f"{invalid_signup_orders} orders occur before customer signup."
        ),
        failure_status="WARNING",
    )


def validate_dataset_sizes(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    requirements = {
        "dim_customers": config.CUSTOMER_COUNT,
        "dim_products": config.PRODUCT_COUNT,
        "fact_orders": config.ORDER_COUNT,
        "fact_order_items": config.MIN_ORDER_ITEMS,
        "fact_payments": config.PAYMENT_COUNT,
    }

    for dataset_name, minimum in requirements.items():
        actual = len(datasets[dataset_name])
        shortfall = max(0, int(minimum) - actual)

        record_count(
            "Dataset Size",
            dataset_name,
            shortfall,
            (
                f"Dataset has {actual:,} rows; minimum is {int(minimum):,}."
                if shortfall == 0
                else (
                    f"Dataset has {actual:,} rows; "
                    f"{shortfall:,} additional rows are required."
                )
            ),
        )


def validate_order_item_coverage(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
) -> None:
    order_ids = set(orders["OrderID"].dropna())
    item_order_ids = set(order_items["OrderID"].dropna())
    missing = len(order_ids - item_order_ids)

    record_count(
        "Order Item Coverage",
        "fact_order_items",
        missing,
        (
            "Every order has at least one order-item record."
            if missing == 0
            else f"{missing} orders have no order-item records."
        ),
    )


def validate_customer_order_coverage(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:
    customer_ids = set(customers["CustomerID"].dropna())
    order_customer_ids = set(orders["CustomerID"].dropna())
    invalid = len(order_customer_ids - customer_ids)

    record_count(
        "Customer Order Coverage",
        "fact_orders",
        invalid,
        (
            "All order customer IDs exist in the customer dimension."
            if invalid == 0
            else f"{invalid} customer IDs in orders do not exist in customers."
        ),
    )


def validate_location_consistency(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:
    customer_locations = customers.set_index("CustomerID")[["City", "State"]]
    order_locations = orders[["CustomerID", "City", "State"]].copy()
    merged = order_locations.merge(
        customer_locations,
        left_on="CustomerID",
        right_index=True,
        how="left",
        suffixes=("_order", "_customer"),
    )

    comparable = merged["City_customer"].notna() & merged["State_customer"].notna()
    mismatch = comparable & (
        merged["City_order"].astype(str).str.strip().str.casefold()
        != merged["City_customer"].astype(str).str.strip().str.casefold()
    )
    mismatch |= comparable & (
        merged["State_order"].astype(str).str.strip().str.casefold()
        != merged["State_customer"].astype(str).str.strip().str.casefold()
    )
    mismatch_count = int(mismatch.sum())

    record_count(
        "Customer Location Consistency",
        "fact_orders",
        mismatch_count,
        (
            "Order city/state matches customer master."
            if mismatch_count == 0
            else f"{mismatch_count} orders have customer location mismatches."
        ),
    )


# ============================================================
# SUMMARY AND MAIN PIPELINE
# ============================================================

def create_summary(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        passed = failed = warnings = 0
    else:
        passed = int(results["Status"].eq("PASS").sum())
        failed = int(results["Status"].eq("FAIL").sum())
        warnings = int(results["Status"].eq("WARNING").sum())

    total = len(results)
    overall = "FAIL" if failed else ("WARNING" if warnings else "PASS")

    return pd.DataFrame(
        [{
            "TotalChecks": total,
            "Passed": passed,
            "Failed": failed,
            "Warnings": warnings,
            "OverallStatus": overall,
        }]
    )


def validate_all_data() -> Dict[str, pd.DataFrame]:
    """Run all QuickCart data checks and save CSV reports."""
    global VALIDATION_RESULTS
    VALIDATION_RESULTS = []

    print("\n" + "=" * 80)
    print(" QUICKCART DATA VALIDATION")
    print("=" * 80)

    LOGGER.info("Starting QuickCart data validation.")

    print("\n[1/8] Loading processed datasets...")
    datasets = load_all_datasets()

    for name, dataframe in datasets.items():
        print(f"  {name:<22} {len(dataframe):>12,} rows")

    print("\n[2/8] Validating required columns...")
    validate_required_columns(datasets)

    print("\n[3/8] Validating primary keys and missing values...")
    validate_primary_keys(datasets)
    validate_missing_values(datasets)

    print("\n[4/8] Validating foreign-key relationships...")
    validate_all_foreign_keys(datasets)

    print("\n[5/8] Validating business rules...")
    validate_numeric_fields(datasets)
    validate_product_margin(datasets["dim_products"])
    validate_order_item_calculations(datasets["fact_order_items"])
    validate_order_status(datasets["fact_orders"])
    validate_returns(datasets["fact_orders"], datasets["fact_returns"])
    validate_payments(datasets["fact_orders"], datasets["fact_payments"])
    validate_deliveries(datasets["fact_orders"], datasets["fact_deliveries"])
    validate_inventory(datasets["fact_inventory"])

    print("\n[6/8] Validating dates and dataset coverage...")
    validate_dates(datasets)
    validate_dataset_sizes(datasets)
    validate_order_item_coverage(
        datasets["fact_orders"], datasets["fact_order_items"]
    )
    validate_customer_order_coverage(
        datasets["dim_customers"], datasets["fact_orders"]
    )
    validate_location_consistency(
        datasets["dim_customers"], datasets["fact_orders"]
    )

    print("\n[7/8] Creating reports...")
    results = pd.DataFrame(
        VALIDATION_RESULTS,
        columns=[
            "CheckName", "Dataset", "Status", "AffectedRows", "Message",
        ],
    )
    summary = create_summary(results)

    report_path = PROCESSED_DIR / "validation_report.csv"
    summary_path = PROCESSED_DIR / "validation_summary.csv"

    results.to_csv(report_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    print("\n[8/8] Validation results")
    print("-" * 80)
    print(results.to_string(index=False))
    print("\nVALIDATION SUMMARY")
    print(summary.to_string(index=False))
    print("-" * 80)
    print(f"Report : {report_path}")
    print(f"Summary: {summary_path}")

    overall = summary.iloc[0]["OverallStatus"]
    if overall == "PASS":
        print("\nQUICKCART DATA VALIDATION PASSED")
    elif overall == "WARNING":
        print("\nVALIDATION COMPLETED WITH WARNINGS - REVIEW THE REPORT")
    else:
        print("\nVALIDATION FAILED - FIX THE REPORTED ISSUES")

    LOGGER.info("QuickCart data validation completed with status: %s", overall)

    return {
        "results": results,
        "summary": summary,
        "datasets": datasets,
    }


# Backward-compatible function names
validate_data = validate_all_data
run = validate_all_data


if __name__ == "__main__":
    try:
        validate_all_data()
    except Exception:
        LOGGER.exception("Data validation failed.")
        raise
"""
QUICKCART - Data Validation Module

Validates the processed QuickCart datasets and creates:
    data/processed/validation_report.csv
    data/processed/validation_summary.csv

Run:
    python data_validation.py
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

import config


# ============================================================
# LOGGING AND PATHS
# ============================================================

LOGGER = logging.getLogger("QuickCart.DataValidation")

if not LOGGER.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

PROCESSED_DIR = Path(config.PROCESSED_DATA_DIR)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

VALIDATION_RESULTS: List[dict] = []


def add_result(
    check_name: str,
    dataset: str,
    status: str,
    message: str,
    affected_rows: int = 0,
) -> None:
    """Add one validation result."""
    VALIDATION_RESULTS.append(
        {
            "CheckName": check_name,
            "Dataset": dataset,
            "Status": status,
            "AffectedRows": int(affected_rows),
            "Message": str(message),
        }
    )


def record_count(
    check_name: str,
    dataset: str,
    invalid_count: int,
    message: str,
    failure_status: str = "FAIL",
) -> None:
    """Record a PASS when invalid_count is zero; otherwise record an issue."""
    status = "PASS" if invalid_count == 0 else failure_status
    add_result(
        check_name,
        dataset,
        status,
        message,
        invalid_count,
    )


# ============================================================
# DATASET DEFINITIONS
# ============================================================

REQUIRED_COLUMNS = {
    "dim_location": [
        "LocationID", "City", "State", "Region", "Tier",
    ],
    "dim_customers": [
        "CustomerID", "Name", "Gender", "Age", "City", "State",
        "SignupDate", "CustomerSegment",
    ],
    "dim_products": [
        "ProductID", "ProductName", "Category", "SubCategory",
        "Brand", "UnitPrice", "CostPrice", "Margin",
        "StockQuantity", "Supplier",
    ],
    "dim_date": [
        "DateKey", "Date", "Year", "Quarter", "MonthNumber",
        "MonthName", "MonthShort", "WeekNumber", "DayOfMonth",
        "DayName", "DayOfWeek", "IsWeekend",
    ],
    "fact_orders": [
        "OrderID", "CustomerID", "OrderDate", "City", "State",
        "PaymentMethod", "OrderStatus", "DeliveryTime",
        "ReturnStatus", "CancellationStatus",
    ],
    "fact_order_items": [
        "OrderItemID", "OrderID", "ProductID", "Quantity",
        "UnitPrice", "Discount", "DiscountPercent", "Tax",
        "TaxRate", "Revenue", "NetRevenue", "CostAmount",
    ],
    "fact_payments": [
        "PaymentID", "OrderID", "PaymentDate", "PaymentMethod",
        "Amount", "PaymentStatus", "TransactionID",
    ],
    "fact_returns": [
        "ReturnID", "OrderID", "ReturnDate", "ReturnReason",
        "RefundAmount", "ReturnStatus",
    ],
    "fact_deliveries": [
        "DeliveryID", "OrderID", "DeliveryPartner",
        "DeliveryStatus", "DeliveryTimeMinutes",
        "TargetDeliveryMinutes", "DeliveredAt",
    ],
    "fact_inventory": [
        "InventoryID", "SnapshotDate", "ProductID",
        "OpeningStock", "ReceivedQuantity", "SoldQuantity",
        "ClosingStock", "UnitCost", "InventoryValue",
        "InventoryStatus",
    ],
}

PRIMARY_KEYS = {
    "dim_location": "LocationID",
    "dim_customers": "CustomerID",
    "dim_products": "ProductID",
    "dim_date": "DateKey",
    "fact_orders": "OrderID",
    "fact_order_items": "OrderItemID",
    "fact_payments": "PaymentID",
    "fact_returns": "ReturnID",
    "fact_deliveries": "DeliveryID",
    "fact_inventory": "InventoryID",
}


# ============================================================
# LOAD DATA
# ============================================================

def load_processed(filename: str) -> pd.DataFrame:
    """Load one processed CSV file."""
    path = PROCESSED_DIR / filename

    if not path.is_file():
        raise FileNotFoundError(f"Processed file not found: {path}")

    return pd.read_csv(path, low_memory=False)


def load_all_datasets() -> Dict[str, pd.DataFrame]:
    """Load all ten processed QuickCart datasets."""
    return {
        name: load_processed(f"{name}.csv")
        for name in REQUIRED_COLUMNS
    }


# ============================================================
# REQUIRED COLUMNS AND PRIMARY KEYS
# ============================================================

def validate_required_columns(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    for dataset_name, required_columns in REQUIRED_COLUMNS.items():
        dataframe = datasets[dataset_name]
        missing = [
            column for column in required_columns
            if column not in dataframe.columns
        ]

        record_count(
            "Required Columns",
            dataset_name,
            len(missing),
            (
                "All required columns are present."
                if not missing
                else "Missing columns: " + ", ".join(missing)
            ),
        )


def validate_primary_keys(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    for dataset_name, primary_key in PRIMARY_KEYS.items():
        dataframe = datasets[dataset_name]

        if primary_key not in dataframe.columns:
            add_result(
                "Primary Key",
                dataset_name,
                "WARNING",
                f"Cannot validate missing column: {primary_key}.",
                0,
            )
            continue

        missing_count = int(dataframe[primary_key].isna().sum())
        duplicate_count = int(
            dataframe[primary_key].dropna().duplicated().sum()
        )

        record_count(
            "Primary Key Missing",
            dataset_name,
            missing_count,
            (
                f"No missing {primary_key} values."
                if missing_count == 0
                else f"{missing_count} missing {primary_key} values."
            ),
        )
        record_count(
            "Primary Key Duplicate",
            dataset_name,
            duplicate_count,
            (
                f"{primary_key} values are unique."
                if duplicate_count == 0
                else f"{duplicate_count} duplicate {primary_key} values."
            ),
        )


# ============================================================
# MISSING VALUES
# ============================================================

def validate_missing_values(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    """
    Count missing cells. DeliveryTime on cancelled orders and
    missing delivery attributes on cancelled deliveries are allowed.
    """
    for dataset_name, dataframe in datasets.items():
        total_missing = int(dataframe.isna().sum().sum())
        allowed_missing = 0

        if (
            dataset_name == "fact_orders"
            and {"OrderStatus", "DeliveryTime"}.issubset(dataframe.columns)
        ):
            cancelled = dataframe["OrderStatus"].eq("Cancelled")
            allowed_missing = int(
                dataframe.loc[cancelled, "DeliveryTime"].isna().sum()
            )

        elif (
            dataset_name == "fact_deliveries"
            and "DeliveryStatus" in dataframe.columns
        ):
            cancelled = dataframe["DeliveryStatus"].eq("Cancelled")
            allowed_missing = int(
                dataframe.loc[cancelled].isna().sum().sum()
            )

        unexpected_missing = max(0, total_missing - allowed_missing)

        add_result(
            "Missing Values",
            dataset_name,
            "PASS" if unexpected_missing == 0 else "WARNING",
            (
                f"Total missing cells: {total_missing}; "
                f"allowed missing cells: {allowed_missing}; "
                f"unexpected missing cells: {unexpected_missing}."
            ),
            unexpected_missing,
        )


# ============================================================
# FOREIGN KEYS
# ============================================================

def validate_foreign_key(
    child_df: pd.DataFrame,
    parent_df: pd.DataFrame,
    child_column: str,
    parent_column: str,
    relationship_name: str,
) -> None:
    """Check non-null child keys against non-null parent keys."""
    if child_column not in child_df.columns:
        add_result(
            "Foreign Key", relationship_name, "WARNING",
            f"Child column {child_column} is missing.", 0,
        )
        return

    if parent_column not in parent_df.columns:
        add_result(
            "Foreign Key", relationship_name, "WARNING",
            f"Parent column {parent_column} is missing.", 0,
        )
        return

    child_values = child_df[child_column]
    parent_values = set(parent_df[parent_column].dropna())

    non_null_child = child_values.notna()
    invalid_mask = (
        non_null_child
        & ~child_values.isin(parent_values)
    )
    invalid_count = int(invalid_mask.sum())

    record_count(
        "Foreign Key",
        relationship_name,
        invalid_count,
        (
            f"{child_column} references valid {parent_column} values."
            if invalid_count == 0
            else f"{invalid_count} non-null child keys have no parent match."
        ),
    )


def validate_all_foreign_keys(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    relationships = [
        ("fact_orders", "dim_customers", "CustomerID", "CustomerID",
         "Orders -> Customers"),
        ("fact_order_items", "fact_orders", "OrderID", "OrderID",
         "Order Items -> Orders"),
        ("fact_order_items", "dim_products", "ProductID", "ProductID",
         "Order Items -> Products"),
        ("fact_payments", "fact_orders", "OrderID", "OrderID",
         "Payments -> Orders"),
        ("fact_returns", "fact_orders", "OrderID", "OrderID",
         "Returns -> Orders"),
        ("fact_deliveries", "fact_orders", "OrderID", "OrderID",
         "Deliveries -> Orders"),
        ("fact_inventory", "dim_products", "ProductID", "ProductID",
         "Inventory -> Products"),
    ]

    for child, parent, child_col, parent_col, label in relationships:
        validate_foreign_key(
            datasets[child],
            datasets[parent],
            child_col,
            parent_col,
            label,
        )


# ============================================================
# NUMERIC RULES
# ============================================================

def validate_non_negative(
    dataframe: pd.DataFrame,
    dataset_name: str,
    column: str,
) -> None:
    if column not in dataframe.columns:
        add_result(
            "Non-Negative Values", dataset_name, "WARNING",
            f"Cannot validate missing column {column}.", 0,
        )
        return

    values = pd.to_numeric(dataframe[column], errors="coerce")
    invalid_count = int((values < 0).sum())

    record_count(
        "Non-Negative Values",
        dataset_name,
        invalid_count,
        (
            f"{column} contains no negative values."
            if invalid_count == 0
            else f"{invalid_count} negative values found in {column}."
        ),
    )


def validate_numeric_fields(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    numeric_rules = {
        "dim_products": [
            "UnitPrice", "CostPrice", "Margin", "StockQuantity",
        ],
        "fact_order_items": [
            "Quantity", "UnitPrice", "Discount", "Tax",
            "Revenue", "NetRevenue", "CostAmount",
        ],
        "fact_payments": ["Amount"],
        "fact_inventory": [
            "OpeningStock", "ReceivedQuantity", "SoldQuantity",
            "ClosingStock", "UnitCost", "InventoryValue",
        ],
        "fact_deliveries": [
            "DeliveryTimeMinutes", "TargetDeliveryMinutes",
        ],
    }

    for dataset_name, columns in numeric_rules.items():
        for column in columns:
            validate_non_negative(
                datasets[dataset_name],
                dataset_name,
                column,
            )


# ============================================================
# BUSINESS CALCULATIONS
# ============================================================

def validate_product_margin(products: pd.DataFrame) -> None:
    required = {"UnitPrice", "CostPrice", "Margin"}
    if not required.issubset(products.columns):
        add_result(
            "Product Margin", "dim_products", "WARNING",
            "Required margin columns are missing.", 0,
        )
        return

    expected = (
        pd.to_numeric(products["UnitPrice"], errors="coerce")
        - pd.to_numeric(products["CostPrice"], errors="coerce")
    )
    actual = pd.to_numeric(products["Margin"], errors="coerce")
    invalid = int(
        ((expected - actual).abs() > 0.01).fillna(True).sum()
    )

    record_count(
        "Product Margin",
        "dim_products",
        invalid,
        (
            "Margin matches UnitPrice - CostPrice."
            if invalid == 0
            else f"{invalid} products have an incorrect or missing margin."
        ),
    )


def validate_order_item_calculations(order_items: pd.DataFrame) -> None:
    required = {
        "Quantity", "UnitPrice", "Revenue",
        "Discount", "Tax", "NetRevenue",
    }
    if not required.issubset(order_items.columns):
        add_result(
            "Order Item Calculations", "fact_order_items", "WARNING",
            "One or more calculation columns are missing.", 0,
        )
        return

    quantity = pd.to_numeric(order_items["Quantity"], errors="coerce")
    price = pd.to_numeric(order_items["UnitPrice"], errors="coerce")
    revenue = pd.to_numeric(order_items["Revenue"], errors="coerce")
    discount = pd.to_numeric(order_items["Discount"], errors="coerce")
    tax = pd.to_numeric(order_items["Tax"], errors="coerce")
    net_revenue = pd.to_numeric(
        order_items["NetRevenue"], errors="coerce"
    )

    expected_revenue = quantity * price
    invalid_revenue = int(
        ((expected_revenue - revenue).abs() > 0.05).fillna(True).sum()
    )
    record_count(
        "Revenue Calculation",
        "fact_order_items",
        invalid_revenue,
        (
            "Revenue matches Quantity × UnitPrice."
            if invalid_revenue == 0
            else f"{invalid_revenue} rows have incorrect or missing Revenue."
        ),
    )

    expected_net = revenue - discount + tax
    invalid_net = int(
        ((expected_net - net_revenue).abs() > 0.05).fillna(True).sum()
    )
    record_count(
        "Net Revenue Calculation",
        "fact_order_items",
        invalid_net,
        (
            "NetRevenue matches Revenue - Discount + Tax."
            if invalid_net == 0
            else f"{invalid_net} rows have incorrect or missing NetRevenue."
        ),
    )


# ============================================================
# ORDER, RETURN, PAYMENT AND DELIVERY RULES
# ============================================================

def validate_order_status(orders: pd.DataFrame) -> None:
    valid_statuses = {"Delivered", "Cancelled", "Returned"}
    invalid_status = int(
        (~orders["OrderStatus"].isin(valid_statuses)).sum()
    )
    record_count(
        "Order Status", "fact_orders", invalid_status,
        (
            "All order statuses are valid."
            if invalid_status == 0
            else f"{invalid_status} invalid order statuses."
        ),
    )

    cancelled_mismatch = int(
        (
            orders["OrderStatus"].eq("Cancelled")
            & ~orders["CancellationStatus"].eq("Cancelled")
        ).sum()
    )
    record_count(
        "Cancellation Status", "fact_orders", cancelled_mismatch,
        (
            "Cancelled orders have the correct cancellation status."
            if cancelled_mismatch == 0
            else f"{cancelled_mismatch} cancelled orders have inconsistent status."
        ),
    )

    return_mismatch = int(
        (
            orders["OrderStatus"].eq("Returned")
            & ~orders["ReturnStatus"].eq("Returned")
        ).sum()
    )
    record_count(
        "Return Status", "fact_orders", return_mismatch,
        (
            "Returned orders have the correct return status."
            if return_mismatch == 0
            else f"{return_mismatch} returned orders have inconsistent status."
        ),
    )


def validate_returns(
    orders: pd.DataFrame,
    returns: pd.DataFrame,
) -> None:
    if returns.empty:
        add_result(
            "Return Records", "fact_returns", "WARNING",
            "No return records found.", 0,
        )
        return

    returned_ids = set(
        orders.loc[
            orders["OrderStatus"].eq("Returned"), "OrderID"
        ].dropna()
    )
    invalid = int(
        (~returns["OrderID"].isin(returned_ids)).sum()
    )
    record_count(
        "Return Order Status",
        "fact_returns",
        invalid,
        (
            "All return records belong to Returned orders."
            if invalid == 0
            else f"{invalid} return records belong to non-returned orders."
        ),
    )


def validate_payments(
    orders: pd.DataFrame,
    payments: pd.DataFrame,
) -> None:
    order_ids = set(orders["OrderID"].dropna())
    payment_ids = set(payments["OrderID"].dropna())

    missing_payment = len(order_ids - payment_ids)
    extra_payment = len(payment_ids - order_ids)

    record_count(
        "Payment Coverage",
        "fact_payments",
        missing_payment + extra_payment,
        (
            f"Payment order IDs cover all {len(order_ids):,} orders."
            if missing_payment + extra_payment == 0
            else (
                f"{missing_payment} orders have no payment record; "
                f"{extra_payment} payment order IDs are not in orders."
            )
        ),
        failure_status="WARNING",
    )

    duplicate_orders = int(
        payments["OrderID"].dropna().duplicated().sum()
    )
    record_count(
        "Payment Per Order",
        "fact_payments",
        duplicate_orders,
        (
            "No order has multiple payment records."
            if duplicate_orders == 0
            else f"{duplicate_orders} duplicate payment-order links."
        ),
        failure_status="WARNING",
    )


def validate_deliveries(
    orders: pd.DataFrame,
    deliveries: pd.DataFrame,
) -> None:
    cancelled_order_ids = set(
        orders.loc[
            orders["OrderStatus"].eq("Cancelled"), "OrderID"
        ].dropna()
    )
    cancelled_delivery_ids = set(
        deliveries.loc[
            deliveries["DeliveryStatus"].eq("Cancelled"), "OrderID"
        ].dropna()
    )
    missing_mapping = len(cancelled_order_ids - cancelled_delivery_ids)

    record_count(
        "Cancelled Delivery Mapping",
        "fact_deliveries",
        missing_mapping,
        (
            "Cancelled orders are marked as cancelled in delivery records."
            if missing_mapping == 0
            else f"{missing_mapping} cancelled orders need delivery review."
        ),
        failure_status="WARNING",
    )

    active = deliveries["DeliveryStatus"].ne("Cancelled")
    missing_time = int(
        deliveries.loc[active, "DeliveryTimeMinutes"].isna().sum()
    )
    record_count(
        "Delivery Time",
        "fact_deliveries",
        missing_time,
        (
            "Active deliveries have delivery times."
            if missing_time == 0
            else f"{missing_time} active deliveries have missing delivery time."
        ),
    )


# ============================================================
# INVENTORY, DATES AND COVERAGE
# ============================================================

def validate_inventory(inventory: pd.DataFrame) -> None:
    expected_closing = (
        inventory["OpeningStock"]
        + inventory["ReceivedQuantity"]
        - inventory["SoldQuantity"]
    ).clip(lower=0)

    closing_difference = (
        expected_closing - inventory["ClosingStock"]
    ).abs()
    invalid_closing = int((closing_difference > 0.01).sum())

    record_count(
        "Inventory Calculation",
        "fact_inventory",
        invalid_closing,
        (
            "ClosingStock follows OpeningStock + ReceivedQuantity - SoldQuantity."
            if invalid_closing == 0
            else f"{invalid_closing} inventory records have incorrect closing stock."
        ),
        failure_status="WARNING",
    )

    expected_value = (
        inventory["ClosingStock"] * inventory["UnitCost"]
    ).round(2)
    actual_value = inventory["InventoryValue"].round(2)
    invalid_value = int(
        ((expected_value - actual_value).abs() > 0.05).sum()
    )

    record_count(
        "Inventory Value",
        "fact_inventory",
        invalid_value,
        (
            "InventoryValue matches ClosingStock × UnitCost."
            if invalid_value == 0
            else f"{invalid_value} inventory values are incorrect."
        ),
    )


def validate_dates(datasets: Dict[str, pd.DataFrame]) -> None:
    start_date = pd.Timestamp(config.DATA_START_DATE)
    end_date = pd.Timestamp(config.DATA_END_DATE)

    orders = datasets["fact_orders"].copy()
    orders["OrderDate"] = pd.to_datetime(
        orders["OrderDate"], errors="coerce"
    )

    outside_period = (
        orders["OrderDate"].isna()
        | orders["OrderDate"].lt(start_date)
        | orders["OrderDate"].gt(end_date)
    )
    invalid_dates = int(outside_period.sum())

    record_count(
        "Order Date Range",
        "fact_orders",
        invalid_dates,
        (
            "All order dates are valid and within the configured business period."
            if invalid_dates == 0
            else f"{invalid_dates} order dates are missing, invalid, or outside the configured period."
        ),
    )

    customers = datasets["dim_customers"].copy()
    customers["SignupDate"] = pd.to_datetime(
        customers["SignupDate"], errors="coerce"
    )

    signup_lookup = customers.set_index("CustomerID")["SignupDate"]
    order_signup = orders["CustomerID"].map(signup_lookup)
    before_signup = (
        orders["OrderDate"].notna()
        & order_signup.notna()
        & orders["OrderDate"].lt(order_signup)
    )
    invalid_signup_orders = int(before_signup.sum())

    record_count(
        "Signup Before Order",
        "fact_orders",
        invalid_signup_orders,
        (
            "Customers do not place orders before signup."
            if invalid_signup_orders == 0
            else f"{invalid_signup_orders} orders occur before customer signup."
        ),
        failure_status="WARNING",
    )


def validate_dataset_sizes(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    requirements = {
        "dim_customers": config.CUSTOMER_COUNT,
        "dim_products": config.PRODUCT_COUNT,
        "fact_orders": config.ORDER_COUNT,
        "fact_order_items": config.MIN_ORDER_ITEMS,
        "fact_payments": config.PAYMENT_COUNT,
    }

    for dataset_name, minimum in requirements.items():
        actual = len(datasets[dataset_name])
        shortfall = max(0, int(minimum) - actual)

        record_count(
            "Dataset Size",
            dataset_name,
            shortfall,
            (
                f"Dataset has {actual:,} rows; minimum is {int(minimum):,}."
                if shortfall == 0
                else (
                    f"Dataset has {actual:,} rows; "
                    f"{shortfall:,} additional rows are required."
                )
            ),
        )


def validate_order_item_coverage(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
) -> None:
    order_ids = set(orders["OrderID"].dropna())
    item_order_ids = set(order_items["OrderID"].dropna())
    missing = len(order_ids - item_order_ids)

    record_count(
        "Order Item Coverage",
        "fact_order_items",
        missing,
        (
            "Every order has at least one order-item record."
            if missing == 0
            else f"{missing} orders have no order-item records."
        ),
    )


def validate_customer_order_coverage(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:
    customer_ids = set(customers["CustomerID"].dropna())
    order_customer_ids = set(orders["CustomerID"].dropna())
    invalid = len(order_customer_ids - customer_ids)

    record_count(
        "Customer Order Coverage",
        "fact_orders",
        invalid,
        (
            "All order customer IDs exist in the customer dimension."
            if invalid == 0
            else f"{invalid} customer IDs in orders do not exist in customers."
        ),
    )


def validate_location_consistency(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:
    customer_locations = customers.set_index("CustomerID")[["City", "State"]]
    order_locations = orders[["CustomerID", "City", "State"]].copy()
    merged = order_locations.merge(
        customer_locations,
        left_on="CustomerID",
        right_index=True,
        how="left",
        suffixes=("_order", "_customer"),
    )

    comparable = merged["City_customer"].notna() & merged["State_customer"].notna()
    mismatch = comparable & (
        merged["City_order"].astype(str).str.strip().str.casefold()
        != merged["City_customer"].astype(str).str.strip().str.casefold()
    )
    mismatch |= comparable & (
        merged["State_order"].astype(str).str.strip().str.casefold()
        != merged["State_customer"].astype(str).str.strip().str.casefold()
    )
    mismatch_count = int(mismatch.sum())

    record_count(
        "Customer Location Consistency",
        "fact_orders",
        mismatch_count,
        (
            "Order city/state matches customer master."
            if mismatch_count == 0
            else f"{mismatch_count} orders have customer location mismatches."
        ),
    )


# ============================================================
# SUMMARY AND MAIN PIPELINE
# ============================================================

def create_summary(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        passed = failed = warnings = 0
    else:
        passed = int(results["Status"].eq("PASS").sum())
        failed = int(results["Status"].eq("FAIL").sum())
        warnings = int(results["Status"].eq("WARNING").sum())

    total = len(results)
    overall = "FAIL" if failed else ("WARNING" if warnings else "PASS")

    return pd.DataFrame(
        [{
            "TotalChecks": total,
            "Passed": passed,
            "Failed": failed,
            "Warnings": warnings,
            "OverallStatus": overall,
        }]
    )


def validate_all_data() -> Dict[str, pd.DataFrame]:
    """Run all QuickCart data checks and save CSV reports."""
    global VALIDATION_RESULTS
    VALIDATION_RESULTS = []

    print("\n" + "=" * 80)
    print(" QUICKCART DATA VALIDATION")
    print("=" * 80)

    LOGGER.info("Starting QuickCart data validation.")

    print("\n[1/8] Loading processed datasets...")
    datasets = load_all_datasets()

    for name, dataframe in datasets.items():
        print(f"  {name:<22} {len(dataframe):>12,} rows")

    print("\n[2/8] Validating required columns...")
    validate_required_columns(datasets)

    print("\n[3/8] Validating primary keys and missing values...")
    validate_primary_keys(datasets)
    validate_missing_values(datasets)

    print("\n[4/8] Validating foreign-key relationships...")
    validate_all_foreign_keys(datasets)

    print("\n[5/8] Validating business rules...")
    validate_numeric_fields(datasets)
    validate_product_margin(datasets["dim_products"])
    validate_order_item_calculations(datasets["fact_order_items"])
    validate_order_status(datasets["fact_orders"])
    validate_returns(datasets["fact_orders"], datasets["fact_returns"])
    validate_payments(datasets["fact_orders"], datasets["fact_payments"])
    validate_deliveries(datasets["fact_orders"], datasets["fact_deliveries"])
    validate_inventory(datasets["fact_inventory"])

    print("\n[6/8] Validating dates and dataset coverage...")
    validate_dates(datasets)
    validate_dataset_sizes(datasets)
    validate_order_item_coverage(
        datasets["fact_orders"], datasets["fact_order_items"]
    )
    validate_customer_order_coverage(
        datasets["dim_customers"], datasets["fact_orders"]
    )
    validate_location_consistency(
        datasets["dim_customers"], datasets["fact_orders"]
    )

    print("\n[7/8] Creating reports...")
    results = pd.DataFrame(
        VALIDATION_RESULTS,
        columns=[
            "CheckName", "Dataset", "Status", "AffectedRows", "Message",
        ],
    )
    summary = create_summary(results)

    report_path = PROCESSED_DIR / "validation_report.csv"
    summary_path = PROCESSED_DIR / "validation_summary.csv"

    results.to_csv(report_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    print("\n[8/8] Validation results")
    print("-" * 80)
    print(results.to_string(index=False))
    print("\nVALIDATION SUMMARY")
    print(summary.to_string(index=False))
    print("-" * 80)
    print(f"Report : {report_path}")
    print(f"Summary: {summary_path}")

    overall = summary.iloc[0]["OverallStatus"]
    if overall == "PASS":
        print("\nQUICKCART DATA VALIDATION PASSED")
    elif overall == "WARNING":
        print("\nVALIDATION COMPLETED WITH WARNINGS - REVIEW THE REPORT")
    else:
        print("\nVALIDATION FAILED - FIX THE REPORTED ISSUES")

    LOGGER.info("QuickCart data validation completed with status: %s", overall)

    return {
        "results": results,
        "summary": summary,
        "datasets": datasets,
    }


# Backward-compatible function names
validate_data = validate_all_data
run = validate_all_data


if __name__ == "__main__":
    try:
        validate_all_data()
    except Exception:
        LOGGER.exception("Data validation failed.")
        raise
