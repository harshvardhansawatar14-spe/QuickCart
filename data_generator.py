"""
QUICKCART - E-Commerce / Grocery Analytics Platform
REALISTIC DATA GENERATOR

Generates:
    - Locations
    - Customers
    - Products
    - Orders
    - Order Items
    - Payments
    - Returns
    - Deliveries
    - Inventory
    - Date Dimension

Important business rules:
    1. Customer SignupDate <= customer's first OrderDate
    2. OrderDate always stays inside configured date range
    3. Cancelled orders do not receive delivery time
    4. Returned orders have valid return records
    5. Revenue calculations remain internally consistent
    6. Foreign-key relationships remain valid
    7. Reproducible using configured random seed
"""

from __future__ import annotations

import logging
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


import config


# ============================================================
# LOGGING
# ============================================================

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_FILE = LOG_DIR / "quickcart_data_generator.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

LOGGER = logging.getLogger(
    "QuickCart.DataGenerator"
)


# ============================================================
# RANDOM SEED
# ============================================================

SEED = int(
    getattr(
        config,
        "RANDOM_SEED",
        getattr(
            config,
            "SEED",
            42,
        ),
    )
)

random.seed(SEED)
np.random.seed(SEED)


# ============================================================
# DIRECTORIES
# ============================================================

RAW_DIR = Path(
    getattr(
        config,
        "RAW_DATA_DIR",
        PROJECT_ROOT / "data" / "raw",
    )
)

PROCESSED_DIR = Path(
    getattr(
        config,
        "PROCESSED_DATA_DIR",
        PROJECT_ROOT / "data" / "processed",
    )
)

RAW_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# CONFIGURATION
# ============================================================

CUSTOMER_COUNT = int(
    getattr(
        config,
        "CUSTOMER_COUNT",
        12000,
    )
)

PRODUCT_COUNT = int(
    getattr(
        config,
        "PRODUCT_COUNT",
        750,
    )
)

ORDER_COUNT = int(
    getattr(
        config,
        "ORDER_COUNT",
        120000,
    )
)

MIN_ORDER_ITEMS = int(
    getattr(
        config,
        "MIN_ORDER_ITEMS",
        200000,
    )
)

PAYMENT_COUNT = int(
    getattr(
        config,
        "PAYMENT_COUNT",
        ORDER_COUNT,
    )
)

DATA_START_DATE = pd.Timestamp(
    getattr(
        config,
        "DATA_START_DATE",
        "2024-01-01",
    )
)

