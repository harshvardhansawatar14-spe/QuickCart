import os
import mysql.connector
import pandas as pd

# ============================================================
# QUICKCART - SQL BUSINESS ANALYSIS
# ============================================================

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "harsh"
DB_NAME = "quickcart_ecommerce"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "sql_analysis")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


# ============================================================
# QUERY HELPER
# ============================================================

def run_query(conn, query):
    return pd.read_sql(query, conn)


def save_result(df, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False)
    print(f"Saved: {filename} -> {len(df):,} rows")


# ============================================================
# SHOW DATABASE SCHEMA
# ============================================================

def show_schema(conn):

    print("\n" + "=" * 70)
    print("QUICKCART DATABASE SCHEMA")
    print("=" * 70)

    tables = [
        "dim_location",
        "dim_customers",
        "dim_products",
        "dim_date",
        "fact_orders",
        "fact_order_items",
        "fact_payments",
        "fact_returns",
        "fact_deliveries",
        "fact_inventory"
    ]

    for table in tables:

        print(f"\n{table}")

        df = run_query(
            conn,
            f"SHOW COLUMNS FROM `{table}`"
        )

        for col in df["Field"]:
            print(f"   {col}")


# ============================================================
# 1. DATABASE SUMMARY
# ============================================================

def analysis_database_summary(conn):

    query = """
    SELECT
        (SELECT COUNT(*) FROM dim_customers) AS TotalCustomers,
        (SELECT COUNT(*) FROM dim_products) AS TotalProducts,
        (SELECT COUNT(*) FROM fact_orders) AS TotalOrders,
        (SELECT COALESCE(SUM(Quantity),0)
         FROM fact_order_items) AS TotalUnits,
        (SELECT COALESCE(SUM(NetRevenue),0)
         FROM fact_order_items) AS NetRevenue,
        (SELECT COALESCE(SUM(CostAmount),0)
         FROM fact_order_items) AS TotalCost
    """

    df = run_query(conn, query)

    df["GrossProfit"] = df["NetRevenue"] - df["TotalCost"]

    df["GrossMarginPercent"] = (
        df["GrossProfit"] /
        df["NetRevenue"].replace(0, pd.NA)
    ) * 100

    save_result(df, "01_database_summary.csv")

    print("\nDATABASE SUMMARY")
    print(df.to_string(index=False))


# ============================================================
# 2. ORDER SUMMARY
# ============================================================

def analysis_order_summary(conn):

    query = """
    SELECT
        COUNT(*) AS TotalOrders,

        SUM(CASE
            WHEN OrderStatus = 'Delivered'
            THEN 1 ELSE 0
        END) AS DeliveredOrders,

        SUM(CASE
            WHEN OrderStatus = 'Cancelled'
            THEN 1 ELSE 0
        END) AS CancelledOrders,

        SUM(CASE
            WHEN OrderStatus = 'Returned'
            THEN 1 ELSE 0
        END) AS ReturnedOrders,

        SUM(CASE
            WHEN OrderStatus = 'Pending'
            THEN 1 ELSE 0
        END) AS PendingOrders

    FROM fact_orders
    """

    df = run_query(conn, query)

    df["CancellationRatePercent"] = (
        df["CancelledOrders"] /
        df["TotalOrders"]
    ) * 100

    df["ReturnRatePercent"] = (
        df["ReturnedOrders"] /
        df["TotalOrders"]
    ) * 100

    save_result(df, "02_order_summary.csv")

    print("\nORDER SUMMARY")
    print(df.to_string(index=False))


# ============================================================
# 3. CATEGORY SALES
# ============================================================

def analysis_category_sales(conn):

    query = """
    SELECT
        p.Category,

        COUNT(DISTINCT oi.OrderID) AS Orders,

        SUM(oi.Quantity) AS Units,

        ROUND(SUM(oi.Revenue), 2) AS Revenue,

        ROUND(SUM(oi.NetRevenue), 2) AS NetRevenue,

        ROUND(SUM(oi.CostAmount), 2) AS Cost,

        ROUND(
            SUM(oi.NetRevenue) - SUM(oi.CostAmount),
            2
        ) AS GrossProfit

    FROM fact_order_items oi

    INNER JOIN dim_products p
        ON oi.ProductID = p.ProductID

    GROUP BY p.Category

    ORDER BY NetRevenue DESC
    """

    df = run_query(conn, query)

    df["GrossMarginPercent"] = (
        df["GrossProfit"] /
        df["NetRevenue"].replace(0, pd.NA)
    ) * 100

    save_result(df, "03_category_sales.csv")

    print("\nCATEGORY SALES")
    print(df.to_string(index=False))


