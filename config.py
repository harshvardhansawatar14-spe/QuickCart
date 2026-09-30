"""
QUICKCART
Central Project Configuration

All major project settings are maintained in this file so that
the remaining modules can use one consistent configuration.
"""

from __future__ import annotations

import os
from pathlib import Path


# ============================================================
# PROJECT INFORMATION
# ============================================================

PROJECT_NAME = "QuickCart"
PROJECT_VERSION = "1.0.0"

RANDOM_SEED = 42

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# DIRECTORY STRUCTURE
# ============================================================

SRC_DIR = BASE_DIR / "src"

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

DATABASE_DIR = BASE_DIR / "database"

POWERBI_DIR = BASE_DIR / "powerbi"

REPORTS_DIR = BASE_DIR / "reports"

DASHBOARD_DIR = BASE_DIR / "dashboard"

LOGS_DIR = BASE_DIR / "logs"


ALL_DIRECTORIES = [
    SRC_DIR,
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    DATABASE_DIR,
    POWERBI_DIR,
    REPORTS_DIR,
    DASHBOARD_DIR,
    LOGS_DIR,
]


# ============================================================
# DATASET SIZE
# ============================================================

CUSTOMER_COUNT = 12000

PRODUCT_COUNT = 750

ORDER_COUNT = 120000

MIN_ORDER_ITEMS = 200000

PAYMENT_COUNT = ORDER_COUNT


# ============================================================
# DATE RANGE
# ============================================================

DATA_START_DATE = "2024-01-01"

DATA_END_DATE = "2026-09-25"


# ============================================================
# BUSINESS SETTINGS
# ============================================================

MIN_ORDER_QUANTITY = 1

MAX_ORDER_QUANTITY = 8

MIN_DISCOUNT_PERCENT = 0.00

MAX_DISCOUNT_PERCENT = 0.25

GST_MIN_PERCENT = 0.00

GST_MAX_PERCENT = 0.18

DEFAULT_DELIVERY_TARGET_MINUTES = 30

LATE_DELIVERY_THRESHOLD_MINUTES = 30

RETURN_WINDOW_DAYS = 7


# ============================================================
# CUSTOMER SETTINGS
# ============================================================

MIN_CUSTOMER_AGE = 18

MAX_CUSTOMER_AGE = 70


GENDERS = [
    "Male",
    "Female",
    "Other",
]


CUSTOMER_SEGMENTS = [
    "Champions",
    "Loyal Customers",
    "Potential Loyalists",
    "At Risk",
    "Lost Customers",
]


# ============================================================
# PRODUCT CATEGORIES
# ============================================================

CATEGORIES = [
    "Fresh Fruits",
    "Fresh Vegetables",
    "Dairy",
    "Staples",
    "Snacks",
    "Beverages",
    "Personal Care",
    "Household Cleaning",
    "Bakery",
    "Frozen Foods",
    "Baby Care",
    "Other",
]


# ============================================================
# PRODUCT SUB-CATEGORIES
# ============================================================

SUBCATEGORIES = {
    "Fresh Fruits": [
        "Apples",
        "Bananas",
        "Mangoes",
        "Oranges",
        "Grapes",
        "Pomegranate",
        "Papaya",
        "Watermelon",
        "Guava",
        "Pears",
    ],

    "Fresh Vegetables": [
        "Potatoes",
        "Tomatoes",
        "Onions",
        "Carrots",
        "Spinach",
        "Cabbage",
        "Cauliflower",
        "Capsicum",
        "Cucumber",
        "Broccoli",
    ],

    "Dairy": [
        "Milk",
        "Curd",
        "Butter",
        "Cheese",
        "Paneer",
        "Lassi",
        "Cream",
        "Flavoured Milk",
    ],

    "Staples": [
        "Rice",
        "Wheat Flour",
        "Pulses",
        "Dal",
        "Sugar",
        "Salt",
        "Cooking Oil",
        "Poha",
        "Rava",
        "Besan",
    ],

    "Snacks": [
        "Chips",
        "Biscuits",
        "Namkeen",
        "Popcorn",
        "Cookies",
        "Chocolates",
        "Protein Bars",
        "Dry Snacks",
    ],

    "Beverages": [
        "Tea",
        "Coffee",
        "Juice",
        "Soft Drinks",
        "Energy Drinks",
        "Mineral Water",
        "Green Tea",
        "Cold Coffee",
    ],

    "Personal Care": [
        "Shampoo",
        "Soap",
        "Face Wash",
        "Toothpaste",
        "Toothbrush",
        "Deodorant",
        "Hair Oil",
        "Skin Care",
    ],

    "Household Cleaning": [
        "Detergent",
        "Dishwash",
        "Floor Cleaner",
        "Toilet Cleaner",
        "Glass Cleaner",
        "Disinfectant",
        "Garbage Bags",
        "Cleaning Tools",
    ],

    "Bakery": [
        "Bread",
        "Buns",
        "Cakes",
        "Muffins",
        "Cookies",
        "Croissants",
        "Pav",
    ],

    "Frozen Foods": [
        "Frozen Peas",
        "Frozen Corn",
        "Frozen Snacks",
        "Frozen Paratha",
        "Ice Cream",
        "Frozen Vegetables",
    ],

    "Baby Care": [
        "Baby Diapers",
        "Baby Food",
        "Baby Wipes",
        "Baby Shampoo",
        "Baby Soap",
        "Baby Lotion",
    ],

    "Other": [
        "Pooja Essentials",
        "Stationery",
        "Pet Supplies",
        "Kitchen Essentials",
        "Miscellaneous",
    ],
}