DATA_END_DATE = pd.Timestamp(
    getattr(
        config,
        "DATA_END_DATE",
        "2026-09-25",
    )
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def timestamp_string(
    value: pd.Timestamp,
) -> str:
    """Convert timestamp to YYYY-MM-DD string."""

    return pd.Timestamp(
        value
    ).strftime(
        "%Y-%m-%d"
    )


def random_date(
    start: pd.Timestamp,
    end: pd.Timestamp,
    size: int = 1,
) -> pd.DatetimeIndex:
    """Generate random dates inside inclusive range."""

    start_value = pd.Timestamp(start)
    end_value = pd.Timestamp(end)

    if end_value < start_value:
        raise ValueError(
            "End date cannot be before start date."
        )

    days = (
        end_value - start_value
    ).days

    offsets = np.random.randint(
        0,
        days + 1,
        size=size,
    )

    return pd.DatetimeIndex(
        start_value
        + pd.to_timedelta(
            offsets,
            unit="D",
        )
    )


def weighted_choice(
    values: List[str],
    weights: List[float],
    size: int,
) -> np.ndarray:
    """Weighted random choice."""

    probabilities = np.array(
        weights,
        dtype=float,
    )

    probabilities = (
        probabilities
        / probabilities.sum()
    )

    return np.random.choice(
        values,
        size=size,
        p=probabilities,
    )


def safe_list(
    value,
    default: List[str],
) -> List[str]:
    """Return a list from config or fallback."""

    if value is None:
        return default

    if isinstance(value, (list, tuple)):
        return list(value)

    return default


# ============================================================
# LOCATION DATA
# ============================================================

def generate_locations() -> pd.DataFrame:
    """Generate Indian business locations."""

    configured_locations = getattr(
        config,
        "LOCATION_DATA",
        None,
    )

    rows = []

    if isinstance(
        configured_locations,
        dict,
    ):

        for index, (
            city,
            details,
        ) in enumerate(
            configured_locations.items(),
            start=1,
        ):

            if isinstance(
                details,
                dict,
            ):

                state = details.get(
                    "state",
                    details.get(
                        "State",
                        "Maharashtra",
                    ),
                )

                region = details.get(
                    "region",
                    details.get(
                        "Region",
                        "West",
                    ),
                )

                tier = details.get(
                    "tier",
                    details.get(
                        "Tier",
                        "Tier 2",
                    ),
                )

            else:

                state = "Maharashtra"
                region = "West"
                tier = "Tier 2"

            rows.append(
                {
                    "LocationID": (
                        f"L{index:04d}"
                    ),
                    "City": city,
                    "State": state,
                    "Region": region,
                    "Tier": tier,
                }
            )

    elif isinstance(
        configured_locations,
        list,
    ):

        for index, item in enumerate(
            configured_locations,
            start=1,
        ):

            if isinstance(
                item,
                dict,
            ):

                city = item.get(
                    "city",
                    item.get(
                        "City",
                        f"City{index}",
                    ),
                )

                state = item.get(
                    "state",
                    item.get(
                        "State",
                        "Maharashtra",
                    ),
                )

                region = item.get(
                    "region",
                    item.get(
                        "Region",
                        "West",
                    ),
                )

                tier = item.get(
                    "tier",
                    item.get(
                        "Tier",
                        "Tier 2",
                    ),
                )

                rows.append(
                    {
                        "LocationID": (
                            f"L{index:04d}"
                        ),
                        "City": city,
                        "State": state,
                        "Region": region,
                        "Tier": tier,
                    }
                )

    if not rows:

        fallback = [
            (
                "Mumbai",
                "Maharashtra",
                "West",
                "Tier 1",
            ),
            (
                "Pune",
                "Maharashtra",
                "West",
                "Tier 1",
            ),
            (
                "Nagpur",
                "Maharashtra",
                "West",
                "Tier 2",
            ),
            (
                "Nashik",
                "Maharashtra",
                "West",
                "Tier 2",
            ),
            (
                "Latur",
                "Maharashtra",
                "West",
                "Tier 3",
            ),
            (
                "Hyderabad",
                "Telangana",
                "South",
                "Tier 1",
            ),
            (
                "Warangal",
                "Telangana",
                "South",
                "Tier 2",
            ),
            (
                "Bengaluru",
                "Karnataka",
                "South",
                "Tier 1",
            ),
            (
                "Mysuru",
                "Karnataka",
                "South",
                "Tier 2",
            ),
            (
                "Delhi",
                "Delhi",
                "North",
                "Tier 1",
            ),
            (
                "Chennai",
                "Tamil Nadu",
                "South",
                "Tier 1",
            ),
            (
                "Ahmedabad",
                "Gujarat",
                "West",
                "Tier 1",
            ),
            (
                "Surat",
                "Gujarat",
                "West",
                "Tier 1",
            ),
            (
                "Kolkata",
                "West Bengal",
                "East",
                "Tier 1",
            ),
            (
                "Jaipur",
                "Rajasthan",
                "North",
                "Tier 1",
            ),
            (
                "Indore",
                "Madhya Pradesh",
                "Central",
                "Tier 2",
            ),
            (
                "Bhopal",
                "Madhya Pradesh",
                "Central",
                "Tier 2",
            ),
            (
                "Lucknow",
                "Uttar Pradesh",
                "North",
                "Tier 1",
            ),
            (
                "Kanpur",
                "Uttar Pradesh",
                "North",
                "Tier 2",
            ),
            (
                "Patna",
                "Bihar",
                "East",
                "Tier 2",
            ),
            (
                "Vadodara",
                "Gujarat",
                "West",
                "Tier 2",
            ),
            (
                "Aurangabad",
                "Maharashtra",
                "West",
                "Tier 2",
            ),
        ]

        rows = [
            {
                "LocationID": f"L{i:04d}",
                "City": city,
                "State": state,
                "Region": region,
                "Tier": tier,
            }
            for i, (
                city,
                state,
                region,
                tier,
            ) in enumerate(
                fallback,
                start=1,
            )
        ]

    dataframe = pd.DataFrame(
        rows
    )

    dataframe.to_csv(
        RAW_DIR / "locations.csv",
        index=False,
        encoding="utf-8-sig",
    )

    LOGGER.info(
        "Locations generated: %s",
        len(dataframe),
    )

    return dataframe


# ============================================================
# CUSTOMER GENERATION
# ============================================================

def get_names() -> Tuple[
    List[str],
    List[str],
]:
    """Get first and last names."""

    first_names = safe_list(
        getattr(
            config,
            "FIRST_NAMES",
            None,
        ),
        [
            "Aarav",
            "Aditi",
            "Aditya",
            "Akash",
            "Amit",
            "Ananya",
            "Aniket",
            "Anjali",
            "Arjun",
            "Ayush",
            "Deepak",
            "Divya",
            "Gaurav",
            "Harsh",
            "Isha",
            "Karan",
            "Kavita",
            "Manish",
            "Neha",
            "Nikhil",
            "Pooja",
            "Rahul",
            "Riya",
            "Rohan",
            "Sakshi",
            "Sameer",
            "Sneha",
            "Sonia",
            "Vikas",
            "Vivek",
        ],
    )

    last_names = safe_list(
        getattr(
            config,
            "LAST_NAMES",
            None,
        ),
        [
            "Sharma",
            "Patil",
            "Sawatar",
            "Deshmukh",
            "Jadhav",
            "Pawar",
            "Kulkarni",
            "Joshi",
            "Shinde",
            "More",
            "Kadam",
            "Gaikwad",
            "Chavan",
            "Bhosale",
            "Mane",
            "Yadav",
            "Verma",
            "Gupta",
            "Singh",
            "Khan",
            "Reddy",
            "Rao",
            "Iyer",
            "Nair",
            "Mehta",
            "Shah",
            "Patel",
            "Das",
            "Banerjee",
            "Mishra",
        ],
    )

    return first_names, last_names


def generate_customers(
    locations: pd.DataFrame,
    orders_count: int,
) -> pd.DataFrame:
    """
    Generate customers.

    Important:
    SignupDate is generated BEFORE the customer's first
    potential order date.

    Because orders are generated after customers, customer
    signup dates are initially generated across the complete
    project period and then adjusted after order assignment.
    """

    first_names, last_names = get_names()

    location_indices = np.random.choice(
        len(locations),
        size=CUSTOMER_COUNT,
        replace=True,
    )

    selected_locations = locations.iloc[
        location_indices
    ].reset_index(
        drop=True
    )

    genders = np.random.choice(
        [
            "Male",
            "Female",
            "Other",
        ],
        size=CUSTOMER_COUNT,
        p=[
            0.50,
            0.48,
            0.02,
        ],
    )

    ages = np.random.randint(
        18,
        66,
        size=CUSTOMER_COUNT,
    )

    # Initial signup dates.
    signup_dates = random_date(
        DATA_START_DATE,
        DATA_END_DATE - pd.Timedelta(days=30),
        CUSTOMER_COUNT,
    )

    names = [
        f"{random.choice(first_names)} "
        f"{random.choice(last_names)}"
        for _ in range(CUSTOMER_COUNT)
    ]

    customers = pd.DataFrame(
        {
            "CustomerID": [
                f"C{i:06d}"
                for i in range(
                    1,
                    CUSTOMER_COUNT + 1,
                )
            ],
            "Name": names,
            "Gender": genders,
            "Age": ages,
            "City": selected_locations[
                "City"
            ].values,
            "State": selected_locations[
                "State"
            ].values,
            "SignupDate": signup_dates,
            "CustomerSegment": "New Customer",
        }
    )

    return customers


# ============================================================
# PRODUCT GENERATION
# ============================================================

def generate_products() -> pd.DataFrame:
    """Generate realistic grocery products."""

    categories = safe_list(
        getattr(
            config,
            "CATEGORIES",
            None,
        ),
        [
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
        ],
    )

    brands = safe_list(
        getattr(
            config,
            "BRANDS",
            None,
        ),
        [
            "Amul",
            "Britannia",
            "Tata",
            "Aashirvaad",
            "Fortune",
            "Parle",
            "Nestle",
            "Haldiram's",
            "Dove",
            "Surf Excel",
            "Himalaya",
            "Patanjali",
            "Mother Dairy",
            "Pepsi",
            "Coca-Cola",
        ],
    )

    suppliers = safe_list(
        getattr(
            config,
            "SUPPLIERS",
            None,
        ),
        [
            "FreshMart Suppliers",
            "Metro Wholesale",
            "National Foods Distributor",
            "Shree Ganesh Traders",
            "Prime Grocery Supply",
            "Urban Retail Supply",
            "DailyFresh Distributors",
            "Maharashtra Food Hub",
        ],
    )

    subcategories = {
        "Fresh Fruits": [
            "Apples",
            "Bananas",
            "Mangoes",
            "Oranges",
            "Grapes",
        ],
        "Fresh Vegetables": [
            "Tomatoes",
            "Potatoes",
            "Onions",
            "Leafy Greens",
            "Root Vegetables",
        ],
        "Dairy": [
            "Milk",
            "Curd",
            "Butter",
            "Cheese",
            "Paneer",
        ],
        "Staples": [
            "Rice",
            "Wheat",
            "Flour",
            "Pulses",
            "Cooking Oil",
        ],
        "Snacks": [
            "Biscuits",
            "Chips",
            "Namkeen",
            "Chocolate",
            "Dry Fruits",
        ],
        "Beverages": [
            "Tea",
            "Coffee",
            "Juice",
            "Soft Drinks",
            "Energy Drinks",
        ],
        "Personal Care": [
            "Shampoo",
            "Soap",
            "Toothpaste",
            "Skincare",
            "Hair Care",
        ],
        "Household Cleaning": [
            "Detergent",
            "Dishwash",
            "Floor Cleaner",
            "Toilet Cleaner",
            "Surface Cleaner",
        ],
        "Bakery": [
            "Bread",
            "Cakes",
            "Cookies",
            "Buns",
            "Pastries",
        ],
        "Frozen Foods": [
            "Frozen Vegetables",
            "Frozen Snacks",
            "Ice Cream",
            "Frozen Paneer",
            "Ready Meals",
        ],
        "Baby Care": [
            "Diapers",
            "Baby Food",
            "Baby Soap",
            "Baby Lotion",
            "Baby Wipes",
        ],
        "Other": [
            "Kitchen Items",
            "Pet Care",
            "Stationery",
            "Miscellaneous",
            "Utility",
        ],
    }

    price_ranges = {
        "Fresh Fruits": (
            40,
            500,
        ),
        "Fresh Vegetables": (
            20,
            300,
        ),
        "Dairy": (
            30,
            600,
        ),
        "Staples": (
            50,
            1500,
        ),
        "Snacks": (
            20,
            900,
        ),
        "Beverages": (
            30,
            800,
        ),
        "Personal Care": (
            50,
            1200,
        ),
        "Household Cleaning": (
            60,
            1000,
        ),
        "Bakery": (
            40,
            800,
        ),
        "Frozen Foods": (
            80,
            1000,
        ),
        "Baby Care": (
            80,
            1800,
        ),
        "Other": (
            30,
            1200,
        ),
    }

    rows = []

    for product_number in range(
        1,
        PRODUCT_COUNT + 1,
    ):

        category = random.choice(
            categories
        )

        subcategory = random.choice(
            subcategories.get(
                category,
                ["General"],
            )
        )

        brand = random.choice(
            brands
        )

        supplier = random.choice(
            suppliers
        )

        minimum_price, maximum_price = (
            price_ranges.get(
                category,
                (
                    50,
                    1000,
                ),
            )
        )

        unit_price = round(
            random.uniform(
                minimum_price,
                maximum_price,
            ),
            2,
        )

        margin_percent = random.uniform(
            0.10,
            0.38,
        )

        cost_price = round(
            unit_price
            * (
                1
                - margin_percent
            ),
            2,
        )

        margin = round(
            unit_price
            - cost_price,
            2,
        )

        stock_quantity = random.randint(
            20,
            1000,
        )

        product_name = (
            f"{brand} "
            f"{subcategory} "
            f"{product_number:03d}"
        )

        rows.append(
            {
                "ProductID": (
                    f"P{product_number:04d}"
                ),
                "ProductName": product_name,
                "Category": category,
                "SubCategory": subcategory,
                "Brand": brand,
                "UnitPrice": unit_price,
                "CostPrice": cost_price,
                "Margin": margin,
                "StockQuantity": stock_quantity,
                "Supplier": supplier,
            }
        )

    products = pd.DataFrame(
        rows
    )

    return products


# ============================================================
# CUSTOMER ORDER PROFILE
# ============================================================

def generate_customer_order_profile(
    customers: pd.DataFrame,
) -> np.ndarray:
    """
    Generate order weights.

    Customers receive realistic purchase frequency
    instead of perfectly uniform order counts.
    """

    customer_count = len(
        customers
    )

    weights = np.random.gamma(
        shape=1.8,
        scale=1.0,
        size=customer_count,
    )

    # Small boost for customers in Tier 1 cities.
    tier1_cities = {
        "Mumbai",
        "Pune",
        "Hyderabad",
        "Bengaluru",
        "Delhi",
        "Chennai",
        "Ahmedabad",
        "Kolkata",
        "Jaipur",
    }

    tier_boost = customers[
        "City"
    ].isin(
        tier1_cities
    ).astype(float)

    weights = (
        weights
        * (
            1.0
            + 0.25
            * tier_boost
        )
    )

    return weights / weights.sum()


# ============================================================
# ORDER GENERATION
# ============================================================

def generate_orders(
    customers: pd.DataFrame,
    locations: pd.DataFrame,
) -> Tuple[
    pd.DataFrame,
    Dict[str, pd.Timestamp],
]:
    """
    Generate orders.

    Critical fix:
    OrderDate is generated only between DATA_START_DATE
    and DATA_END_DATE.

    Customer signup dates are later adjusted so that:

        SignupDate <= customer's first OrderDate
    """

    customer_probabilities = (
        generate_customer_order_profile(
            customers
        )
    )

    customer_indices = np.random.choice(
        len(customers),
        size=ORDER_COUNT,
        replace=True,
        p=customer_probabilities,
    )

    selected_customers = customers.iloc[
        customer_indices
    ].reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Generate dates strictly inside configured range.
    # --------------------------------------------------------

    order_dates = random_date(
        DATA_START_DATE,
        DATA_END_DATE,
        ORDER_COUNT,
    )

    # --------------------------------------------------------
    # Sort customer orders by date.
    # This makes first-order calculation deterministic.
    # --------------------------------------------------------

    temporary_orders = pd.DataFrame(
        {
            "CustomerID": selected_customers[
                "CustomerID"
            ].values,
            "OrderDate": order_dates,
        }
    )

    first_order_dates = (
        temporary_orders
        .groupby("CustomerID")[
            "OrderDate"
        ]
        .min()
        .to_dict()
    )

    # --------------------------------------------------------
    # Fix customer signup dates.
    #
    # Signup must be at least 1 day before first order,
    # where possible.
    # --------------------------------------------------------

    for customer_id, first_order in (
        first_order_dates.items()
    ):

        customer_index = customers.index[
            customers["CustomerID"]
            == customer_id
        ]

        if len(customer_index) == 0:
            continue

        first_order = pd.Timestamp(
            first_order
        )

        earliest_signup = DATA_START_DATE

        latest_signup = (
            first_order
            - pd.Timedelta(days=1)
        )

        if latest_signup < earliest_signup:

            signup_date = earliest_signup

        else:

            days_available = (
                latest_signup
                - earliest_signup
            ).days

            random_offset = random.randint(
                0,
                days_available,
            )

            signup_date = (
                earliest_signup
                + pd.Timedelta(
                    days=random_offset
                )
            )

        customers.loc[
            customer_index,
            "SignupDate",
        ] = signup_date

    # --------------------------------------------------------
    # Location mapping
    # --------------------------------------------------------

    customer_location = (
        customers.set_index(
            "CustomerID"
        )[["City", "State"]]
        .to_dict(
            orient="index"
        )
    )

    cities = []
    states = []

    for customer_id in (
        selected_customers[
            "CustomerID"
        ]
    ):

        location = customer_location[
            customer_id
        ]

        cities.append(
            location["City"]
        )

        states.append(
            location["State"]
        )

    # --------------------------------------------------------
    # Order statuses
    # --------------------------------------------------------

    configured_statuses = getattr(
        config,
        "ORDER_STATUS_WEIGHTS",
        None,
    )

    if isinstance(
        configured_statuses,
        dict,
    ):

        status_values = list(
            configured_statuses.keys()
        )

        status_weights = list(
            configured_statuses.values()
        )

    else:

        status_values = [
            "Delivered",
            "Returned",
            "Cancelled",
        ]

        status_weights = [
            0.88,
            0.06,
            0.06,
        ]

    order_statuses = weighted_choice(
        status_values,
        status_weights,
        ORDER_COUNT,
    )

    # --------------------------------------------------------
    # Payment methods
    # --------------------------------------------------------

    configured_payments = getattr(
        config,
        "PAYMENT_METHOD_WEIGHTS",
        None,
    )

    if isinstance(
        configured_payments,
        dict,
    ):

        payment_values = list(
            configured_payments.keys()
        )

        payment_weights = list(
            configured_payments.values()
        )

    else:

        payment_values = [
            "UPI",
            "Credit Card",
            "Debit Card",
            "Cash on Delivery",
            "Net Banking",
            "Wallet",
        ]

        payment_weights = [
            0.40,
            0.20,
            0.15,
            0.12,
            0.08,
            0.05,
        ]

    payment_methods = weighted_choice(
        payment_values,
        payment_weights,
        ORDER_COUNT,
    )

    # --------------------------------------------------------
    # Delivery time
    # --------------------------------------------------------

    delivery_times = []

    return_statuses = []
    cancellation_statuses = []

    for status in order_statuses:

        if status == "Cancelled":

            delivery_times.append(
                np.nan
            )

            return_statuses.append(
                "Not Returned"
            )

            cancellation_statuses.append(
                "Cancelled"
            )

        elif status == "Returned":

            delivery_times.append(
                random.randint(
                    20,
                    180,
                )
            )

            return_statuses.append(
                "Returned"
            )

            cancellation_statuses.append(
                "Not Cancelled"
            )

        else:

            delivery_times.append(
                random.randint(
                    20,
                    180,
                )
            )

            return_statuses.append(
                "Not Returned"
            )

            cancellation_statuses.append(
                "Not Cancelled"
            )

    orders = pd.DataFrame(
        {
            "OrderID": [
                f"O{i:07d}"
                for i in range(
                    1,
                    ORDER_COUNT + 1,
                )
            ],
            "CustomerID": selected_customers[
                "CustomerID"
            ].values,
            "OrderDate": order_dates,
            "City": cities,
            "State": states,
            "PaymentMethod": payment_methods,
            "OrderStatus": order_statuses,
            "DeliveryTime": delivery_times,
            "ReturnStatus": return_statuses,
            "CancellationStatus": (
                cancellation_statuses
            ),
        }
    )

    # --------------------------------------------------------
    # Customer segment based on purchase frequency
    # --------------------------------------------------------

    customer_order_counts = (
        orders.groupby(
            "CustomerID"
        )
        .size()
    )

    segment_map = {}

    for customer_id in customers[
        "CustomerID"
    ]:

        order_count = int(
            customer_order_counts.get(
                customer_id,
                0,
            )
        )

        if order_count >= 15:

            segment = "Loyal Customer"

        elif order_count >= 7:

            segment = "Regular Customer"

        elif order_count >= 2:

            segment = "Occasional Customer"

        else:

            segment = "New Customer"

        segment_map[
            customer_id
        ] = segment

    customers[
        "CustomerSegment"
    ] = customers[
        "CustomerID"
    ].map(
        segment_map
    )

    return (
        orders,
        first_order_dates,
    )


# ============================================================
# ORDER ITEM GENERATION
# ============================================================

def generate_order_items(
    orders: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Generate realistic order line items."""

    product_ids = products[
        "ProductID"
    ].to_numpy()

    product_lookup = products.set_index(
        "ProductID"
    )

    rows = []

    order_item_number = 1

    for order_id in orders[
        "OrderID"
    ]:

        item_count = random.choices(
            population=[
                1,
                2,
                3,
                4,
                5,
                6,
            ],
            weights=[
                0.16,
                0.25,
                0.25,
                0.18,
                0.10,
                0.06,
            ],
            k=1,
        )[0]

        selected_products = np.random.choice(
            product_ids,
            size=item_count,
            replace=False,
        )

        for product_id in selected_products:

            product = product_lookup.loc[
                product_id
            ]

            quantity = random.randint(
                1,
                6,
            )

            unit_price = float(
                product["UnitPrice"]
            )

            revenue = round(
                quantity
                * unit_price,
                2,
            )

            discount_percent = random.choice(
                [
                    0,
                    0,
                    0,
                    5,
                    5,
                    10,
                    10,
                    15,
                    20,
                ]
            )

            discount = round(
                revenue
                * discount_percent
                / 100,
                2,
            )

            category = product[
                "Category"
            ]

            if category in {
                "Fresh Fruits",
                "Fresh Vegetables",
                "Dairy",
            }:

                tax_rate = 0.05

            elif category in {
                "Staples",
                "Baby Care",
            }:

                tax_rate = 0.05

            elif category in {
                "Snacks",
                "Beverages",
                "Bakery",
                "Frozen Foods",
            }:

                tax_rate = 0.12

            else:

                tax_rate = 0.18

            taxable_amount = (
                revenue
                - discount
            )

            tax = round(
                taxable_amount
                * tax_rate,
                2,
            )

            net_revenue = round(
                taxable_amount
                + tax,
                2,
            )

            cost_amount = round(
                quantity
                * float(
                    product["CostPrice"]
                ),
                2,
            )

            rows.append(
                {
                    "OrderItemID": (
                        f"OI{order_item_number:08d}"
                    ),
                    "OrderID": order_id,
                    "ProductID": product_id,
                    "Quantity": quantity,
                    "UnitPrice": unit_price,
                    "Discount": discount,
                    "DiscountPercent": (
                        discount_percent
                    ),
                    "Tax": tax,
                    "TaxRate": tax_rate,
                    "Revenue": revenue,
                    "NetRevenue": net_revenue,
                    "CostAmount": cost_amount,
                }
            )

            order_item_number += 1

    # --------------------------------------------------------
    # Ensure requested minimum.
    #
    # Normal generation is already > 200,000.
    # If configuration changes, we add one extra item to
    # random orders until minimum is satisfied.
    # --------------------------------------------------------

    while len(rows) < MIN_ORDER_ITEMS:

        order = orders.sample(
            n=1
        ).iloc[0]

        product = products.sample(
            n=1
        ).iloc[0]

        quantity = random.randint(
            1,
            4,
        )

        unit_price = float(
            product["UnitPrice"]
        )

        revenue = round(
            quantity
            * unit_price,
            2,
        )

        discount_percent = random.choice(
            [
                0,
                5,
                10,
            ]
        )

        discount = round(
            revenue
            * discount_percent
            / 100,
            2,
        )

        tax_rate = 0.05

        taxable_amount = (
            revenue
            - discount
        )

        tax = round(
            taxable_amount
            * tax_rate,
            2,
        )

        net_revenue = round(
            taxable_amount
            + tax,
            2,
        )

        cost_amount = round(
            quantity
            * float(
                product["CostPrice"]
            ),
            2,
        )

        rows.append(
            {
                "OrderItemID": (
                    f"OI{order_item_number:08d}"
                ),
                "OrderID": order[
                    "OrderID"
                ],
                "ProductID": product[
                    "ProductID"
                ],
                "Quantity": quantity,
                "UnitPrice": unit_price,
                "Discount": discount,
                "DiscountPercent": (
                    discount_percent
                ),
                "Tax": tax,
                "TaxRate": tax_rate,
                "Revenue": revenue,
                "NetRevenue": net_revenue,
                "CostAmount": cost_amount,
            }
        )

        order_item_number += 1

    return pd.DataFrame(
        rows
    )


# ============================================================
# PAYMENT GENERATION
# ============================================================

def generate_payments(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
) -> pd.DataFrame:
    """Generate one payment per order."""

    order_totals = (
        order_items.groupby(
            "OrderID"
        )[
            "NetRevenue"
        ]
        .sum()
        .round(2)
    )

    rows = []

    for index, order in orders.iterrows():

        order_id = order[
            "OrderID"
        ]

        amount = float(
            order_totals.get(
                order_id,
                0.0,
            )
        )

        payment_date = pd.Timestamp(
            order["OrderDate"]
        )

        payment_method = order[
            "PaymentMethod"
        ]

        if order[
            "OrderStatus"
        ] == "Cancelled":

            payment_status = random.choice(
                [
                    "Refunded",
                    "Cancelled",
                ]
            )

        else:

            payment_status = "Completed"

        rows.append(
            {
                "PaymentID": (
                    f"PAY{index + 1:07d}"
                ),
                "OrderID": order_id,
                "PaymentDate": payment_date,
                "PaymentMethod": payment_method,
                "Amount": amount,
                "PaymentStatus": payment_status,
                "TransactionID": (
                    f"TXN"
                    f"{index + 1:010d}"
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# RETURN GENERATION
# ============================================================

def generate_returns(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
) -> pd.DataFrame:
    """Generate return records for returned orders."""

    returned_orders = orders[
        orders["OrderStatus"]
        == "Returned"
    ]

    if returned_orders.empty:

        return pd.DataFrame(
            columns=[
                "ReturnID",
                "OrderID",
                "ReturnDate",
                "ReturnReason",
                "RefundAmount",
                "ReturnStatus",
            ]
        )

    order_totals = (
        order_items.groupby(
            "OrderID"
        )[
            "NetRevenue"
        ]
        .sum()
        .to_dict()
    )

    reasons = [
        "Damaged Product",
        "Wrong Product",
        "Quality Issue",
        "Late Delivery",
        "Product Not Required",
        "Packaging Issue",
        "Customer Changed Mind",
    ]

    rows = []

    for index, order in returned_orders.iterrows():

        order_id = order[
            "OrderID"
        ]

        order_date = pd.Timestamp(
            order["OrderDate"]
        )

        latest_return_date = min(
            order_date
            + pd.Timedelta(
                days=30
            ),
            DATA_END_DATE,
        )

        if latest_return_date < order_date:

            return_date = order_date

        else:

            days = (
                latest_return_date
                - order_date
            ).days

            return_date = (
                order_date
                + pd.Timedelta(
                    days=random.randint(
                        1,
                        max(
                            1,
                            days,
                        ),
                    )
                )
            )

        refund_amount = round(
            float(
                order_totals.get(
                    order_id,
                    0.0,
                )
            ),
            2,
        )

        rows.append(
            {
                "ReturnID": (
                    f"RET{len(rows) + 1:06d}"
                ),
                "OrderID": order_id,
                "ReturnDate": return_date,
                "ReturnReason": random.choice(
                    reasons
                ),
                "RefundAmount": refund_amount,
                "ReturnStatus": "Returned",
            }
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# DELIVERY GENERATION
# ============================================================

def generate_deliveries(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Generate delivery records."""

    partners = [
        "QuickCart Logistics",
        "Delhivery",
        "Ecom Express",
        "Shadowfax",
        "XpressBees",
    ]

    rows = []

    for index, order in orders.iterrows():

        order_id = order[
            "OrderID"
        ]

        order_date = pd.Timestamp(
            order["OrderDate"]
        )

        status = order[
            "OrderStatus"
        ]

        if status == "Cancelled":

            delivery_status = "Cancelled"
            delivery_time = np.nan
            target_time = np.nan
            delivered_at = pd.NaT

        else:

            target_time = random.choice(
                [
                    30,
                    45,
                    60,
                    90,
                    120,
                    180,
                ]
            )

            delivery_time = max(
                15,
                int(
                    np.random.normal(
                        target_time,
                        max(
                            10,
                            target_time
                            * 0.20,
                        ),
                    )
                ),
            )

            delivery_time = min(
                delivery_time,
                360,
            )

            if (
                delivery_time
                <= target_time
            ):

                delivery_status = (
                    "Delivered On Time"
                )

            else:

                delivery_status = (
                    "Delivered Late"
                )

            delivered_at = (
                order_date
                + pd.Timedelta(
                    minutes=delivery_time
                )
            )

        rows.append(
            {
                "DeliveryID": (
                    f"DEL{index + 1:07d}"
                ),
                "OrderID": order_id,
                "DeliveryPartner": random.choice(
                    partners
                ),
                "DeliveryStatus": delivery_status,
                "DeliveryTimeMinutes": delivery_time,
                "TargetDeliveryMinutes": target_time,
                "DeliveredAt": delivered_at,
            }
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# INVENTORY GENERATION
# ============================================================

def generate_inventory(
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Generate periodic product inventory snapshots."""

    snapshot_dates = pd.date_range(
        DATA_START_DATE,
        DATA_END_DATE,
        freq="MS",
    )

    if len(snapshot_dates) == 0:

        snapshot_dates = pd.DatetimeIndex(
            [
                DATA_START_DATE
            ]
        )

    rows = []

    inventory_number = 1

    for snapshot_date in snapshot_dates:

        for _, product in products.iterrows():

            opening_stock = random.randint(
                20,
                1000,
            )

            received_quantity = random.randint(
                0,
                500,
            )

            sold_quantity = random.randint(
                0,
                min(
                    opening_stock
                    + received_quantity,
                    500,
                ),
            )

            closing_stock = max(
                0,
                opening_stock
                + received_quantity
                - sold_quantity,
            )

            unit_cost = float(
                product["CostPrice"]
            )

            inventory_value = round(
                closing_stock
                * unit_cost,
                2,
            )

            if closing_stock == 0:

                inventory_status = (
                    "Stock-Out"
                )

            elif closing_stock <= 25:

                inventory_status = (
                    "Low Stock"
                )

            else:

                inventory_status = (
                    "Healthy"
                )

            rows.append(
                {
                    "InventoryID": (
                        f"INV{inventory_number:08d}"
                    ),
                    "SnapshotDate": snapshot_date,
                    "ProductID": product[
                        "ProductID"
                    ],
                    "OpeningStock": opening_stock,
                    "ReceivedQuantity": received_quantity,
                    "SoldQuantity": sold_quantity,
                    "ClosingStock": closing_stock,
                    "UnitCost": unit_cost,
                    "InventoryValue": inventory_value,
                    "InventoryStatus": inventory_status,
                }
            )

            inventory_number += 1

    return pd.DataFrame(
        rows
    )


# ============================================================
# DATE DIMENSION
# ============================================================

def generate_date_dimension() -> pd.DataFrame:
    """Generate Power BI date dimension."""

    dates = pd.date_range(
        DATA_START_DATE,
        DATA_END_DATE,
        freq="D",
    )

    dataframe = pd.DataFrame(
        {
            "DateKey": (
                dates.strftime(
                    "%Y%m%d"
                ).astype(int)
            ),
            "Date": dates,
            "Year": dates.year,
            "Quarter": (
                "Q"
                + dates.quarter.astype(str)
            ),
            "MonthNumber": dates.month,
            "MonthName": dates.month_name(),
            "MonthShort": dates.strftime(
                "%b"
            ),
            "WeekNumber": (
                dates.isocalendar()
                .week
                .astype(int)
            ),
            "DayOfMonth": dates.day,
            "DayName": dates.day_name(),
            "DayOfWeek": (
                dates.dayofweek + 1
            ),
            "IsWeekend": (
                dates.dayofweek >= 5
            ),
        }
    )

    return dataframe


# ============================================================
# DATA VALIDATION BEFORE SAVE
# ============================================================

def validate_generated_data(
    locations: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    payments: pd.DataFrame,
    returns: pd.DataFrame,
    deliveries: pd.DataFrame,
    inventory: pd.DataFrame,
    date_dimension: pd.DataFrame,
) -> None:
    """Validate generated data before writing files."""

    LOGGER.info(
        "Running pre-save generator validation."
    )

    # --------------------------------------------------------
    # Required counts
    # --------------------------------------------------------

    if len(customers) < CUSTOMER_COUNT:
        raise ValueError(
            "Customer count is below configured requirement."
        )

    if len(products) < PRODUCT_COUNT:
        raise ValueError(
            "Product count is below configured requirement."
        )

    if len(orders) < ORDER_COUNT:
        raise ValueError(
            "Order count is below configured requirement."
        )

    if len(order_items) < MIN_ORDER_ITEMS:
        raise ValueError(
            "Order item count is below configured requirement."
        )

    # --------------------------------------------------------
    # Order date range
    # --------------------------------------------------------

    order_dates = pd.to_datetime(
        orders["OrderDate"]
    )

    outside_range = (
        (order_dates < DATA_START_DATE)
        | (order_dates > DATA_END_DATE)
    )

    outside_count = int(
        outside_range.sum()
    )

    if outside_count > 0:

        raise ValueError(
            f"{outside_count} orders have "
            f"dates outside configured range."
        )

    # --------------------------------------------------------
    # Signup before order
    # --------------------------------------------------------

    customer_dates = (
        customers.set_index(
            "CustomerID"
        )[
            "SignupDate"
        ]
    )

    merged = orders[
        [
            "CustomerID",
            "OrderDate",
        ]
    ].copy()

    merged[
        "SignupDate"
    ] = merged[
        "CustomerID"
    ].map(
        customer_dates
    )

    invalid_signup = (
        merged["SignupDate"]
        > merged["OrderDate"]
    )

    invalid_signup_count = int(
        invalid_signup.sum()
    )

    if invalid_signup_count > 0:

        raise ValueError(
            f"{invalid_signup_count} orders occur "
            f"before customer signup."
        )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    expected_revenue = (
        order_items["Quantity"]
        * order_items["UnitPrice"]
    ).round(2)

    actual_revenue = (
        order_items["Revenue"]
        .round(2)
    )

    revenue_errors = int(
        (
            (
                expected_revenue
                - actual_revenue
            ).abs()
            > 0.05
        ).sum()
    )

    if revenue_errors > 0:

        raise ValueError(
            f"{revenue_errors} order-item "
            f"revenue calculations are invalid."
        )

    # --------------------------------------------------------
    # Net revenue
    # --------------------------------------------------------

    expected_net = (
        order_items["Revenue"]
        - order_items["Discount"]
        + order_items["Tax"]
    ).round(2)

    actual_net = (
        order_items["NetRevenue"]
        .round(2)
    )

    net_errors = int(
        (
            (
                expected_net
                - actual_net
            ).abs()
            > 0.05
        ).sum()
    )

    if net_errors > 0:

        raise ValueError(
            f"{net_errors} NetRevenue calculations "
            f"are invalid."
        )

    # --------------------------------------------------------
    # Foreign keys
    # --------------------------------------------------------

    valid_customers = set(
        customers["CustomerID"]
    )

    invalid_order_customers = (
        ~orders["CustomerID"]
        .isin(valid_customers)
    )

    if invalid_order_customers.any():

        raise ValueError(
            "Orders contain invalid CustomerID values."
        )

    valid_orders = set(
        orders["OrderID"]
    )

    invalid_item_orders = (
        ~order_items["OrderID"]
        .isin(valid_orders)
    )

    if invalid_item_orders.any():

        raise ValueError(
            "Order items contain invalid OrderID values."
        )

    valid_products = set(
        products["ProductID"]
    )

    invalid_item_products = (
        ~order_items["ProductID"]
        .isin(valid_products)
    )

    if invalid_item_products.any():

        raise ValueError(
            "Order items contain invalid ProductID values."
        )

    # --------------------------------------------------------
    # Payment coverage
    # --------------------------------------------------------

    if payments["OrderID"].nunique() != orders[
        "OrderID"
    ].nunique():

        raise ValueError(
            "Payment coverage does not match order coverage."
        )

    # --------------------------------------------------------
    # Delivery coverage
    # --------------------------------------------------------

    if deliveries["OrderID"].nunique() != orders[
        "OrderID"
    ].nunique():

        raise ValueError(
            "Delivery coverage does not match order coverage."
        )

    # --------------------------------------------------------
    # Return status
    # --------------------------------------------------------

    returned_order_ids = set(
        orders.loc[
            orders["OrderStatus"]
            == "Returned",
            "OrderID",
        ]
    )

    return_order_ids = set(
        returns["OrderID"]
    )

    if not return_order_ids.issubset(
        returned_order_ids
    ):

        raise ValueError(
            "Return records contain orders "
            "that are not marked Returned."
        )

    # --------------------------------------------------------
    # Inventory
    # --------------------------------------------------------

    expected_inventory = (
        inventory["ClosingStock"]
        * inventory["UnitCost"]
    ).round(2)

    actual_inventory = (
        inventory["InventoryValue"]
        .round(2)
    )

    inventory_errors = int(
        (
            (
                expected_inventory
                - actual_inventory
            ).abs()
            > 0.05
        ).sum()
    )

    if inventory_errors > 0:

        raise ValueError(
            f"{inventory_errors} inventory value "
            f"calculations are invalid."
        )

    LOGGER.info(
        "Pre-save validation PASSED."
    )


# ============================================================
# SAVE DATASETS
# ============================================================

def save_datasets(
    locations: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    payments: pd.DataFrame,
    returns: pd.DataFrame,
    deliveries: pd.DataFrame,
    inventory: pd.DataFrame,
    date_dimension: pd.DataFrame,
) -> None:
    """Save raw and date data."""

    datasets = {
        "locations.csv": locations,
        "customers.csv": customers,
        "products.csv": products,
        "orders.csv": orders,
        "order_items.csv": order_items,
        "payments.csv": payments,
        "returns.csv": returns,
        "deliveries.csv": deliveries,
        "inventory.csv": inventory,
    }

    for filename, dataframe in datasets.items():

        path = RAW_DIR / filename

        dataframe.to_csv(
            path,
            index=False,
            encoding="utf-8-sig",
        )

        LOGGER.info(
            "Saved %-20s %10s rows",
            filename,
            f"{len(dataframe):,}",
        )

    date_dimension.to_csv(
        PROCESSED_DIR
        / "dim_date.csv",
        index=False,
        encoding="utf-8-sig",
    )

    LOGGER.info(
        "Saved %-20s %10s rows",
        "dim_date.csv",
        f"{len(date_dimension):,}",
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def generate_all_data() -> Dict[str, pd.DataFrame]:
    """Run complete QuickCart data generation."""

    print()
    print("=" * 90)
    print(" QUICKCART - REALISTIC E-COMMERCE DATA GENERATOR")
    print("=" * 90)

    print(
        f"\nSeed       : {SEED}"
    )

    print(
        f"Date range : "
        f"{timestamp_string(DATA_START_DATE)} "
        f"to "
        f"{timestamp_string(DATA_END_DATE)}"
    )

    print()

    # --------------------------------------------------------
    # 1. Locations
    # --------------------------------------------------------

    print(
        "[1/9] Generating locations..."
    )

    locations = generate_locations()

    # --------------------------------------------------------
    # 2. Customers
    # --------------------------------------------------------

    print(
        "[2/9] Generating customers..."
    )

    customers = generate_customers(
        locations,
        ORDER_COUNT,
    )

    # --------------------------------------------------------
    # 3. Products
    # --------------------------------------------------------

    print(
        "[3/9] Generating products..."
    )

    products = generate_products()

    # --------------------------------------------------------
    # 4. Orders
    # --------------------------------------------------------

    print(
        "[4/9] Generating orders..."
    )

    orders, first_order_dates = (
        generate_orders(
            customers,
            locations,
        )
    )

    # --------------------------------------------------------
    # 5. Order items
    # --------------------------------------------------------

    print(
        "[5/9] Generating order items..."
    )

    order_items = generate_order_items(
        orders,
        products,
    )

    # --------------------------------------------------------
    # 6. Payments
    # --------------------------------------------------------

    print(
        "[6/9] Generating payments..."
    )

    payments = generate_payments(
        orders,
        order_items,
    )

    # --------------------------------------------------------
    # 7. Returns + deliveries
    # --------------------------------------------------------

    print(
        "[7/9] Generating returns and deliveries..."
    )

    returns = generate_returns(
        orders,
        order_items,
    )

    deliveries = generate_deliveries(
        orders
    )

    # --------------------------------------------------------
    # 8. Inventory
    # --------------------------------------------------------

    print(
        "[8/9] Generating inventory..."
    )

    inventory = generate_inventory(
        products
    )

    # --------------------------------------------------------
    # 9. Date dimension
    # --------------------------------------------------------

    print(
        "[9/9] Generating date dimension..."
    )

    date_dimension = (
        generate_date_dimension()
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    print()
    print(
        "Running generator validation..."
    )

    validate_generated_data(
        locations,
        customers,
        products,
        orders,
        order_items,
        payments,
        returns,
        deliveries,
        inventory,
        date_dimension,
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    print(
        "\nSaving datasets..."
    )

    save_datasets(
        locations,
        customers,
        products,
        orders,
        order_items,
        payments,
        returns,
        deliveries,
        inventory,
        date_dimension,
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print()
    print("=" * 90)
    print(" DATA GENERATION COMPLETED SUCCESSFULLY")
    print("=" * 90)

    print(
        f"Locations       : {len(locations):,}"
    )

    print(
        f"Customers       : {len(customers):,}"
    )

    print(
        f"Products        : {len(products):,}"
    )

    print(
        f"Orders          : {len(orders):,}"
    )

    print(
        f"Order Items     : {len(order_items):,}"
    )

    print(
        f"Payments        : {len(payments):,}"
    )

    print(
        f"Returns         : {len(returns):,}"
    )

    print(
        f"Deliveries      : {len(deliveries):,}"
    )

    print(
        f"Inventory       : {len(inventory):,}"
    )

    print(
        f"Date Dimension  : {len(date_dimension):,}"
    )

    print()
    print(
        "RAW DATA:"
    )

    print(
        f"  {RAW_DIR}"
    )

    print(
        "PROCESSED DATA:"
    )

    print(
        f"  {PROCESSED_DIR}"
    )

    print("=" * 90)

    LOGGER.info(
        "QuickCart data generation completed successfully."
    )

    return {
        "locations": locations,
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
        "returns": returns,
        "deliveries": deliveries,
        "inventory": inventory,
        "dim_date": date_dimension,
    }


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

generate_data = generate_all_data
run = generate_all_data
main = generate_all_data


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    try:

        generate_all_data()

    except Exception as exc:

        LOGGER.exception(
            "QuickCart data generation failed: %s",
            exc,
        )

        print()
        print("=" * 90)
        print(" DATA GENERATION FAILED")
        print("=" * 90)
        print(
            f"Error: {exc}"
        )
        print("=" * 90)

        raise