# ============================================================
# 4. TOP PRODUCTS
# ============================================================

def analysis_top_products(conn):

    query = """
    SELECT
        p.ProductID,
        p.ProductName,
        p.Category,
        p.Brand,

        SUM(oi.Quantity) AS Units,

        ROUND(SUM(oi.Revenue), 2) AS Revenue,

        ROUND(SUM(oi.NetRevenue), 2) AS NetRevenue,

        ROUND(SUM(oi.CostAmount), 2) AS Cost,

        ROUND(
            SUM(oi.NetRevenue) - SUM(oi.CostAmount),
            2
        ) AS GrossProfit

    FROM fact_order_items oi

    INNER JOIN dim_products p
        ON oi.ProductID = p.ProductID

    GROUP BY
        p.ProductID,
        p.ProductName,
        p.Category,
        p.Brand

    ORDER BY NetRevenue DESC

    LIMIT 50
    """

    df = run_query(conn, query)

    save_result(df, "04_top_50_products.csv")

    print("\nTOP 50 PRODUCTS")
    print(df.head(10).to_string(index=False))


# ============================================================
# 5. MONTHLY SALES
# ============================================================

def analysis_monthly_sales(conn):

    query = """
    SELECT
        YEAR(o.OrderDate) AS Year,
        MONTH(o.OrderDate) AS MonthNumber,
        DATE_FORMAT(o.OrderDate, '%Y-%m') AS YearMonth,

        COUNT(DISTINCT o.OrderID) AS Orders,

        SUM(oi.Quantity) AS Units,

        ROUND(SUM(oi.Revenue), 2) AS Revenue,

        ROUND(SUM(oi.NetRevenue), 2) AS NetRevenue,

        ROUND(SUM(oi.CostAmount), 2) AS Cost,

        ROUND(
            SUM(oi.NetRevenue) - SUM(oi.CostAmount),
            2
        ) AS GrossProfit

    FROM fact_orders o

    INNER JOIN fact_order_items oi
        ON o.OrderID = oi.OrderID

    GROUP BY
        YEAR(o.OrderDate),
        MONTH(o.OrderDate),
        DATE_FORMAT(o.OrderDate, '%Y-%m')

    ORDER BY Year, MonthNumber
    """

    df = run_query(conn, query)

    save_result(df, "05_monthly_sales.csv")

    print("\nMONTHLY SALES")
    print(df.to_string(index=False))


# ============================================================
# 6. CUSTOMER ANALYSIS
# ============================================================

def analysis_customer_analysis(conn):

    query = """
    SELECT
        c.CustomerID,
        c.Name,
        c.Gender,
        c.Age,
        c.City,
        c.State,
        c.CustomerSegment,

        COUNT(DISTINCT o.OrderID) AS Orders,

        COALESCE(SUM(oi.Quantity),0) AS Units,

        ROUND(
            COALESCE(SUM(oi.NetRevenue),0),
            2
        ) AS NetRevenue,

        ROUND(
            COALESCE(SUM(oi.NetRevenue),0)
            /
            NULLIF(COUNT(DISTINCT o.OrderID),0),
            2
        ) AS AOV

    FROM dim_customers c

    LEFT JOIN fact_orders o
        ON c.CustomerID = o.CustomerID

    LEFT JOIN fact_order_items oi
        ON o.OrderID = oi.OrderID

    GROUP BY
        c.CustomerID,
        c.Name,
        c.Gender,
        c.Age,
        c.City,
        c.State,
        c.CustomerSegment

    ORDER BY NetRevenue DESC
    """

    df = run_query(conn, query)

    save_result(df, "06_customer_analysis.csv")

    print("\nTOP CUSTOMERS")
    print(df.head(20).to_string(index=False))


# ============================================================
# 7. CUSTOMER SEGMENT ANALYSIS
# ============================================================