# ============================================================
# BRANDS
# ============================================================

BRANDS = [
    "Amul",
    "Mother Dairy",
    "Nestle",
    "Britannia",
    "Parle",
    "ITC",
    "Haldiram's",
    "Tata",
    "Aashirvaad",
    "Fortune",
    "Surf Excel",
    "Harpic",
    "Vim",
    "Dove",
    "Lifebuoy",
    "Dettol",
    "Colgate",
    "PepsiCo",
    "Coca-Cola",
    "Lay's",
    "Kurkure",
    "Maggi",
    "Thums Up",
    "Real",
    "Paper Boat",
    "Red Bull",
    "London Dairy",
    "Kwality Wall's",
    "Patanjali",
    "Dabur",
    "Himalaya",
    "Nivea",
    "Pears",
    "Saffola",
    "India Gate",
    "Daawat",
    "Fortune",
    "Parachute",
    "Clinic Plus",
    "Head & Shoulders",
]


# ============================================================
# SUPPLIERS
# ============================================================

SUPPLIERS = [
    "Reliance Consumer Products",
    "DMart Supply Chain",
    "Metro Cash & Carry",
    "BigBasket Wholesale",
    "Udaan Distribution",
    "Nature's Basket Supply",
    "FreshKart Distributors",
    "Maharashtra Food Supply",
    "Hyderabad Wholesale Mart",
    "South India FMCG Supply",
    "Western India Grocery Supply",
    "National FMCG Distribution",
    "GreenHarvest Suppliers",
    "DailyNeeds Distribution",
    "UrbanBasket Suppliers",
]


# ============================================================
# INDIAN LOCATIONS
# ============================================================

