# powerbi_setup.py

import os
import mysql.connector
import pandas as pd

# ============================================================
# QUICKCART - POWER BI SETUP
# ============================================================

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "harsh"
DB_NAME = "quickcart_ecommerce"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "powerbi"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# DATABASE
# ============================================================

def get_connection():

    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def save_csv(df, filename):

    path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    df.to_csv(
        path,
        index=False
    )

    print(
        f"Saved: {filename} -> {len(df):,} rows"
    )


# ============================================================
# DIM CUSTOMER
# ============================================================

def export_customers(conn):

    query = """
    SELECT
        CustomerID,
        Name,
        Gender,
        Age,
        City,
        State,
        SignupDate,
        CustomerSegment
    FROM dim_customers
    """

    df = pd.read_sql(query, conn)

    save_csv(
        df,
        "dim_customers.csv"
    )


# ============================================================
# DIM PRODUCT
# ============================================================

def export_products(conn):

    query = """
    SELECT
        ProductID,
        ProductName,
        Category,
        SubCategory,
        Brand,
        UnitPrice,
        CostPrice,
        Margin,
        StockQuantity,
        Supplier
    FROM dim_products
    """

    df = pd.read_sql(query, conn)

    save_csv(
        df,
        "dim_products.csv"
    )


# ============================================================
# DIM LOCATION
# ============================================================

def export_location(conn):

    query = """
    SELECT
        LocationID,
        City,
        State,
        Region,
        Tier
    FROM dim_location
    """

    df = pd.read_sql(query, conn)

    save_csv(
        df,
        "dim_location.csv"
    )


# ============================================================
# DIM DATE
# ============================================================

def export_date(conn):

    query = """
    SELECT
        DateKey,
        Date,
        Year,
        Quarter,
        MonthNumber,
        MonthName,
        MonthShort,
        WeekNumber,
        DayOfMonth,
        DayName,
        DayOfWeek,
        IsWeekend
    FROM dim_date
    """

    df = pd.read_sql(query, conn)

    save_csv(
        df,
        "dim_date.csv"
    )


# ============================================================
# FACT ORDERS
# ============================================================

def export_orders(conn):

    query = """
    SELECT
        OrderID,
        CustomerID,
        OrderDate,
        City,
        State,
        PaymentMethod,
        OrderStatus,
        DeliveryTime,
        ReturnStatus,
        CancellationStatus
    FROM fact_orders
    """

    df = pd.read_sql(query, conn)

    save_csv(
        df,
        "fact_orders.csv"
    )


# ============================================================
# FACT ORDER ITEMS
# ============================================================

def export_order_items(conn):

    query = """
    SELECT
        OrderItemID,
        OrderID,
        ProductID,
        Quantity,
        UnitPrice,
        Discount,
        DiscountPercent,
        Tax,
        TaxRate,
        Revenue,
        NetRevenue,
        CostAmount
    FROM fact_order_items
    """

    df = pd.read_sql(query, conn)

    save_csv(
        df,
        "fact_order_items.csv"
    )


# ============================================================
# FACT PAYMENTS
# ============================================================

def export_payments(conn):

    query = """
    SELECT
        PaymentID,
        OrderID,
        PaymentDate,
        PaymentMethod,
        Amount,
        PaymentStatus,
        TransactionID
    FROM fact_payments
    """

    df = pd.read_sql(query, conn)

    save_csv(
        df,
        "fact_payments.csv"
    )


# ============================================================
# FACT RETURNS
# ============================================================

def export_returns(conn):

    query = """
    SELECT
        ReturnID,
        OrderID,
        ReturnDate,
        ReturnReason,
        RefundAmount,
        ReturnStatus
    FROM fact_returns
    """

    df = pd.read_sql(query, conn)

    save_csv(
        df,
        "fact_returns.csv"
    )


# ============================================================
# FACT DELIVERIES
# ============================================================