def analysis_customer_segments(conn):

    query = """
    SELECT
        c.CustomerSegment,

        COUNT(DISTINCT c.CustomerID) AS Customers,

        COUNT(DISTINCT o.OrderID) AS Orders,

        SUM(oi.Quantity) AS Units,

        ROUND(SUM(oi.NetRevenue),2) AS NetRevenue

    FROM dim_customers c

    LEFT JOIN fact_orders o
        ON c.CustomerID = o.CustomerID

    LEFT JOIN fact_order_items oi
        ON o.OrderID = oi.OrderID

    GROUP BY c.CustomerSegment

    ORDER BY NetRevenue DESC
    """

    df = run_query(conn, query)

    save_result(df, "07_customer_segments.csv")

    print("\nCUSTOMER SEGMENTS")
    print(df.to_string(index=False))


# ============================================================
# 8. PAYMENT ANALYSIS
# ============================================================

def analysis_payments(conn):

    query = """
    SELECT
        PaymentMethod,

        COUNT(*) AS Transactions,

        ROUND(SUM(Amount),2) AS PaymentAmount,

        SUM(
            CASE
                WHEN PaymentStatus = 'Success'
                THEN 1 ELSE 0
            END
        ) AS SuccessfulPayments,

        SUM(
            CASE
                WHEN PaymentStatus != 'Success'
                THEN 1 ELSE 0
            END
        ) AS FailedPayments

    FROM fact_payments

    GROUP BY PaymentMethod

    ORDER BY PaymentAmount DESC
    """

    df = run_query(conn, query)

    save_result(df, "08_payment_analysis.csv")

    print("\nPAYMENT ANALYSIS")
    print(df.to_string(index=False))


# ============================================================
# 9. RETURNS
# ============================================================

def analysis_returns(conn):

    query = """
    SELECT
        ReturnReason,

        COUNT(*) AS ReturnCount,

        ROUND(
            SUM(RefundAmount),
            2
        ) AS RefundAmount

    FROM fact_returns

    GROUP BY ReturnReason

    ORDER BY ReturnCount DESC
    """

    df = run_query(conn, query)

    save_result(df, "09_return_analysis.csv")

    print("\nRETURN ANALYSIS")
    print(df.to_string(index=False))


# ============================================================
# 10. DELIVERY
# ============================================================

def analysis_delivery(conn):

    query = """
    SELECT
        DeliveryPartner,

        COUNT(*) AS Deliveries,

        ROUND(
            AVG(DeliveryTimeMinutes),
            2
        ) AS AvgDeliveryMinutes,

        ROUND(
            AVG(TargetDeliveryMinutes),
            2
        ) AS AvgTargetMinutes,

        SUM(
            CASE
                WHEN DeliveryStatus = 'Delivered'
                THEN 1 ELSE 0
            END
        ) AS Delivered,

        SUM(
            CASE
                WHEN DeliveryStatus = 'Late'
                THEN 1 ELSE 0
        END) AS LateDeliveries

    FROM fact_deliveries

    GROUP BY DeliveryPartner

    ORDER BY AvgDeliveryMinutes
    """

    df = run_query(conn, query)

    save_result(df, "10_delivery_analysis.csv")

    print("\nDELIVERY ANALYSIS")
    print(df.to_string(index=False))


# ============================================================
# 11. INVENTORY
# ============================================================

def analysis_inventory(conn):

    query = """
    SELECT
        p.ProductID,
        p.ProductName,
        p.Category,
        p.Brand,

        i.SnapshotDate,

        i.OpeningStock,
        i.ReceivedQuantity,
        i.SoldQuantity,
        i.ClosingStock,

        i.UnitCost,
        i.InventoryValue,
        i.InventoryStatus

    FROM fact_inventory i

    INNER JOIN dim_products p
        ON i.ProductID = p.ProductID

    ORDER BY
        i.InventoryValue DESC
    """

    df = run_query(conn, query)

    save_result(df, "11_inventory_analysis.csv")

    print("\nINVENTORY ANALYSIS")
    print(df.head(20).to_string(index=False))


# ============================================================
# 12. CITY ANALYSIS
# ============================================================