LOCATION_DATA = [
    {
        "city": "Mumbai",
        "state": "Maharashtra",
        "region": "West",
        "tier": "Tier 1",
    },
    {
        "city": "Pune",
        "state": "Maharashtra",
        "region": "West",
        "tier": "Tier 1",
    },
    {
        "city": "Nagpur",
        "state": "Maharashtra",
        "region": "West",
        "tier": "Tier 2",
    },
    {
        "city": "Nashik",
        "state": "Maharashtra",
        "region": "West",
        "tier": "Tier 2",
    },
    {
        "city": "Aurangabad",
        "state": "Maharashtra",
        "region": "West",
        "tier": "Tier 2",
    },
    {
        "city": "Latur",
        "state": "Maharashtra",
        "region": "West",
        "tier": "Tier 2",
    },
    {
        "city": "Hyderabad",
        "state": "Telangana",
        "region": "South",
        "tier": "Tier 1",
    },
    {
        "city": "Warangal",
        "state": "Telangana",
        "region": "South",
        "tier": "Tier 2",
    },
    {
        "city": "Bengaluru",
        "state": "Karnataka",
        "region": "South",
        "tier": "Tier 1",
    },
    {
        "city": "Mysuru",
        "state": "Karnataka",
        "region": "South",
        "tier": "Tier 2",
    },
    {
        "city": "Delhi",
        "state": "Delhi",
        "region": "North",
        "tier": "Tier 1",
    },
    {
        "city": "Chennai",
        "state": "Tamil Nadu",
        "region": "South",
        "tier": "Tier 1",
    },
    {
        "city": "Ahmedabad",
        "state": "Gujarat",
        "region": "West",
        "tier": "Tier 1",
    },
    {
        "city": "Surat",
        "state": "Gujarat",
        "region": "West",
        "tier": "Tier 1",
    },
    {
        "city": "Kolkata",
        "state": "West Bengal",
        "region": "East",
        "tier": "Tier 1",
    },
    {
        "city": "Jaipur",
        "state": "Rajasthan",
        "region": "North",
        "tier": "Tier 1",
    },
    {
        "city": "Indore",
        "state": "Madhya Pradesh",
        "region": "Central",
        "tier": "Tier 2",
    },
    {
        "city": "Bhopal",
        "state": "Madhya Pradesh",
        "region": "Central",
        "tier": "Tier 2",
    },
    {
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "region": "North",
        "tier": "Tier 1",
    },
    {
        "city": "Kanpur",
        "state": "Uttar Pradesh",
        "region": "North",
        "tier": "Tier 2",
    },
    {
        "city": "Patna",
        "state": "Bihar",
        "region": "East",
        "tier": "Tier 2",
    },
    {
        "city": "Vadodara",
        "state": "Gujarat",
        "region": "West",
        "tier": "Tier 2",
    },
]


CITIES = [
    item["city"]
    for item in LOCATION_DATA
]


STATES = sorted(
    {
        item["state"]
        for item in LOCATION_DATA
    }
)


# ============================================================
# PAYMENT METHODS
# ============================================================

PAYMENT_METHODS = [
    "UPI",
    "Cards",
    "Cash on Delivery",
    "Wallets",
    "Net Banking",
]


# Probability distribution used by data generation.
PAYMENT_METHOD_WEIGHTS = {
    "UPI": 0.46,
    "Cards": 0.27,
    "Cash on Delivery": 0.14,
    "Wallets": 0.08,
    "Net Banking": 0.05,
}


# ============================================================
# ORDER STATUS
# ============================================================

ORDER_STATUSES = [
    "Delivered",
    "Cancelled",
    "Returned",
]


ORDER_STATUS_WEIGHTS = {
    "Delivered": 0.90,
    "Cancelled": 0.06,
    "Returned": 0.04,
}


# ============================================================
# RETURN STATUS
# ============================================================

RETURN_STATUSES = [
    "No Return",
    "Returned",
]


RETURN_REASONS = [
    "Damaged Product",
    "Wrong Product",
    "Quality Issue",
    "Expired Product",
    "Customer Changed Mind",
    "Missing Item",
]


# ============================================================
# CANCELLATION
# ============================================================

CANCELLATION_STATUSES = [
    "Not Cancelled",
    "Cancelled",
]


CANCELLATION_REASONS = [
    "Customer Changed Mind",
    "Payment Failure",
    "Out of Stock",
    "Delivery Delay",
    "Duplicate Order",
    "Other",
]


# ============================================================
# DELIVERY
# ============================================================

DELIVERY_STATUS = [
    "Delivered",
    "Late",
    "Cancelled",
]


DELIVERY_PARTNERS = [
    "QuickCart Delivery",
    "ShadowExpress",
    "RapidGo",
    "UrbanFleet",
    "FlashDelivery",
]


DELIVERY_TARGET_MINUTES = {
    "Tier 1": 30,
    "Tier 2": 40,
}


# ============================================================
# INVENTORY
# ============================================================

INVENTORY_STATUS = [
    "Healthy Stock",
    "Low Stock",
    "Out of Stock",
]


LOW_STOCK_THRESHOLD = 20

OUT_OF_STOCK_THRESHOLD = 0


# ============================================================
# PRODUCT PRICE RANGES
# ============================================================

CATEGORY_PRICE_RANGES = {
    "Fresh Fruits": (20, 450),
    "Fresh Vegetables": (15, 300),
    "Dairy": (20, 500),
    "Staples": (30, 1500),
    "Snacks": (10, 600),
    "Beverages": (10, 800),
    "Personal Care": (30, 1200),
    "Household Cleaning": (40, 1000),
    "Bakery": (20, 700),
    "Frozen Foods": (50, 900),
    "Baby Care": (80, 1800),
    "Other": (30, 1500),
}


