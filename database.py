# ============================================================
# QUICKCART - E-COMMERCE ANALYTICS PLATFORM
# MYSQL DATABASE BUILDER + DATA LOADER
# ============================================================

from pathlib import Path
import re

import pandas as pd
import mysql.connector
from mysql.connector import Error


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(
    r"C:\Users\harsh\OneDrive\Desktop\ecomarece"
)

PROCESSED_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)


# ============================================================
# MYSQL CONFIGURATION
# ============================================================

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "harsh"

DB_NAME = "quickcart_ecommerce"


# ============================================================
# TABLE + CSV MAPPING
# ============================================================

TABLE_FILES = {

    "dim_location":
        "dim_location.csv",

    "dim_customers":
        "dim_customers.csv",

    "dim_products":
        "dim_products.csv",

    "dim_date":
        "dim_date.csv",

    "fact_orders":
        "fact_orders.csv",

    "fact_order_items":
        "fact_order_items.csv",

    "fact_payments":
        "fact_payments.csv",

    "fact_returns":
        "fact_returns.csv",

    "fact_deliveries":
        "fact_deliveries.csv",

    "fact_inventory":
        "fact_inventory.csv",
}


# ============================================================
# TABLE CREATION ORDER
# ============================================================

TABLE_ORDER = [

    "dim_location",

    "dim_customers",

    "dim_products",

    "dim_date",

    "fact_orders",

    "fact_order_items",

    "fact_payments",

    "fact_returns",

    "fact_deliveries",

    "fact_inventory",
]


# ============================================================
# PRIMARY KEY CONFIGURATION
# ============================================================

PRIMARY_KEYS = {

    "dim_location":
        "LocationID",

    "dim_customers":
        "CustomerID",

    "dim_products":
        "ProductID",

    "dim_date":
        "DateKey",

    "fact_orders":
        "OrderID",

    "fact_order_items":
        "OrderItemID",

    "fact_payments":
        "PaymentID",

    "fact_returns":
        "ReturnID",

    "fact_deliveries":
        "DeliveryID",

    "fact_inventory":
        "InventoryID",
}


# ============================================================
# CONNECTION
# ============================================================

def get_connection(database=None):

    config = {

        "host":
            DB_HOST,

        "port":
            DB_PORT,

        "user":
            DB_USER,

        "password":
            DB_PASSWORD,
    }

    if database:

        config["database"] = database

    return mysql.connector.connect(
        **config
    )


# ============================================================
# MYSQL IDENTIFIER
# ============================================================