def analysis_city(conn):

    query = """
    SELECT
        o.City,

        o.State,

        COUNT(DISTINCT o.OrderID) AS Orders,

        COUNT(DISTINCT o.CustomerID) AS Customers,

        SUM(oi.Quantity) AS Units,

        ROUND(SUM(oi.NetRevenue),2) AS NetRevenue

    FROM fact_orders o

    INNER JOIN fact_order_items oi
        ON o.OrderID = oi.OrderID

    GROUP BY
        o.City,
        o.State

    ORDER BY NetRevenue DESC
    """

    df = run_query(conn, query)

    save_result(df, "12_city_analysis.csv")

    print("\nCITY ANALYSIS")
    print(df.to_string(index=False))


# ============================================================
# 13. STATE ANALYSIS
# ============================================================

def analysis_state(conn):

    query = """
    SELECT
        o.State,

        COUNT(DISTINCT o.OrderID) AS Orders,

        COUNT(DISTINCT o.CustomerID) AS Customers,

        SUM(oi.Quantity) AS Units,

        ROUND(SUM(oi.NetRevenue),2) AS NetRevenue,

        ROUND(SUM(oi.NetRevenue - oi.CostAmount),2)
            AS GrossProfit

    FROM fact_orders o

    INNER JOIN fact_order_items oi
        ON o.OrderID = oi.OrderID

    GROUP BY o.State

    ORDER BY NetRevenue DESC
    """

    df = run_query(conn, query)

    save_result(df, "13_state_analysis.csv")

    print("\nSTATE ANALYSIS")
    print(df.to_string(index=False))


# ============================================================
# 14. BRAND ANALYSIS
# ============================================================

def analysis_brand(conn):

    query = """
    SELECT
        p.Brand,

        COUNT(DISTINCT oi.OrderID) AS Orders,

        SUM(oi.Quantity) AS Units,

        ROUND(SUM(oi.NetRevenue),2) AS NetRevenue,

        ROUND(
            SUM(oi.NetRevenue - oi.CostAmount),
            2
        ) AS GrossProfit

    FROM fact_order_items oi

    INNER JOIN dim_products p
        ON oi.ProductID = p.ProductID

    GROUP BY p.Brand

    ORDER BY NetRevenue DESC
    """

    df = run_query(conn, query)

    save_result(df, "14_brand_analysis.csv")

    print("\nBRAND ANALYSIS")
    print(df.to_string(index=False))


# ============================================================
# 15. DISCOUNT ANALYSIS
# ============================================================

def analysis_discount(conn):

    query = """
    SELECT
        p.Category,

        ROUND(
            AVG(oi.DiscountPercent),
            2
        ) AS AvgDiscountPercent,

        ROUND(
            SUM(oi.Discount),
            2
        ) AS TotalDiscount,

        ROUND(
            SUM(oi.NetRevenue),
            2
        ) AS NetRevenue

    FROM fact_order_items oi

    INNER JOIN dim_products p
        ON oi.ProductID = p.ProductID

    GROUP BY p.Category

    ORDER BY TotalDiscount DESC
    """

    df = run_query(conn, query)

    save_result(df, "15_discount_analysis.csv")

    print("\nDISCOUNT ANALYSIS")
    print(df.to_string(index=False))


# ============================================================
# 16. TOP CUSTOMERS
# ============================================================

def analysis_top_customers(conn):

    query = """
    SELECT
        c.CustomerID,
        c.Name,
        c.City,
        c.State,
        c.CustomerSegment,

        COUNT(DISTINCT o.OrderID) AS Orders,

        SUM(oi.Quantity) AS Units,

        ROUND(
            SUM(oi.NetRevenue),
            2
        ) AS NetRevenue

    FROM dim_customers c

    INNER JOIN fact_orders o
        ON c.CustomerID = o.CustomerID

    INNER JOIN fact_order_items oi
        ON o.OrderID = oi.OrderID

    GROUP BY
        c.CustomerID,
        c.Name,
        c.City,
        c.State,
        c.CustomerSegment

    ORDER BY NetRevenue DESC

    LIMIT 100
    """

    df = run_query(conn, query)

    save_result(df, "16_top_100_customers.csv")

    print("\nTOP 100 CUSTOMERS")
    print(df.head(20).to_string(index=False))


# ============================================================
# 17. ORDER STATUS
# ============================================================