def export_deliveries(conn):

    query = """
    SELECT
        DeliveryID,
        OrderID,
        DeliveryPartner,
        DeliveryStatus,
        DeliveryTimeMinutes,
        TargetDeliveryMinutes,
        DeliveredAt
    FROM fact_deliveries
    """

    df = pd.read_sql(query, conn)

    save_csv(
        df,
        "fact_deliveries.csv"
    )


# ============================================================
# FACT INVENTORY
# ============================================================

def export_inventory(conn):

    query = """
    SELECT
        InventoryID,
        SnapshotDate,
        ProductID,
        OpeningStock,
        ReceivedQuantity,
        SoldQuantity,
        ClosingStock,
        UnitCost,
        InventoryValue,
        InventoryStatus
    FROM fact_inventory
    """

    df = pd.read_sql(query, conn)

    save_csv(
        df,
        "fact_inventory.csv"
    )


# ============================================================
# POWER BI KPI DATASET
# ============================================================

def export_kpi_dataset(conn):

    query = """
    SELECT

        COUNT(DISTINCT o.OrderID)
            AS TotalOrders,

        COUNT(DISTINCT o.CustomerID)
            AS TotalCustomers,

        SUM(oi.Quantity)
            AS TotalUnits,

        ROUND(
            SUM(oi.Revenue),
            2
        ) AS TotalRevenue,

        ROUND(
            SUM(oi.NetRevenue),
            2
        ) AS NetRevenue,

        ROUND(
            SUM(oi.CostAmount),
            2
        ) AS TotalCost,

        ROUND(
            SUM(oi.NetRevenue - oi.CostAmount),
            2
        ) AS GrossProfit,

        ROUND(
            SUM(oi.NetRevenue)
            /
            NULLIF(
                COUNT(DISTINCT o.OrderID),
                0
            ),
            2
        ) AS AOV,

        ROUND(
            AVG(oi.DiscountPercent),
            2
        ) AS AverageDiscount

    FROM fact_orders o

    INNER JOIN fact_order_items oi
        ON o.OrderID = oi.OrderID
    """

    df = pd.read_sql(query, conn)

    df["GrossMarginPercent"] = (
        df["GrossProfit"]
        /
        df["NetRevenue"]
        * 100
    )

    save_csv(
        df,
        "powerbi_kpi_summary.csv"
    )


# ============================================================
# DAX MEASURES
# ============================================================