def quote_identifier(name):

    return (
        "`"
        + str(name).replace("`", "``")
        + "`"
    )


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            f"""
            CREATE DATABASE IF NOT EXISTS
            {quote_identifier(DB_NAME)}
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci
            """
        )

        connection.commit()

        print(
            f"Database ready: {DB_NAME}"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# CLEAN COLUMN NAME
# ============================================================

def clean_column_name(column):

    column = str(
        column
    ).strip()

    column = re.sub(
        r"[^a-zA-Z0-9_]",
        "_",
        column
    )

    column = re.sub(
        r"_+",
        "_",
        column
    )

    column = column.strip("_")

    if not column:

        column = "column_name"

    if column[0].isdigit():

        column = (
            "col_"
            + column
        )

    return column


# ============================================================
# READ CSV
# ============================================================

def read_csv_file(file_path):

    df = pd.read_csv(
        file_path
    )

    df.columns = [

        clean_column_name(
            column
        )

        for column in df.columns
    ]

    return df


# ============================================================
# CHECK ID COLUMN
# ============================================================

def is_id_column(column):

    col = str(
        column
    ).lower()

    # DateKey is numeric
    if col == "datekey":

        return False

    if col.endswith("id"):

        return True

    if "_id" in col:

        return True

    return False


# ============================================================
# CHECK DATETIME
# ============================================================

def is_datetime_column(column):

    col = str(
        column
    ).lower()

    datetime_keywords = [

        "timestamp",

        "datetime",

        "created_at",

        "updated_at",

        "approved_at",

        "purchase_datetime",

        "payment_datetime",

        "return_datetime",

        "delivery_datetime",

        "delivered_at",

        "estimated_delivery_datetime",

        "signup_datetime",
    ]

    for keyword in datetime_keywords:

        if keyword in col:

            return True

    return False


# ============================================================
# CHECK DATE
# ============================================================

def is_date_column(column):

    col = str(
        column
    ).lower()

    if col == "date":

        return True

    if col == "datekey":

        return False

    if col.endswith("_date"):

        return True

    return False


# ============================================================
# CHECK BOOLEAN
# ============================================================

def is_boolean_column(column):

    col = str(
        column
    ).lower()

    return (

        col.startswith("is_")

        or

        col.startswith("has_")

        or

        col.endswith("_flag")
    )


# ============================================================
# MYSQL DATA TYPE
# ============================================================

def mysql_type(
    series,
    column
):

    column_lower = str(
        column
    ).lower()

    # --------------------------------------------------------
    # DateKey
    # --------------------------------------------------------

    if column_lower == "datekey":

        return "INT"

    # --------------------------------------------------------
    # IDs
    # --------------------------------------------------------

    if is_id_column(column):

        return "VARCHAR(50)"

    # --------------------------------------------------------
    # Datetime
    # --------------------------------------------------------

    if is_datetime_column(column):

        return "DATETIME"

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    if is_date_column(column):

        return "DATE"

    # --------------------------------------------------------
    # Boolean
    # --------------------------------------------------------

    if is_boolean_column(column):

        return "TINYINT"

    # --------------------------------------------------------
    # Integer
    # --------------------------------------------------------

    if pd.api.types.is_integer_dtype(
        series
    ):

        return "BIGINT"

    # --------------------------------------------------------
    # Float
    # --------------------------------------------------------

    if pd.api.types.is_float_dtype(
        series
    ):

        return "DECIMAL(18,4)"

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    try:

        values = (
            series
            .dropna()
            .astype(str)
        )

        if len(values) > 0:

            max_length = int(
                values.str.len().max()
            )

        else:

            max_length = 0

    except Exception:

        max_length = 0

    if max_length <= 100:

        return "VARCHAR(100)"

    if max_length <= 255:

        return "VARCHAR(255)"

    return "TEXT"


# ============================================================
# GET PRIMARY KEY
# ============================================================

def get_primary_key(
    table_name,
    df
):

    primary_key = PRIMARY_KEYS.get(
        table_name
    )

    if primary_key is None:

        return None

    if primary_key not in df.columns:

        raise ValueError(
            f"Expected primary key "
            f"{primary_key} not found in "
            f"{table_name}. "
            f"Available columns: "
            f"{list(df.columns)}"
        )

    return primary_key


# ============================================================
# DROP OLD TABLES
# ============================================================

def drop_old_tables(
    cursor
):

    print(
        "\nRemoving old QuickCart tables..."
    )

    cursor.execute(
        "SET FOREIGN_KEY_CHECKS = 0"
    )

    for table_name in reversed(
        TABLE_ORDER
    ):

        cursor.execute(
            f"""
            DROP TABLE IF EXISTS
            {quote_identifier(table_name)}
            """
        )

        print(
            f"   Dropped: {table_name}"
        )

    cursor.execute(
        "SET FOREIGN_KEY_CHECKS = 1"
    )


# ============================================================
# CREATE TABLE
# ============================================================

def create_table(
    cursor,
    table_name,
    df
):

    column_definitions = []

    # --------------------------------------------------------
    # Columns
    # --------------------------------------------------------

    for column in df.columns:

        data_type = mysql_type(
            df[column],
            column
        )

        column_definitions.append(

            f"{quote_identifier(column)} "
            f"{data_type}"
        )

    # --------------------------------------------------------
    # Correct Primary Key
    # --------------------------------------------------------

    primary_key = get_primary_key(
        table_name,
        df
    )

    primary_key_sql = ""

    if primary_key:

        primary_key_sql = f"""

        ,
        PRIMARY KEY
        (
            {quote_identifier(primary_key)}
        )

        """

    # --------------------------------------------------------
    # CREATE TABLE
    # --------------------------------------------------------

    sql = f"""

    CREATE TABLE
    {quote_identifier(table_name)}
    (

        {", ".join(column_definitions)}

        {primary_key_sql}

    )

    ENGINE=InnoDB

    DEFAULT CHARSET=utf8mb4

    COLLATE=utf8mb4_unicode_ci

    """

    cursor.execute(
        sql
    )

    print(
        f"   Created: {table_name}"
    )

    print(
        f"      Primary Key: "
        f"{primary_key}"
    )


# ============================================================
# PREPARE VALUE
# ============================================================

def prepare_value(value):

    if pd.isna(value):

        return None

    if isinstance(
        value,
        pd.Timestamp
    ):

        return value.to_pydatetime()

    return value


# ============================================================
# INSERT DATAFRAME
# ============================================================

def insert_dataframe(
    cursor,
    table_name,
    df
):

    if df.empty:

        return 0

    columns = list(
        df.columns
    )

    column_sql = ", ".join(

        quote_identifier(
            column
        )

        for column in columns
    )

    placeholders = ", ".join(

        ["%s"]
        * len(columns)
    )

    sql = f"""

    INSERT INTO
    {quote_identifier(table_name)}

    (
        {column_sql}
    )

    VALUES
    (
        {placeholders}
    )

    """

    records = []

    for row in df.itertuples(
        index=False,
        name=None
    ):

        records.append(

            tuple(

                prepare_value(
                    value
                )

                for value in row
            )
        )

    cursor.executemany(
        sql,
        records
    )

    return len(records)


# ============================================================
# CREATE INDEXES
# ============================================================

def create_indexes(
    cursor,
    table_name,
    df
):

    index_number = 1

    for column in df.columns:

        col_lower = str(
            column
        ).lower()

        should_index = False

        # ----------------------------------------------------
        # IDs
        # ----------------------------------------------------

        if is_id_column(column):

            should_index = True

        # ----------------------------------------------------
        # Business fields
        # ----------------------------------------------------

        if col_lower in [

            "order_status",

            "payment_method",

            "payment_status",

            "return_status",

            "delivery_status",

            "category",

            "category_name",

            "city",

            "state",

            "region",

            "order_date",

            "order_month",

            "year",

            "month",
        ]:

            should_index = True

        if not should_index:

            continue

        index_name = (

            f"idx_"
            f"{table_name}_"
            f"{index_number}"
        )

        try:

            cursor.execute(

                f"""

                CREATE INDEX
                {quote_identifier(index_name)}

                ON
                {quote_identifier(table_name)}

                (
                    {quote_identifier(column)}
                )

                """
            )

        except Error:

            pass

        index_number += 1


# ============================================================
# VALIDATE FILES
# ============================================================

def validate_input_files():

    print(
        "\nChecking processed CSV files..."
    )

    for (
        table_name,
        file_name
    ) in TABLE_FILES.items():

        file_path = (
            PROCESSED_DIR
            / file_name
        )

        if not file_path.exists():

            raise FileNotFoundError(

                f"Missing file: "
                f"{file_path}"
            )

        print(
            f"   OK: {file_name}"
        )


# ============================================================
# SHOW IMPORTANT COLUMNS
# ============================================================

def show_table_columns(
    cursor,
    table_name
):

    cursor.execute(

        f"""

        DESCRIBE
        {quote_identifier(table_name)}

        """
    )

    rows = cursor.fetchall()

    print(
        f"\n   {table_name}:"
    )

    for row in rows:

        column_name = row[0]

        data_type = row[1]

        key_type = row[3]

        if str(
            column_name
        ).lower() in [

            "locationid",

            "customerid",

            "productid",

            "datekey",

            "orderid",

            "orderitemid",

            "paymentid",

            "returnid",

            "deliveryid",

            "inventoryid",
        ]:

            print(

                f"      "
                f"{column_name:<18}"
                f"{str(data_type):<18}"
                f"{key_type}"
            )


# ============================================================
# FOREIGN KEYS
# ============================================================

def add_foreign_keys(
    cursor,
    dataframes
):

    relationships = [

        # ----------------------------------------------------
        # Customers -> Location
        # ----------------------------------------------------

        (
            "dim_customers",
            "LocationID",

            "dim_location",
            "LocationID",

            "fk_customer_location",
        ),

        # ----------------------------------------------------
        # Orders -> Customers
        # ----------------------------------------------------

        (
            "fact_orders",
            "CustomerID",

            "dim_customers",
            "CustomerID",

            "fk_orders_customer",
        ),

        # ----------------------------------------------------
        # Orders -> Location
        # ----------------------------------------------------

        (
            "fact_orders",
            "LocationID",

            "dim_location",
            "LocationID",

            "fk_orders_location",
        ),

        # ----------------------------------------------------
        # Orders -> Date
        # ----------------------------------------------------

        (
            "fact_orders",
            "DateKey",

            "dim_date",
            "DateKey",

            "fk_orders_date",
        ),

        # ----------------------------------------------------
        # Order Items -> Orders
        # ----------------------------------------------------

        (
            "fact_order_items",
            "OrderID",

            "fact_orders",
            "OrderID",

            "fk_items_order",
        ),

        # ----------------------------------------------------
        # Order Items -> Products
        # ----------------------------------------------------

        (
            "fact_order_items",
            "ProductID",

            "dim_products",
            "ProductID",

            "fk_items_product",
        ),

        # ----------------------------------------------------
        # Payments -> Orders
        # ----------------------------------------------------

        (
            "fact_payments",
            "OrderID",

            "fact_orders",
            "OrderID",

            "fk_payments_order",
        ),

        # ----------------------------------------------------
        # Returns -> Orders
        # ----------------------------------------------------

        (
            "fact_returns",
            "OrderID",

            "fact_orders",
            "OrderID",

            "fk_returns_order",
        ),

        # ----------------------------------------------------
        # Deliveries -> Orders
        # ----------------------------------------------------

        (
            "fact_deliveries",
            "OrderID",

            "fact_orders",
            "OrderID",

            "fk_deliveries_order",
        ),

        # ----------------------------------------------------
        # Inventory -> Products
        # ----------------------------------------------------

        (
            "fact_inventory",
            "ProductID",

            "dim_products",
            "ProductID",

            "fk_inventory_product",
        ),

        # ----------------------------------------------------
        # Inventory -> Location
        # ----------------------------------------------------

        (
            "fact_inventory",
            "LocationID",

            "dim_location",
            "LocationID",

            "fk_inventory_location",
        ),
    ]

    print(
        "\nCreating foreign-key relationships..."
    )

    for (
        child_table,
        child_column,

        parent_table,
        parent_column,

        constraint_name,

    ) in relationships:

        # ----------------------------------------------------
        # Check tables
        # ----------------------------------------------------

        if child_table not in dataframes:

            continue

        if parent_table not in dataframes:

            continue

        child_df = dataframes[
            child_table
        ]

        parent_df = dataframes[
            parent_table
        ]

        # ----------------------------------------------------
        # Check columns
        # ----------------------------------------------------

        if child_column not in child_df.columns:

            continue

        if parent_column not in parent_df.columns:

            continue

        # ----------------------------------------------------
        # Add FK
        # ----------------------------------------------------

        try:

            sql = f"""

            ALTER TABLE
            {quote_identifier(child_table)}

            ADD CONSTRAINT
            {quote_identifier(constraint_name)}

            FOREIGN KEY
            (
                {quote_identifier(child_column)}
            )

            REFERENCES
            {quote_identifier(parent_table)}
            (
                {quote_identifier(parent_column)}
            )

            """

            cursor.execute(
                sql
            )

            print(

                f"   OK: "
                f"{child_table}."
                f"{child_column}"
                f" -> "
                f"{parent_table}."
                f"{parent_column}"
            )

        except Error as error:

            print(

                f"   SKIPPED: "
                f"{child_table}."
                f"{child_column}"
            )

            print(
                f"      Reason: "
                f"{error}"
            )


# ============================================================
# ROW COUNT
# ============================================================

def show_row_count(
    cursor,
    table_name
):

    cursor.execute(

        f"""

        SELECT COUNT(*)

        FROM
        {quote_identifier(table_name)}

        """
    )

    count = cursor.fetchone()[0]

    print(

        f"   "
        f"{table_name:<24}"
        f": "
        f"{count:,} rows"
    )


# ============================================================
# VERIFY PRIMARY KEYS
# ============================================================

def verify_primary_keys(
    cursor
):

    print(
        "\nPrimary Key Verification:"
    )

    for table_name in TABLE_ORDER:

        expected_pk = PRIMARY_KEYS[
            table_name
        ]

        cursor.execute(

            f"""

            SHOW KEYS

            FROM
            {quote_identifier(table_name)}

            WHERE
            Key_name = 'PRIMARY'

            """
        )

        rows = cursor.fetchall()

        actual_pk = None

        if rows:

            actual_pk = rows[0][4]

        if actual_pk == expected_pk:

            print(

                f"   PASS: "
                f"{table_name:<24}"
                f"-> {actual_pk}"
            )

        else:

            print(

                f"   FAIL: "
                f"{table_name:<24}"
                f"expected {expected_pk}, "
                f"found {actual_pk}"
            )


# ============================================================
# MAIN DATABASE LOADER
# ============================================================

def load_database():

    connection = None

    cursor = None

    dataframes = {}

    try:

        # ====================================================
        # 1. CONNECTION
        # ====================================================

        print(
            "\n[1/7] Testing MySQL connection..."
        )

        connection = get_connection()

        print(
            "MySQL connection successful."
        )

        cursor = connection.cursor()

        # ====================================================
        # 2. DATABASE
        # ====================================================

        print(
            "\n[2/7] Creating database..."
        )

        cursor.execute(

            f"""

            CREATE DATABASE IF NOT EXISTS
            {quote_identifier(DB_NAME)}

            CHARACTER SET utf8mb4

            COLLATE utf8mb4_unicode_ci

            """
        )

        connection.commit()

        cursor.close()

        connection.close()

        connection = get_connection(
            DB_NAME
        )

        cursor = connection.cursor()

        print(
            f"Database ready: {DB_NAME}"
        )

        # ====================================================
        # 3. FILES
        # ====================================================

        print(
            "\n[3/7] Checking CSV files..."
        )

        validate_input_files()

        # ====================================================
        # 4. READ DATA
        # ====================================================

        print(
            "\n[4/7] Reading cleaned CSV files..."
        )

        for (
            table_name,
            file_name
        ) in TABLE_FILES.items():

            file_path = (
                PROCESSED_DIR
                / file_name
            )

            df = read_csv_file(
                file_path
            )

            dataframes[
                table_name
            ] = df

            print(

                f"   "
                f"{table_name:<24}"
                f"{len(df):>10,} rows"
            )

            print(

                f"      "
                f"Columns: "
                f"{len(df.columns)}"
            )

        # ====================================================
        # 5. REBUILD TABLES
        # ====================================================

        print(
            "\n[5/7] Rebuilding MySQL tables..."
        )

        # ----------------------------------------------------
        # Disable FK checks
        # ----------------------------------------------------

        cursor.execute(
            "SET FOREIGN_KEY_CHECKS = 0"
        )

        # ----------------------------------------------------
        # Drop old tables
        # ----------------------------------------------------

        drop_old_tables(
            cursor
        )

        # ----------------------------------------------------
        # Create new tables
        # ----------------------------------------------------

        for table_name in TABLE_ORDER:

            create_table(

                cursor,

                table_name,

                dataframes[
                    table_name
                ]
            )

        connection.commit()

        cursor.execute(
            "SET FOREIGN_KEY_CHECKS = 1"
        )

        # ====================================================
        # 6. LOAD DATA
        # ====================================================

        print(
            "\n[6/7] Loading data into MySQL..."
        )

        for table_name in TABLE_ORDER:

            df = dataframes[
                table_name
            ]

            print(
                f"\nLoading "
                f"{table_name}.csv"
            )

            print(

                f"Prepared "
                f"{table_name} : "
                f"{len(df):,} rows"
            )

            inserted = insert_dataframe(

                cursor,

                table_name,

                df
            )

            connection.commit()

            print(

                f"Inserted "
                f"{inserted:,} rows"
            )

        # ====================================================
        # 7. INDEXES + FOREIGN KEYS
        # ====================================================

        print(
            "\n[7/7] Creating indexes "
            "and relationships..."
        )

        # ----------------------------------------------------
        # Indexes
        # ----------------------------------------------------

        for table_name in TABLE_ORDER:

            create_indexes(

                cursor,

                table_name,

                dataframes[
                    table_name
                ]
            )

        connection.commit()

        # ----------------------------------------------------
        # Foreign Keys
        # ----------------------------------------------------

        add_foreign_keys(

            cursor,

            dataframes
        )

        connection.commit()

        # ====================================================
        # FINAL VERIFICATION
        # ====================================================

        print(
            "\n"
            + "=" * 60
        )

        print(
            "FINAL DATABASE VERIFICATION"
        )

        print(
            "=" * 60
        )

        # ----------------------------------------------------
        # Row Counts
        # ----------------------------------------------------

        print(
            "\nTable Row Counts:"
        )

        for table_name in TABLE_ORDER:

            show_row_count(

                cursor,

                table_name
            )

        # ----------------------------------------------------
        # Primary Keys
        # ----------------------------------------------------

        verify_primary_keys(
            cursor
        )

        # ----------------------------------------------------
        # Important ID Datatypes
        # ----------------------------------------------------

        print(
            "\nImportant ID Datatypes:"
        )

        for table_name in TABLE_ORDER:

            show_table_columns(

                cursor,

                table_name
            )

        # ----------------------------------------------------
        # Tables
        # ----------------------------------------------------

        cursor.execute(
            "SHOW TABLES"
        )

        tables = cursor.fetchall()

        print(
            "\nMySQL Tables:"
        )

        for table in tables:

            print(
                f"   {table[0]}"
            )

        # ====================================================
        # SUCCESS
        # ====================================================

        print(
            "\n"
            + "=" * 60
        )

        print(
            "SUCCESS: QUICKCART MYSQL DATABASE READY"
        )

        print(
            "=" * 60
        )

        print(
            f"Database : "
            f"{DB_NAME}"
        )

        print(
            f"Host     : "
            f"{DB_HOST}:{DB_PORT}"
        )

        print(
            f"Tables   : "
            f"{len(tables)}"
        )

        print(
            "Data     : "
            "Loaded successfully"
        )

        print(
            "=" * 60
        )

    except Error as error:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "MYSQL ERROR"
        )

        print(
            "=" * 60
        )

        print(
            error
        )

        print(
            "=" * 60
        )

        if connection:

            try:

                connection.rollback()

            except Exception:

                pass

        raise

    except Exception as error:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "ERROR"
        )

        print(
            "=" * 60
        )

        print(
            error
        )

        print(
            "=" * 60
        )

        if connection:

            try:

                connection.rollback()

            except Exception:

                pass

        raise

    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    print(
        "\n"
        + "=" * 60
    )

    print(
        "QUICKCART - MYSQL DATABASE BUILDER"
    )

    print(
        "=" * 60
    )

    print(
        f"Project : "
        f"{BASE_DIR}"
    )

    print(
        f"Database: "
        f"{DB_NAME}"
    )

    print(
        "=" * 60
    )

    load_database()