def analysis_order_status(conn):

    query = """
    SELECT
        OrderStatus,

        COUNT(*) AS Orders,

        ROUND(
            COUNT(*) * 100.0 /
            (SELECT COUNT(*) FROM fact_orders),
            2
        ) AS Percentage

    FROM fact_orders

    GROUP BY OrderStatus

    ORDER BY Orders DESC
    """

    df = run_query(conn, query)

    save_result(df, "17_order_status.csv")

    print("\nORDER STATUS")
    print(df.to_string(index=False))


# ============================================================
# 18. RETURN STATUS
# ============================================================

def analysis_return_status(conn):

    query = """
    SELECT
        ReturnStatus,

        COUNT(*) AS Returns,

        ROUND(
            SUM(RefundAmount),
            2
        ) AS RefundAmount

    FROM fact_returns

    GROUP BY ReturnStatus

    ORDER BY Returns DESC
    """

    df = run_query(conn, query)

    save_result(df, "18_return_status.csv")

    print("\nRETURN STATUS")
    print(df.to_string(index=False))


# ============================================================
# 19. INVENTORY STATUS
# ============================================================

def analysis_inventory_status(conn):

    query = """
    SELECT
        InventoryStatus,

        COUNT(*) AS ProductSnapshots,

        SUM(ClosingStock) AS ClosingStock,

        ROUND(
            SUM(InventoryValue),
            2
        ) AS InventoryValue

    FROM fact_inventory

    GROUP BY InventoryStatus

    ORDER BY ProductSnapshots DESC
    """

    df = run_query(conn, query)

    save_result(df, "19_inventory_status.csv")

    print("\nINVENTORY STATUS")
    print(df.to_string(index=False))


# ============================================================
# 20. BUSINESS KPI
# ============================================================

def analysis_business_kpi(conn):

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
            NULLIF(COUNT(DISTINCT o.OrderID),0),
            2
        ) AS AOV,

        ROUND(
            AVG(oi.DiscountPercent),
            2
        ) AS AvgDiscountPercent

    FROM fact_orders o

    INNER JOIN fact_order_items oi
        ON o.OrderID = oi.OrderID
    """

    df = run_query(conn, query)

    df["GrossMarginPercent"] = (
        df["GrossProfit"] /
        df["NetRevenue"].replace(0, pd.NA)
    ) * 100

    save_result(df, "20_business_kpi.csv")

    print("\nBUSINESS KPI")
    print(df.to_string(index=False))


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("QUICKCART - SQL BUSINESS ANALYSIS")
    print("=" * 70)

    print(f"Database : {DB_NAME}")
    print(f"Output   : {OUTPUT_DIR}")

    print("=" * 70)

    conn = None

    try:

        print("\nConnecting to MySQL...")

        conn = get_connection()

        print("MySQL connection successful.")

        show_schema(conn)

        print("\n" + "=" * 70)
        print("RUNNING BUSINESS ANALYSIS")
        print("=" * 70)

        analysis_database_summary(conn)
        analysis_order_summary(conn)
        analysis_category_sales(conn)
        analysis_top_products(conn)
        analysis_monthly_sales(conn)
        analysis_customer_analysis(conn)
        analysis_customer_segments(conn)
        analysis_payments(conn)
        analysis_returns(conn)
        analysis_delivery(conn)
        analysis_inventory(conn)
        analysis_city(conn)
        analysis_state(conn)
        analysis_brand(conn)
        analysis_discount(conn)
        analysis_top_customers(conn)
        analysis_order_status(conn)
        analysis_return_status(conn)
        analysis_inventory_status(conn)
        analysis_business_kpi(conn)

        print("\n" + "=" * 70)
        print("SQL ANALYSIS COMPLETED SUCCESSFULLY")
        print("=" * 70)

        print(f"\nAll analysis files saved in:")
        print(OUTPUT_DIR)

    except Exception as e:

        print("\n" + "=" * 70)
        print("SQL ANALYSIS ERROR")
        print("=" * 70)

        print(type(e).__name__)
        print(str(e))

        raise

    finally:

        if conn is not None and conn.is_connected():

            conn.close()

            print("\nMySQL connection closed.")


if __name__ == "__main__":
    main()