# ============================================================
# PRODUCT MARGIN RANGES
# ============================================================

CATEGORY_MARGIN_RANGES = {
    "Fresh Fruits": (0.12, 0.28),
    "Fresh Vegetables": (0.12, 0.30),
    "Dairy": (0.10, 0.25),
    "Staples": (0.08, 0.22),
    "Snacks": (0.15, 0.35),
    "Beverages": (0.14, 0.32),
    "Personal Care": (0.18, 0.40),
    "Household Cleaning": (0.16, 0.35),
    "Bakery": (0.18, 0.38),
    "Frozen Foods": (0.15, 0.32),
    "Baby Care": (0.18, 0.38),
    "Other": (0.12, 0.30),
}


# ============================================================
# GST RATES
# ============================================================

CATEGORY_GST_RATES = {
    "Fresh Fruits": 0.00,
    "Fresh Vegetables": 0.00,
    "Dairy": 0.05,
    "Staples": 0.05,
    "Snacks": 0.12,
    "Beverages": 0.12,
    "Personal Care": 0.18,
    "Household Cleaning": 0.18,
    "Bakery": 0.05,
    "Frozen Foods": 0.05,
    "Baby Care": 0.05,
    "Other": 0.18,
}


# ============================================================
# CUSTOMER NAME DATA
# ============================================================

FIRST_NAMES_MALE = [
    "Aarav",
    "Vivaan",
    "Aditya",
    "Arjun",
    "Rohan",
    "Rahul",
    "Amit",
    "Akash",
    "Siddharth",
    "Kunal",
    "Harsh",
    "Vivek",
    "Nikhil",
    "Ankit",
    "Saurabh",
    "Pranav",
    "Rohit",
    "Yash",
    "Abhishek",
    "Manish",
    "Varun",
    "Tushar",
    "Omkar",
    "Tejas",
    "Shubham",
    "Sachin",
    "Sameer",
    "Raj",
    "Vikram",
    "Mohit",
]


FIRST_NAMES_FEMALE = [
    "Aanya",
    "Ananya",
    "Diya",
    "Isha",
    "Priya",
    "Sneha",
    "Neha",
    "Pooja",
    "Riya",
    "Kavya",
    "Meera",
    "Nandini",
    "Shruti",
    "Aditi",
    "Sakshi",
    "Simran",
    "Pallavi",
    "Swati",
    "Mansi",
    "Rutuja",
    "Tanvi",
    "Shreya",
    "Prachi",
    "Komal",
    "Anjali",
    "Payal",
    "Vaishnavi",
    "Madhuri",
    "Sonali",
    "Isha",
]


LAST_NAMES = [
    "Sharma",
    "Patil",
    "Deshmukh",
    "Kulkarni",
    "Jadhav",
    "Pawar",
    "Shinde",
    "Joshi",
    "More",
    "Sawant",
    "Chavan",
    "Kadam",
    "Gaikwad",
    "Bhosale",
    "Thakur",
    "Yadav",
    "Verma",
    "Gupta",
    "Mehta",
    "Shah",
    "Reddy",
    "Rao",
    "Nair",
    "Iyer",
    "Menon",
    "Das",
    "Banerjee",
    "Mishra",
    "Singh",
    "Kumar",
]


# ============================================================
# FILE NAMES
# ============================================================

RAW_CUSTOMERS_FILE = RAW_DATA_DIR / "customers.csv"
RAW_PRODUCTS_FILE = RAW_DATA_DIR / "products.csv"
RAW_ORDERS_FILE = RAW_DATA_DIR / "orders.csv"
RAW_ORDER_ITEMS_FILE = RAW_DATA_DIR / "order_items.csv"
RAW_PAYMENTS_FILE = RAW_DATA_DIR / "payments.csv"
RAW_RETURNS_FILE = RAW_DATA_DIR / "returns.csv"
RAW_DELIVERIES_FILE = RAW_DATA_DIR / "deliveries.csv"
RAW_INVENTORY_FILE = RAW_DATA_DIR / "inventory.csv"
RAW_LOCATIONS_FILE = RAW_DATA_DIR / "locations.csv"


