"""
QUICKCART - Data Validation Module

Validates cleaned QuickCart datasets for:

- File availability
- Required columns
- Primary-key uniqueness
- Duplicate records
- Missing values
- Foreign-key integrity
- Numeric business rules
- Revenue calculations
- Customer/order relationships
- Product/order-item relationships
- Payment/order relationships
- Return/order relationships
- Delivery/order relationships
- Inventory/product relationships
- Date consistency

Outputs:
    data/processed/validation_report.csv
    data/processed/validation_summary.csv
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

import config


# ============================================================
# LOGGING
# ============================================================

LOGGER = logging.getLogger("QuickCart.DataValidation")

if not LOGGER.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


# ============================================================
# PATHS
# ============================================================

PROCESSED_DIR = Path(
    config.PROCESSED_DATA_DIR
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# VALIDATION RESULT STORAGE
# ============================================================

VALIDATION_RESULTS: List[dict] = []


def add_result(
    check_name: str,
    dataset: str,
    status: str,
    message: str,
    affected_rows: int = 0,
) -> None:
    """Store one validation result."""

    VALIDATION_RESULTS.append(
        {
            "CheckName": check_name,
            "Dataset": dataset,
            "Status": status,
            "AffectedRows": int(
                affected_rows
            ),
            "Message": message,
        }
    )


# ============================================================
# FILE LOADING
# ============================================================

def load_processed(
    filename: str,
) -> pd.DataFrame:
    """Load a processed CSV dataset."""

    path = PROCESSED_DIR / filename

    if not path.exists():

        raise FileNotFoundError(
            f"Processed file not found: {path}"
        )

    return pd.read_csv(
        path,
        low_memory=False,
    )


def load_all_datasets() -> Dict[str, pd.DataFrame]:
    """Load all processed QuickCart datasets."""

    datasets = {
        "dim_location": load_processed(
            "dim_location.csv"
        ),
        "dim_customers": load_processed(
            "dim_customers.csv"
        ),
        "dim_products": load_processed(
            "dim_products.csv"
        ),
        "dim_date": load_processed(
            "dim_date.csv"
        ),
        "fact_orders": load_processed(
            "fact_orders.csv"
        ),
        "fact_order_items": load_processed(
            "fact_order_items.csv"
        ),
        "fact_payments": load_processed(
            "fact_payments.csv"
        ),
        "fact_returns": load_processed(
            "fact_returns.csv"
        ),
        "fact_deliveries": load_processed(
            "fact_deliveries.csv"
        ),
        "fact_inventory": load_processed(
            "fact_inventory.csv"
        ),
    }

    return datasets


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = {
    "dim_location": [
        "LocationID",
        "City",
        "State",
        "Region",
        "Tier",
    ],
    "dim_customers": [
        "CustomerID",
        "Name",
        "Gender",
        "Age",
        "City",
        "State",
        "SignupDate",
        "CustomerSegment",
    ],
    "dim_products": [
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
    ],
    "dim_date": [
        "DateKey",
        "Date",
        "Year",
        "Quarter",
        "MonthNumber",
        "MonthName",
        "MonthShort",
        "WeekNumber",
        "DayOfMonth",
        "DayName",
        "DayOfWeek",
        "IsWeekend",
    ],
    "fact_orders": [
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
    ],
    "fact_order_items": [
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
    ],
    "fact_payments": [
        "PaymentID",
        "OrderID",
        "PaymentDate",
        "PaymentMethod",
        "Amount",
        "PaymentStatus",
        "TransactionID",
    ],
    "fact_returns": [
        "ReturnID",
        "OrderID",
        "ReturnDate",
        "ReturnReason",
        "RefundAmount",
        "ReturnStatus",
    ],
    "fact_deliveries": [
        "DeliveryID",
        "OrderID",
        "DeliveryPartner",
        "DeliveryStatus",
        "DeliveryTimeMinutes",
        "TargetDeliveryMinutes",
        "DeliveredAt",
    ],
    "fact_inventory": [
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
    ],
}


# ============================================================
# PRIMARY KEYS
# ============================================================

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
# REQUIRED COLUMN VALIDATION
# ============================================================

def validate_required_columns(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    """Check that every dataset has required columns."""

    for dataset_name, required in REQUIRED_COLUMNS.items():

        dataframe = datasets[dataset_name]

        missing_columns = [
            column
            for column in required
            if column not in dataframe.columns
        ]

        if missing_columns:

            add_result(
                "Required Columns",
                dataset_name,
                "FAIL",
                (
                    "Missing columns: "
                    + ", ".join(missing_columns)
                ),
                len(missing_columns),
            )

        else:

            add_result(
                "Required Columns",
                dataset_name,
                "PASS",
                "All required columns are present.",
                0,
            )


# ============================================================
# PRIMARY KEY VALIDATION
# ============================================================

def validate_primary_keys(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    """Check PK uniqueness and missing primary keys."""

    for dataset_name, primary_key in PRIMARY_KEYS.items():

        dataframe = datasets[dataset_name]

        if primary_key not in dataframe.columns:
            continue

        missing_count = int(
            dataframe[primary_key]
            .isna()
            .sum()
        )

        duplicate_count = int(
            dataframe[primary_key]
            .duplicated()
            .sum()
        )

        if missing_count == 0:

            add_result(
                "Primary Key Missing",
                dataset_name,
                "PASS",
                f"No missing {primary_key} values.",
                0,
            )

        else:

            add_result(
                "Primary Key Missing",
                dataset_name,
                "FAIL",
                (
                    f"{missing_count} missing "
                    f"{primary_key} values."
                ),
                missing_count,
            )

        if duplicate_count == 0:

            add_result(
                "Primary Key Duplicate",
                dataset_name,
                "PASS",
                f"{primary_key} values are unique.",
                0,
            )

        else:

            add_result(
                "Primary Key Duplicate",
                dataset_name,
                "FAIL",
                (
                    f"{duplicate_count} duplicate "
                    f"{primary_key} values."
                ),
                duplicate_count,
            )


# ============================================================
# GENERAL MISSING VALUE VALIDATION
# ============================================================

def validate_missing_values(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    """Check missing values with business-aware exceptions."""

    for dataset_name, dataframe in datasets.items():

        # ----------------------------------------------------
        # Special handling for fact_orders
        # DeliveryTime can be NULL for cancelled orders.
        # ----------------------------------------------------

        if dataset_name == "fact_orders":

            total_missing = int(
                dataframe.isna()
                .sum()
                .sum()
            )

            cancelled_orders = (
                dataframe["OrderStatus"]
                .eq("Cancelled")
            )

            allowed_delivery_missing = int(
                dataframe.loc[
                    cancelled_orders,
                    "DeliveryTime"
                ]
                .isna()
                .sum()
            )

            # Count only unexpected missing values.
            unexpected_missing = (
                total_missing
                - allowed_delivery_missing
            )

        # ----------------------------------------------------
        # Special handling for fact_deliveries
        # Cancelled deliveries can have NULL delivery fields.
        # ----------------------------------------------------

        elif dataset_name == "fact_deliveries":

            total_missing = int(
                dataframe.isna()
                .sum()
                .sum()
            )

            cancelled_deliveries = (
                dataframe["DeliveryStatus"]
                .eq("Cancelled")
            )

            cancelled_missing = (
                dataframe.loc[
                    cancelled_deliveries
                ]
                .isna()
                .sum()
                .sum()
            )

            unexpected_missing = (
                total_missing
                - int(cancelled_missing)
            )

        # ----------------------------------------------------
        # All other datasets
        # ----------------------------------------------------

        else:

            total_missing = int(
                dataframe.isna()
                .sum()
                .sum()
            )

            unexpected_missing = total_missing

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        if unexpected_missing == 0:

            add_result(
                "Missing Values",
                dataset_name,
                "PASS",
                (
                    f"No unexpected missing values. "
                    f"Total missing: {total_missing}."
                ),
                0,
            )

        else:

            add_result(
                "Missing Values",
                dataset_name,
                "WARNING",
                (
                    f"{unexpected_missing} unexpected "
                    f"missing values found. "
                    f"Total missing: {total_missing}."
                ),
                unexpected_missing,
            )


# ============================================================
# FOREIGN KEY VALIDATION
# ============================================================

def validate_foreign_key(
    child_df: pd.DataFrame,
    parent_df: pd.DataFrame,
    child_column: str,
    parent_column: str,
    relationship_name: str,
) -> None:
    """Validate a foreign-key relationship."""

    child_values = set(
        child_df[child_column]
        .dropna()
        .astype(str)
    )

    parent_values = set(
        parent_df[parent_column]
        .dropna()
        .astype(str)
    )

    invalid_mask = (
        ~child_df[child_column]
        .astype(str)
        .isin(parent_values)
    )

    invalid_count = int(
        invalid_mask.sum()
    )

    if invalid_count == 0:

        add_result(
            "Foreign Key",
            relationship_name,
            "PASS",
            (
                f"{child_column} correctly "
                f"references {parent_column}."
            ),
            0,
        )

    else:

        add_result(
            "Foreign Key",
            relationship_name,
            "FAIL",
            (
                f"{invalid_count} records have "
                f"invalid foreign-key values."
            ),
            invalid_count,
        )


def validate_all_foreign_keys(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    """Validate all QuickCart foreign-key relationships."""

    validate_foreign_key(
        datasets["fact_orders"],
        datasets["dim_customers"],
        "CustomerID",
        "CustomerID",
        "Orders -> Customers",
    )

    validate_foreign_key(
        datasets["fact_order_items"],
        datasets["fact_orders"],
        "OrderID",
        "OrderID",
        "Order Items -> Orders",
    )

    validate_foreign_key(
        datasets["fact_order_items"],
        datasets["dim_products"],
        "ProductID",
        "ProductID",
        "Order Items -> Products",
    )

    validate_foreign_key(
        datasets["fact_payments"],
        datasets["fact_orders"],
        "OrderID",
        "OrderID",
        "Payments -> Orders",
    )

    validate_foreign_key(
        datasets["fact_returns"],
        datasets["fact_orders"],
        "OrderID",
        "OrderID",
        "Returns -> Orders",
    )

    validate_foreign_key(
        datasets["fact_deliveries"],
        datasets["fact_orders"],
        "OrderID",
        "OrderID",
        "Deliveries -> Orders",
    )

    validate_foreign_key(
        datasets["fact_inventory"],
        datasets["dim_products"],
        "ProductID",
        "ProductID",
        "Inventory -> Products",
    )


# ============================================================
# NUMERIC VALIDATION
# ============================================================

def validate_non_negative(
    dataframe: pd.DataFrame,
    dataset_name: str,
    column: str,
) -> None:
    """Check that a numeric field contains no negative values."""

    if column not in dataframe.columns:
        return

    numeric_values = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    )

    invalid_count = int(
        (numeric_values < 0)
        .sum()
    )

    if invalid_count == 0:

        add_result(
            "Non-Negative Values",
            dataset_name,
            "PASS",
            f"{column} contains no negative values.",
            0,
        )

    else:

        add_result(
            "Non-Negative Values",
            dataset_name,
            "FAIL",
            (
                f"{invalid_count} negative "
                f"{column} values."
            ),
            invalid_count,
        )


def validate_numeric_fields(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    """Validate numeric business fields."""

    product_df = datasets["dim_products"]
    item_df = datasets["fact_order_items"]
    payment_df = datasets["fact_payments"]
    inventory_df = datasets["fact_inventory"]
    delivery_df = datasets["fact_deliveries"]

    product_fields = [
        "UnitPrice",
        "CostPrice",
        "Margin",
        "StockQuantity",
    ]

    item_fields = [
        "Quantity",
        "UnitPrice",
        "Discount",
        "Tax",
        "Revenue",
        "NetRevenue",
        "CostAmount",
    ]

    payment_fields = [
        "Amount",
    ]

    inventory_fields = [
        "OpeningStock",
        "ReceivedQuantity",
        "SoldQuantity",
        "ClosingStock",
        "UnitCost",
        "InventoryValue",
    ]

    delivery_fields = [
        "DeliveryTimeMinutes",
        "TargetDeliveryMinutes",
    ]

    for field in product_fields:
        validate_non_negative(
            product_df,
            "dim_products",
            field,
        )

    for field in item_fields:
        validate_non_negative(
            item_df,
            "fact_order_items",
            field,
        )

    for field in payment_fields:
        validate_non_negative(
            payment_df,
            "fact_payments",
            field,
        )

    for field in inventory_fields:
        validate_non_negative(
            inventory_df,
            "fact_inventory",
            field,
        )

    for field in delivery_fields:
        validate_non_negative(
            delivery_df,
            "fact_deliveries",
            field,
        )


# ============================================================
# PRODUCT MARGIN VALIDATION
# ============================================================

def validate_product_margin(
    products: pd.DataFrame,
) -> None:
    """Check UnitPrice, CostPrice and Margin relationship."""

    calculated_margin = (
        products["UnitPrice"]
        - products["CostPrice"]
    ).round(2)

    actual_margin = (
        products["Margin"]
        .round(2)
    )

    invalid_count = int(
        (
            calculated_margin
            != actual_margin
        ).sum()
    )

    if invalid_count == 0:

        add_result(
            "Product Margin",
            "dim_products",
            "PASS",
            (
                "Margin equals "
                "UnitPrice - CostPrice."
            ),
            0,
        )

    else:

        add_result(
            "Product Margin",
            "dim_products",
            "FAIL",
            (
                f"{invalid_count} products "
                f"have incorrect margin."
            ),
            invalid_count,
        )


# ============================================================
# ORDER ITEM CALCULATION VALIDATION
# ============================================================

def validate_order_item_calculations(
    order_items: pd.DataFrame,
) -> None:
    """Validate revenue and net revenue calculations."""

    expected_revenue = (
        order_items["Quantity"]
        * order_items["UnitPrice"]
    ).round(2)

    actual_revenue = (
        order_items["Revenue"]
        .round(2)
    )

    revenue_difference = (
        expected_revenue
        - actual_revenue
    ).abs()

    invalid_revenue = int(
        (
            revenue_difference
            > 0.05
        ).sum()
    )

    if invalid_revenue == 0:

        add_result(
            "Revenue Calculation",
            "fact_order_items",
            "PASS",
            (
                "Revenue matches "
                "Quantity × UnitPrice."
            ),
            0,
        )

    else:

        add_result(
            "Revenue Calculation",
            "fact_order_items",
            "FAIL",
            (
                f"{invalid_revenue} rows have "
                f"incorrect Revenue."
            ),
            invalid_revenue,
        )

    expected_net_revenue = (
        order_items["Revenue"]
        - order_items["Discount"]
        + order_items["Tax"]
    ).round(2)

    actual_net_revenue = (
        order_items["NetRevenue"]
        .round(2)
    )

    net_difference = (
        expected_net_revenue
        - actual_net_revenue
    ).abs()

    invalid_net = int(
        (
            net_difference
            > 0.05
        ).sum()
    )

    if invalid_net == 0:

        add_result(
            "Net Revenue Calculation",
            "fact_order_items",
            "PASS",
            (
                "NetRevenue matches "
                "Revenue - Discount + Tax."
            ),
            0,
        )

    else:

        add_result(
            "Net Revenue Calculation",
            "fact_order_items",
            "FAIL",
            (
                f"{invalid_net} rows have "
                f"incorrect NetRevenue."
            ),
            invalid_net,
        )


# ============================================================
# ORDER STATUS VALIDATION
# ============================================================

def validate_order_status(
    orders: pd.DataFrame,
) -> None:
    """Validate order status combinations."""

    valid_statuses = {
        "Delivered",
        "Cancelled",
        "Returned",
    }

    invalid_status_count = int(
        (
            ~orders["OrderStatus"]
            .isin(valid_statuses)
        ).sum()
    )

    if invalid_status_count == 0:

        add_result(
            "Order Status",
            "fact_orders",
            "PASS",
            "All order statuses are valid.",
            0,
        )

    else:

        add_result(
            "Order Status",
            "fact_orders",
            "FAIL",
            (
                f"{invalid_status_count} "
                f"invalid order statuses."
            ),
            invalid_status_count,
        )

    # Cancelled orders should be marked cancelled.
    cancelled_mismatch = int(
        (
            (
                orders["OrderStatus"]
                == "Cancelled"
            )
            & (
                orders["CancellationStatus"]
                != "Cancelled"
            )
        ).sum()
    )

    if cancelled_mismatch == 0:

        add_result(
            "Cancellation Status",
            "fact_orders",
            "PASS",
            (
                "Cancelled orders have "
                "correct cancellation status."
            ),
            0,
        )

    else:

        add_result(
            "Cancellation Status",
            "fact_orders",
            "FAIL",
            (
                f"{cancelled_mismatch} cancelled "
                f"orders have incorrect status."
            ),
            cancelled_mismatch,
        )

    # Returned orders should have return status.
    return_mismatch = int(
        (
            (
                orders["OrderStatus"]
                == "Returned"
            )
            & (
                orders["ReturnStatus"]
                != "Returned"
            )
        ).sum()
    )

    if return_mismatch == 0:

        add_result(
            "Return Status",
            "fact_orders",
            "PASS",
            (
                "Returned orders have "
                "correct return status."
            ),
            0,
        )

    else:

        add_result(
            "Return Status",
            "fact_orders",
            "FAIL",
            (
                f"{return_mismatch} returned "
                f"orders have incorrect status."
            ),
            return_mismatch,
        )


# ============================================================
# RETURN VALIDATION
# ============================================================

def validate_returns(
    orders: pd.DataFrame,
    returns: pd.DataFrame,
) -> None:
    """Validate return records against order status."""

    if returns.empty:

        add_result(
            "Return Records",
            "fact_returns",
            "WARNING",
            "No return records found.",
            0,
        )

        return

    order_status_lookup = (
        orders.set_index("OrderID")
        ["OrderStatus"]
        .to_dict()
    )

    invalid_returns = 0

    for order_id in returns["OrderID"]:

        if order_status_lookup.get(
            order_id
        ) != "Returned":

            invalid_returns += 1

    if invalid_returns == 0:

        add_result(
            "Return Order Status",
            "fact_returns",
            "PASS",
            (
                "All return records belong "
                "to Returned orders."
            ),
            0,
        )

    else:

        add_result(
            "Return Order Status",
            "fact_returns",
            "FAIL",
            (
                f"{invalid_returns} return records "
                f"belong to non-returned orders."
            ),
            invalid_returns,
        )


# ============================================================
# PAYMENT VALIDATION
# ============================================================

def validate_payments(
    orders: pd.DataFrame,
    payments: pd.DataFrame,
) -> None:
    """Validate payment coverage."""

    order_count = (
        orders["OrderID"]
        .nunique()
    )

    payment_order_count = (
        payments["OrderID"]
        .nunique()
    )

    duplicate_payment_orders = int(
        payments["OrderID"]
        .duplicated()
        .sum()
    )

    if payment_order_count == order_count:

        add_result(
            "Payment Coverage",
            "fact_payments",
            "PASS",
            (
                f"All {order_count:,} orders "
                f"have payment records."
            ),
            0,
        )

    else:

        difference = abs(
            order_count
            - payment_order_count
        )

        add_result(
            "Payment Coverage",
            "fact_payments",
            "WARNING",
            (
                f"Payment coverage differs "
                f"from order count by "
                f"{difference:,}."
            ),
            difference,
        )

    if duplicate_payment_orders == 0:

        add_result(
            "Payment Per Order",
            "fact_payments",
            "PASS",
            (
                "No order has multiple "
                "payment records."
            ),
            0,
        )

    else:

        add_result(
            "Payment Per Order",
            "fact_payments",
            "WARNING",
            (
                f"{duplicate_payment_orders} "
                f"duplicate payment-order links."
            ),
            duplicate_payment_orders,
        )


# ============================================================
# DELIVERY VALIDATION
# ============================================================

def validate_deliveries(
    orders: pd.DataFrame,
    deliveries: pd.DataFrame,
) -> None:
    """Validate delivery business rules."""

    cancelled_order_ids = set(
        orders.loc[
            orders["OrderStatus"]
            == "Cancelled",
            "OrderID",
        ]
    )

    delivery_cancelled_ids = set(
        deliveries.loc[
            deliveries["DeliveryStatus"]
            == "Cancelled",
            "OrderID",
        ]
    )

    missing_delivery_cancelled = (
        cancelled_order_ids
        - delivery_cancelled_ids
    )

    if not missing_delivery_cancelled:

        add_result(
            "Cancelled Delivery Mapping",
            "fact_deliveries",
            "PASS",
            (
                "Cancelled orders are correctly "
                "marked in delivery records."
            ),
            0,
        )

    else:

        add_result(
            "Cancelled Delivery Mapping",
            "fact_deliveries",
            "WARNING",
            (
                f"{len(missing_delivery_cancelled)} "
                f"cancelled orders need delivery review."
            ),
            len(missing_delivery_cancelled),
        )

    # Delivered records should have a delivery time.
    delivered_mask = (
        deliveries["DeliveryStatus"]
        != "Cancelled"
    )

    missing_delivery_time = int(
        deliveries.loc[
            delivered_mask,
            "DeliveryTimeMinutes",
        ]
        .isna()
        .sum()
    )

    if missing_delivery_time == 0:

        add_result(
            "Delivery Time",
            "fact_deliveries",
            "PASS",
            (
                "Active deliveries have "
                "delivery times."
            ),
            0,
        )

    else:

        add_result(
            "Delivery Time",
            "fact_deliveries",
            "FAIL",
            (
                f"{missing_delivery_time} active "
                f"deliveries have missing time."
            ),
            missing_delivery_time,
        )


# ============================================================
# INVENTORY VALIDATION
# ============================================================

def validate_inventory(
    inventory: pd.DataFrame,
) -> None:
    """Validate inventory arithmetic."""

    expected_closing = (
        inventory["OpeningStock"]
        + inventory["ReceivedQuantity"]
        - inventory["SoldQuantity"]
    ).clip(lower=0)

    actual_closing = (
        inventory["ClosingStock"]
    )

    differences = (
        expected_closing
        - actual_closing
    ).abs()

    invalid_count = int(
        (
            differences
            > 0.01
        ).sum()
    )

    if invalid_count == 0:

        add_result(
            "Inventory Calculation",
            "fact_inventory",
            "PASS",
            (
                "ClosingStock follows "
                "Opening + Received - Sold."
            ),
            0,
        )

    else:

        add_result(
            "Inventory Calculation",
            "fact_inventory",
            "WARNING",
            (
                f"{invalid_count} inventory "
                f"records require review."
            ),
            invalid_count,
        )

    expected_value = (
        inventory["ClosingStock"]
        * inventory["UnitCost"]
    ).round(2)

    actual_value = (
        inventory["InventoryValue"]
        .round(2)
    )

    value_difference = (
        expected_value
        - actual_value
    ).abs()

    invalid_value = int(
        (
            value_difference
            > 0.05
        ).sum()
    )

    if invalid_value == 0:

        add_result(
            "Inventory Value",
            "fact_inventory",
            "PASS",
            (
                "InventoryValue matches "
                "ClosingStock × UnitCost."
            ),
            0,
        )

    else:

        add_result(
            "Inventory Value",
            "fact_inventory",
            "FAIL",
            (
                f"{invalid_value} inventory "
                f"values are incorrect."
            ),
            invalid_value,
        )


# ============================================================
# DATE VALIDATION
# ============================================================

def validate_dates(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    """Validate transaction dates."""

    start_date = pd.Timestamp(
        config.DATA_START_DATE
    )

    end_date = pd.Timestamp(
        config.DATA_END_DATE
    )

    orders = datasets[
        "fact_orders"
    ].copy()

    orders["OrderDate"] = pd.to_datetime(
        orders["OrderDate"],
        errors="coerce",
    )

    invalid_order_dates = int(
        (
            (orders["OrderDate"] < start_date)
            | (orders["OrderDate"] > end_date)
        ).sum()
    )

    if invalid_order_dates == 0:

        add_result(
            "Order Date Range",
            "fact_orders",
            "PASS",
            (
                "All order dates are within "
                "the configured business period."
            ),
            0,
        )

    else:

        add_result(
            "Order Date Range",
            "fact_orders",
            "FAIL",
            (
                f"{invalid_order_dates} orders "
                f"have dates outside the period."
            ),
            invalid_order_dates,
        )

    customers = datasets[
        "dim_customers"
    ].copy()

    customers["SignupDate"] = pd.to_datetime(
        customers["SignupDate"],
        errors="coerce",
    )

    customer_signup = (
        customers.set_index("CustomerID")
        ["SignupDate"]
        .to_dict()
    )

    invalid_signup_orders = 0

    for _, row in orders[
        ["CustomerID", "OrderDate"]
    ].iterrows():

        signup_date = customer_signup.get(
            row["CustomerID"]
        )

        if (
            signup_date is not None
            and row["OrderDate"] < signup_date
        ):
            invalid_signup_orders += 1

    if invalid_signup_orders == 0:

        add_result(
            "Signup Before Order",
            "fact_orders",
            "PASS",
            (
                "Customers do not place orders "
                "before signup."
            ),
            0,
        )

    else:

        add_result(
            "Signup Before Order",
            "fact_orders",
            "WARNING",
            (
                f"{invalid_signup_orders} orders "
                f"occur before customer signup."
            ),
            invalid_signup_orders,
        )


# ============================================================
# DATASET SIZE VALIDATION
# ============================================================

def validate_dataset_sizes(
    datasets: Dict[str, pd.DataFrame],
) -> None:
    """Validate project minimum dataset requirements."""

    requirements = {
        "dim_customers": (
            config.CUSTOMER_COUNT
        ),
        "dim_products": (
            config.PRODUCT_COUNT
        ),
        "fact_orders": (
            config.ORDER_COUNT
        ),
        "fact_order_items": (
            config.MIN_ORDER_ITEMS
        ),
        "fact_payments": (
            config.PAYMENT_COUNT
        ),
    }

    for dataset_name, minimum in requirements.items():

        actual = len(
            datasets[dataset_name]
        )

        if actual >= minimum:

            add_result(
                "Dataset Size",
                dataset_name,
                "PASS",
                (
                    f"Dataset has {actual:,} rows; "
                    f"minimum required is {minimum:,}."
                ),
                0,
            )

        else:

            difference = minimum - actual

            add_result(
                "Dataset Size",
                dataset_name,
                "FAIL",
                (
                    f"Dataset has only {actual:,} rows; "
                    f"{difference:,} additional rows required."
                ),
                difference,
            )


# ============================================================
# ORDER ITEM COVERAGE
# ============================================================

def validate_order_item_coverage(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
) -> None:
    """Ensure orders have associated items."""

    order_ids = set(
        orders["OrderID"]
    )

    item_order_ids = set(
        order_items["OrderID"]
    )

    missing_items = (
        order_ids
        - item_order_ids
    )

    if not missing_items:

        add_result(
            "Order Item Coverage",
            "fact_order_items",
            "PASS",
            (
                "Every order has at least "
                "one order-item record."
            ),
            0,
        )

    else:

        add_result(
            "Order Item Coverage",
            "fact_order_items",
            "FAIL",
            (
                f"{len(missing_items)} orders "
                f"have no order items."
            ),
            len(missing_items),
        )


# ============================================================
# CUSTOMER ORDER COVERAGE
# ============================================================

def validate_customer_order_coverage(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:
    """Check customer transaction coverage."""

    customer_ids = set(
        customers["CustomerID"]
    )

    order_customer_ids = set(
        orders["CustomerID"]
    )

    invalid_customer_ids = (
        order_customer_ids
        - customer_ids
    )

    if not invalid_customer_ids:

        add_result(
            "Customer Order Coverage",
            "fact_orders",
            "PASS",
            (
                "All orders belong to "
                "valid customers."
            ),
            0,
        )

    else:

        add_result(
            "Customer Order Coverage",
            "fact_orders",
            "FAIL",
            (
                f"{len(invalid_customer_ids)} "
                f"invalid customer IDs."
            ),
            len(invalid_customer_ids),
        )


# ============================================================
# LOCATION CONSISTENCY
# ============================================================

def validate_location_consistency(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:
    """Check that customer and order locations agree."""

    customer_location = (
        customers.set_index(
            "CustomerID"
        )[["City", "State"]]
        .to_dict(
            orient="index"
        )
    )

    mismatches = 0

    for _, row in orders[
        [
            "CustomerID",
            "City",
            "State",
        ]
    ].iterrows():

        customer_info = customer_location.get(
            row["CustomerID"]
        )

        if customer_info is None:
            continue

        if (
            str(row["City"])
            != str(customer_info["City"])
            or str(row["State"])
            != str(customer_info["State"])
        ):
            mismatches += 1

    if mismatches == 0:

        add_result(
            "Customer Location Consistency",
            "fact_orders",
            "PASS",
            (
                "Order city/state matches "
                "customer master."
            ),
            0,
        )

    else:

        add_result(
            "Customer Location Consistency",
            "fact_orders",
            "FAIL",
            (
                f"{mismatches} orders have "
                f"location mismatches."
            ),
            mismatches,
        )


# ============================================================
# SUMMARY
# ============================================================

def create_summary(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """Create overall validation summary."""

    total_checks = len(results)

    passed = int(
        (
            results["Status"]
            == "PASS"
        ).sum()
    )

    failed = int(
        (
            results["Status"]
            == "FAIL"
        ).sum()
    )

    warnings = int(
        (
            results["Status"]
            == "WARNING"
        ).sum()
    )

    summary = pd.DataFrame(
        [
            {
                "TotalChecks": total_checks,
                "Passed": passed,
                "Failed": failed,
                "Warnings": warnings,
                "OverallStatus": (
                    "PASS"
                    if failed == 0
                    else "FAIL"
                ),
            }
        ]
    )

    return summary


# ============================================================
# MAIN VALIDATION PIPELINE
# ============================================================

def validate_all_data() -> Dict[str, pd.DataFrame]:
    """Execute the complete QuickCart validation pipeline."""

    global VALIDATION_RESULTS

    VALIDATION_RESULTS = []

    print()
    print("=" * 90)
    print(" QUICKCART DATA VALIDATION")
    print("=" * 90)

    LOGGER.info(
        "Starting QuickCart data validation."
    )

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    print("\n[1/8] Loading processed datasets...")

    datasets = load_all_datasets()

    for name, dataframe in datasets.items():

        print(
            f"  {name:<22} "
            f"{len(dataframe):>10,} rows"
        )

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    print("\n[2/8] Validating required columns...")

    validate_required_columns(
        datasets
    )

    # --------------------------------------------------------
    # Primary keys
    # --------------------------------------------------------

    print("\n[3/8] Validating primary keys...")

    validate_primary_keys(
        datasets
    )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print("\n[4/8] Validating missing values...")

    validate_missing_values(
        datasets
    )

    # --------------------------------------------------------
    # Foreign keys
    # --------------------------------------------------------

    print("\n[5/8] Validating relationships...")

    validate_all_foreign_keys(
        datasets
    )

    # --------------------------------------------------------
    # Business rules
    # --------------------------------------------------------

    print("\n[6/8] Validating business calculations...")

    validate_numeric_fields(
        datasets
    )

    validate_product_margin(
        datasets["dim_products"]
    )

    validate_order_item_calculations(
        datasets["fact_order_items"]
    )

    validate_order_status(
        datasets["fact_orders"]
    )

    validate_returns(
        datasets["fact_orders"],
        datasets["fact_returns"],
    )

    validate_payments(
        datasets["fact_orders"],
        datasets["fact_payments"],
    )

    validate_deliveries(
        datasets["fact_orders"],
        datasets["fact_deliveries"],
    )

    validate_inventory(
        datasets["fact_inventory"]
    )

    # --------------------------------------------------------
    # Date validation
    # --------------------------------------------------------

    print("\n[7/8] Validating dates and coverage...")

    validate_dates(
        datasets
    )

    validate_dataset_sizes(
        datasets
    )

    validate_order_item_coverage(
        datasets["fact_orders"],
        datasets["fact_order_items"],
    )

    validate_customer_order_coverage(
        datasets["dim_customers"],
        datasets["fact_orders"],
    )

    validate_location_consistency(
        datasets["dim_customers"],
        datasets["fact_orders"],
    )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print("\n[8/8] Creating validation reports...")

    results = pd.DataFrame(
        VALIDATION_RESULTS
    )

    summary = create_summary(
        results
    )

    report_path = (
        PROCESSED_DIR
        / "validation_report.csv"
    )

    summary_path = (
        PROCESSED_DIR
        / "validation_summary.csv"
    )

    results.to_csv(
        report_path,
        index=False,
        encoding="utf-8-sig",
    )

    summary.to_csv(
        summary_path,
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # Console output
    # --------------------------------------------------------

    print()
    print("=" * 90)
    print(" VALIDATION RESULTS")
    print("=" * 90)

    print(
        results[
            [
                "CheckName",
                "Dataset",
                "Status",
                "AffectedRows",
                "Message",
            ]
        ].to_string(
            index=False
        )
    )

    print()
    print("=" * 90)
    print(" VALIDATION SUMMARY")
    print("=" * 90)

    print(
        summary.to_string(
            index=False
        )
    )

    print("=" * 90)

    failed_count = int(
        summary.iloc[0]["Failed"]
    )

    warning_count = int(
        summary.iloc[0]["Warnings"]
    )

    if failed_count == 0:

        print(
            "\n✅ QUICKCART DATA VALIDATION PASSED"
        )

        if warning_count > 0:

            print(
                f"⚠️ {warning_count} warning(s) "
                f"require review."
            )

    else:

        print(
            f"\n❌ QUICKCART VALIDATION FOUND "
            f"{failed_count} FAILURE(S)"
        )

    print()
    print(
        f"Validation report : {report_path}"
    )

    print(
        f"Validation summary: {summary_path}"
    )

    print("=" * 90)

    LOGGER.info(
        "QuickCart data validation completed."
    )

    return {
        "results": results,
        "summary": summary,
        "datasets": datasets,
    }


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

validate_data = validate_all_data
run = validate_all_data


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    try:

        validate_all_data()

    except Exception as exc:

        LOGGER.exception(
            "Data validation failed: %s",
            exc,
        )

        print()
        print("=" * 90)
        print(" DATA VALIDATION FAILED")
        print("=" * 90)
        print(
            f"Error: {exc}"
        )
        print("=" * 90)

        raise