def create_dax_file():

    dax = r"""
QUICKCART POWER BI - DAX MEASURES
=================================

-- SALES KPIs

Total Revenue =
SUM(fact_order_items[Revenue])


Net Revenue =
SUM(fact_order_items[NetRevenue])


Total Cost =
SUM(fact_order_items[CostAmount])


Gross Profit =
[Net Revenue] - [Total Cost]


Gross Margin % =
DIVIDE(
    [Gross Profit],
    [Net Revenue],
    0
)


-- ORDER KPIs

Total Orders =
DISTINCTCOUNT(fact_orders[OrderID])


Total Customers =
DISTINCTCOUNT(fact_orders[CustomerID])


Total Units =
SUM(fact_order_items[Quantity])


Average Order Value =
DIVIDE(
    [Net Revenue],
    [Total Orders],
    0
)


Average Basket Size =
DIVIDE(
    [Total Units],
    [Total Orders],
    0
)


-- CUSTOMER KPIs

Average Customer Revenue =
DIVIDE(
    [Net Revenue],
    [Total Customers],
    0
)


-- DISCOUNT

Average Discount % =
AVERAGE(
    fact_order_items[DiscountPercent]
)


Total Discount =
SUM(
    fact_order_items[Discount]
)


-- RETURNS

Returned Orders =
CALCULATE(
    [Total Orders],
    fact_orders[ReturnStatus] = "Returned"
)


Return Rate % =
DIVIDE(
    [Returned Orders],
    [Total Orders],
    0
)


-- CANCELLATIONS

Cancelled Orders =
CALCULATE(
    [Total Orders],
    fact_orders[OrderStatus] = "Cancelled"
)


Cancellation Rate % =
DIVIDE(
    [Cancelled Orders],
    [Total Orders],
    0
)


-- DELIVERY

Average Delivery Time =
AVERAGE(
    fact_deliveries[DeliveryTimeMinutes]
)


On Time Deliveries =
CALCULATE(
    COUNTROWS(fact_deliveries),
    fact_deliveries[DeliveryTimeMinutes]
        <= fact_deliveries[TargetDeliveryMinutes]
)


Total Deliveries =
COUNTROWS(fact_deliveries)


On Time Delivery % =
DIVIDE(
    [On Time Deliveries],
    [Total Deliveries],
    0
)


Late Deliveries =
CALCULATE(
    COUNTROWS(fact_deliveries),
    fact_deliveries[DeliveryTimeMinutes]
        >
        fact_deliveries[TargetDeliveryMinutes]
)


Late Delivery % =
DIVIDE(
    [Late Deliveries],
    [Total Deliveries],
    0
)


-- INVENTORY

Inventory Value =
SUM(
    fact_inventory[InventoryValue]
)


Low Stock Products =
CALCULATE(
    DISTINCTCOUNT(fact_inventory[ProductID]),
    fact_inventory[InventoryStatus] = "Low Stock"
)


Stock Out Products =
CALCULATE(
    DISTINCTCOUNT(fact_inventory[ProductID]),
    fact_inventory[InventoryStatus] = "Out of Stock"
)


-- TIME INTELLIGENCE

Previous Month Revenue =
CALCULATE(
    [Net Revenue],
    DATEADD(
        dim_date[Date],
        -1,
        MONTH
    )
)


MoM Revenue Growth % =
DIVIDE(
    [Net Revenue]
        - [Previous Month Revenue],
    [Previous Month Revenue],
    0
)


Previous Year Revenue =
CALCULATE(
    [Net Revenue],
    DATEADD(
        dim_date[Date],
        -1,
        YEAR
    )
)


YoY Revenue Growth % =
DIVIDE(
    [Net Revenue]
        - [Previous Year Revenue],
    [Previous Year Revenue],
    0
)


Previous Year Orders =
CALCULATE(
    [Total Orders],
    DATEADD(
        dim_date[Date],
        -1,
        YEAR
    )
)


Order Growth % =
DIVIDE(
    [Total Orders]
        - [Previous Year Orders],
    [Previous Year Orders],
    0
)


-- PAYMENT

Successful Payments =
CALCULATE(
    COUNTROWS(fact_payments),
    fact_payments[PaymentStatus] = "Success"
)


Payment Success Rate % =
DIVIDE(
    [Successful Payments],
    COUNTROWS(fact_payments),
    0
)


-- PRODUCT

Average Selling Price =
DIVIDE(
    [Net Revenue],
    [Total Units],
    0
)


-- CUSTOMER SEGMENTS

Champions Customers =
CALCULATE(
    [Total Customers],
    dim_customers[CustomerSegment] = "Champions"
)


Loyal Customers =
CALCULATE(
    [Total Customers],
    dim_customers[CustomerSegment] = "Loyal Customers"
)


Potential Loyalists =
CALCULATE(
    [Total Customers],
    dim_customers[CustomerSegment] = "Potential Loyalists"
)


At Risk Customers =
CALCULATE(
    [Total Customers],
    dim_customers[CustomerSegment] = "At Risk"
)


Lost Customers =
CALCULATE(
    [Total Customers],
    dim_customers[CustomerSegment] = "Lost Customers"
)
"""

    path = os.path.join(
        OUTPUT_DIR,
        "DAX_Measures.txt"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(dax)

    print(
        f"Saved: DAX_Measures.txt"
    )


# ============================================================
# POWER BI MODEL GUIDE
# ============================================================

def create_model_guide():

    guide = """
QUICKCART POWER BI DATA MODEL
=============================

DIMENSIONS
----------

dim_customers
    CustomerID -> fact_orders.CustomerID

dim_products
    ProductID -> fact_order_items.ProductID

dim_date
    Date -> fact_orders.OrderDate

dim_location
    City / State -> fact_orders.City / State


FACT TABLES
-----------

fact_orders
fact_order_items
fact_payments
fact_returns
fact_deliveries
fact_inventory


RECOMMENDED CORE MODEL
----------------------

dim_customers
       |
       | CustomerID
       v
fact_orders
       |
       | OrderID
       v
fact_order_items
       |
       | ProductID
       v
dim_products


DATE
----

dim_date[Date]
       |
       v
fact_orders[OrderDate]


PAYMENTS
--------

fact_orders[OrderID]
       |
       v
fact_payments[OrderID]


RETURNS
-------

fact_orders[OrderID]
       |
       v
fact_returns[OrderID]


DELIVERIES
----------

fact_orders[OrderID]
       |
       v
fact_deliveries[OrderID]


INVENTORY
---------

dim_products[ProductID]
       |
       v
fact_inventory[ProductID]


POWER BI PAGES
--------------

1. Executive Overview

2. Sales Analysis

3. Product Analysis

4. Customer Intelligence

5. Regional Analysis

6. Operations

7. Inventory

8. Payments & Discounts


EXECUTIVE OVERVIEW KPIs
-----------------------

Total Revenue
Net Revenue
Total Orders
Total Customers
Total Units
AOV
Gross Profit
Gross Margin %
Return Rate %
Cancellation Rate %


SALES PAGE
----------

Monthly Revenue
Monthly Orders
Revenue by Category
Revenue by State
Revenue by City
Revenue Trend


PRODUCT PAGE
------------

Top Products
Category Performance
Brand Performance
Units Sold
Gross Profit
Gross Margin %


CUSTOMER PAGE
------------

Customer Segments
Customer Revenue
Orders per Customer
Top Customers
Customer Distribution


REGIONAL PAGE
-------------

State Revenue
City Revenue
Orders by State
Customers by State


OPERATIONS PAGE
---------------

Average Delivery Time
On-Time %
Late %
Delivery Partner Performance
Return Rate
Cancellation Rate


INVENTORY PAGE
--------------

Inventory Value
Low Stock Products
Stock-Out Products
Closing Stock
Inventory Status


PAYMENT PAGE
------------

Payment Method
Payment Amount
Payment Success Rate
Discount %
Return Refund Amount
"""


    path = os.path.join(
        OUTPUT_DIR,
        "PowerBI_Model_Guide.txt"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(guide)

    print(
        "Saved: PowerBI_Model_Guide.txt"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("QUICKCART - POWER BI SETUP")
    print("=" * 70)

    print(
        f"Output: {OUTPUT_DIR}"
    )

    conn = None

    try:

        print("\nConnecting to MySQL...")

        conn = get_connection()

        print(
            "MySQL connection successful."
        )

        print("\nExporting Power BI tables...")

        export_customers(conn)
        export_products(conn)
        export_location(conn)
        export_date(conn)
        export_orders(conn)
        export_order_items(conn)
        export_payments(conn)
        export_returns(conn)
        export_deliveries(conn)
        export_inventory(conn)

        print("\nCreating KPI dataset...")

        export_kpi_dataset(conn)

        print("\nCreating DAX file...")

        create_dax_file()

        print("\nCreating Power BI model guide...")

        create_model_guide()

        print("\n" + "=" * 70)
        print("POWER BI SETUP FILES CREATED SUCCESSFULLY")
        print("=" * 70)

        print(
            f"\nFolder:\n{OUTPUT_DIR}"
        )

    except Exception as e:

        print("\n" + "=" * 70)
        print("POWER BI SETUP ERROR")
        print("=" * 70)

        print(
            type(e).__name__,
            ":",
            str(e)
        )

        raise

    finally:

        if conn is not None and conn.is_connected():

            conn.close()

            print(
                "\nMySQL connection closed."
            )


if __name__ == "__main__":
    main()