PROCESSED_CUSTOMERS_FILE = PROCESSED_DATA_DIR / "dim_customers.csv"
PROCESSED_PRODUCTS_FILE = PROCESSED_DATA_DIR / "dim_products.csv"
PROCESSED_DATE_FILE = PROCESSED_DATA_DIR / "dim_date.csv"
PROCESSED_LOCATION_FILE = PROCESSED_DATA_DIR / "dim_location.csv"

PROCESSED_ORDERS_FILE = PROCESSED_DATA_DIR / "fact_orders.csv"
PROCESSED_ORDER_ITEMS_FILE = PROCESSED_DATA_DIR / "fact_order_items.csv"
PROCESSED_PAYMENTS_FILE = PROCESSED_DATA_DIR / "fact_payments.csv"
PROCESSED_RETURNS_FILE = PROCESSED_DATA_DIR / "fact_returns.csv"
PROCESSED_DELIVERIES_FILE = PROCESSED_DATA_DIR / "fact_deliveries.csv"
PROCESSED_INVENTORY_FILE = PROCESSED_DATA_DIR / "fact_inventory.csv"


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_NAME = "quickcart_analytics"

MYSQL_HOST = os.getenv(
    "QUICKCART_MYSQL_HOST",
    "localhost",
)

MYSQL_PORT = int(
    os.getenv(
        "QUICKCART_MYSQL_PORT",
        "3306",
    )
)

MYSQL_USER = os.getenv(
    "QUICKCART_MYSQL_USER",
    "root",
)

MYSQL_PASSWORD = os.getenv(
    "QUICKCART_MYSQL_PASSWORD",
    "",
)


MYSQL_DATABASE_CONFIG = {
    "host": MYSQL_HOST,
    "port": MYSQL_PORT,
    "user": MYSQL_USER,
    "password": MYSQL_PASSWORD,
    "database": DATABASE_NAME,
}


# SQLite fallback database.
SQLITE_DATABASE_FILE = DATABASE_DIR / "quickcart_analytics.sqlite3"


# ============================================================
# DATABASE TABLES
# ============================================================

DIMENSION_TABLES = [
    "dim_customers",
    "dim_products",
    "dim_date",
    "dim_location",
]


FACT_TABLES = [
    "fact_orders",
    "fact_order_items",
    "fact_payments",
    "fact_returns",
    "fact_deliveries",
    "fact_inventory",
]


ALL_TABLES = DIMENSION_TABLES + FACT_TABLES


# ============================================================
# REPORT FILES
# ============================================================

REPORT_FILES = {
    "executive_summary": REPORTS_DIR / "executive_summary.csv",
    "category_analysis": REPORTS_DIR / "category_analysis.csv",
    "city_analysis": REPORTS_DIR / "city_analysis.csv",
    "state_analysis": REPORTS_DIR / "state_analysis.csv",
    "customer_segments": REPORTS_DIR / "customer_segments.csv",
    "product_analysis": REPORTS_DIR / "product_analysis.csv",
    "payment_analysis": REPORTS_DIR / "payment_analysis.csv",
    "inventory_analysis": REPORTS_DIR / "inventory_analysis.csv",
    "delivery_analysis": REPORTS_DIR / "delivery_analysis.csv",
}


# ============================================================
# POWER BI OUTPUTS
# ============================================================

DAX_FILE = POWERBI_DIR / "DAX_Measures.txt"

POWERBI_MODEL_FILE = POWERBI_DIR / "PowerBI_Data_Model.txt"

DASHBOARD_DESIGN_FILE = POWERBI_DIR / "Dashboard_Design.txt"


# ============================================================
# PROJECT DOCUMENTATION
# ============================================================

README_FILE = BASE_DIR / "README.md"

RESUME_DESCRIPTION_FILE = (
    BASE_DIR / "resume_project_description.txt"
)

PROJECT_SUMMARY_FILE = (
    BASE_DIR / "project_summary.txt"
)

EXCEL_REPORT_FILE = (
    REPORTS_DIR / "QuickCart_Analytics_Report.xlsx"
)

HTML_DASHBOARD_FILE = (
    DASHBOARD_DIR / "dashboard.html"
)


# ============================================================
# POWER BI PAGES
# ============================================================

POWERBI_PAGES = [
    "Executive Overview",
    "Sales Analysis",
    "Product Analysis",
    "Customer Intelligence",
    "Regional Analysis",
    "Operations",
    "Inventory",
    "Payments & Discounts",
]


# ============================================================
# KPI DEFINITIONS
# ============================================================

CORE_KPIS = [
    "Total Revenue",
    "Net Revenue",
    "Total Orders",
    "Total Customers",
    "Total Units",
    "Average Order Value",
    "Return Rate",
    "Cancellation Rate",
    "Gross Margin",
    "Gross Margin %",
    "Average Delivery Time",
    "On-Time Delivery %",
    "Late Delivery %",
    "Inventory Value",
    "Stock-Out Products",
    "Low Stock Products",
]


ADVANCED_KPIS = [
    "YoY Revenue",
    "MoM Revenue",
    "Revenue Growth %",
    "Order Growth %",
    "Customer Growth %",
    "Average Discount",
    "Average Basket Size",
]


# ============================================================
# RFM SETTINGS
# ============================================================

RFM_QUANTILES = 5

RFM_SEGMENT_RULES = {
    "Champions": {
        "recency": (4, 5),
        "frequency": (4, 5),
        "monetary": (4, 5),
    },
    "Loyal Customers": {
        "recency": (3, 5),
        "frequency": (3, 5),
        "monetary": (3, 5),
    },
    "Potential Loyalists": {
        "recency": (4, 5),
        "frequency": (2, 3),
        "monetary": (2, 3),
    },
    "At Risk": {
        "recency": (1, 3),
        "frequency": (3, 5),
        "monetary": (3, 5),
    },
    "Lost Customers": {
        "recency": (1, 2),
        "frequency": (1, 2),
        "monetary": (1, 2),
    },
}


# ============================================================
# VALIDATION SETTINGS
# ============================================================

REQUIRED_CUSTOMER_COLUMNS = [
    "CustomerID",
    "Name",
    "Gender",
    "Age",
    "City",
    "State",
    "SignupDate",
    "CustomerSegment",
]


REQUIRED_PRODUCT_COLUMNS = [
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


REQUIRED_ORDER_COLUMNS = [
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


REQUIRED_ORDER_ITEM_COLUMNS = [
    "OrderItemID",
    "OrderID",
    "ProductID",
    "Quantity",
    "UnitPrice",
    "Discount",
    "Tax",
    "Revenue",
    "NetRevenue",
]


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def create_directories() -> None:
    """
    Create all configured project directories.
    """

    for directory in ALL_DIRECTORIES:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )


def get_database_url() -> str:
    """
    Return a human-readable MySQL connection description.

    Password is intentionally excluded for security.
    """

    return (
        f"mysql://{MYSQL_USER}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/"
        f"{DATABASE_NAME}"
    )


def get_project_info() -> dict:
    """
    Return core project configuration information.
    """

    return {
        "project_name": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "base_dir": str(BASE_DIR),
        "database": DATABASE_NAME,
        "customer_count": CUSTOMER_COUNT,
        "product_count": PRODUCT_COUNT,
        "order_count": ORDER_COUNT,
        "minimum_order_items": MIN_ORDER_ITEMS,
        "data_start_date": DATA_START_DATE,
        "data_end_date": DATA_END_DATE,
    }


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

def validate_config() -> None:
    """
    Validate important configuration values before the project
    pipeline starts.
    """

    if CUSTOMER_COUNT < 10000:
        raise ValueError(
            "CUSTOMER_COUNT must be at least 10,000."
        )

    if PRODUCT_COUNT < 500:
        raise ValueError(
            "PRODUCT_COUNT must be at least 500."
        )

    if ORDER_COUNT < 100000:
        raise ValueError(
            "ORDER_COUNT must be at least 100,000."
        )

    if MIN_ORDER_ITEMS < 200000:
        raise ValueError(
            "MIN_ORDER_ITEMS must be at least 200,000."
        )

    if not CATEGORIES:
        raise ValueError(
            "Product categories cannot be empty."
        )

    if not LOCATION_DATA:
        raise ValueError(
            "Location data cannot be empty."
        )

    if not PAYMENT_METHODS:
        raise ValueError(
            "Payment methods cannot be empty."
        )

    if RANDOM_SEED is None:
        raise ValueError(
            "RANDOM_SEED must be defined."
        )


# ============================================================
# MODULE INITIALIZATION
# ============================================================

create_directories()
validate_config()