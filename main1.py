"""
QUICKCART – E-COMMERCE / GROCERY SALES & CUSTOMER INTELLIGENCE PLATFORM

Master Automation / Project Orchestrator

Run:
    python main.py

This file coordinates the complete QuickCart project pipeline:

1. Python version check
2. Dependency check / installation
3. Folder creation
4. Data generation
5. Data cleaning
6. Data validation
7. Database creation
8. Data loading
9. Analytics
10. RFM segmentation
11. Inventory analysis
12. Delivery analysis
13. CSV / Excel exports
14. SQL scripts
15. Power BI documentation
16. Dashboard generation
17. README generation
18. Resume project description
19. Final project completion report
"""

from __future__ import annotations

import importlib
import logging
import os
import platform
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_NAME = "QUICKCART – E-COMMERCE / GROCERY SALES & CUSTOMER INTELLIGENCE PLATFORM"
PROJECT_VERSION = "1.0.0"

MIN_PYTHON = (3, 10)

BASE_DIR = Path(__file__).resolve().parent

SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

DATABASE_DIR = BASE_DIR / "database"
POWERBI_DIR = BASE_DIR / "powerbi"
REPORTS_DIR = BASE_DIR / "reports"
DASHBOARD_DIR = BASE_DIR / "dashboard"
LOGS_DIR = BASE_DIR / "logs"

REQUIRED_DIRECTORIES = [
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
# REQUIRED PYTHON PACKAGES
# ============================================================

REQUIRED_PACKAGES: Dict[str, str] = {
    "pandas": "pandas>=2.0",
    "numpy": "numpy>=1.24",
    "openpyxl": "openpyxl>=3.1",
    "matplotlib": "matplotlib>=3.7",
    "plotly": "plotly>=5.15",
    "mysql.connector": "mysql-connector-python>=8.0",
}


# ============================================================
# LOGGER
# ============================================================

LOGGER: Optional[logging.Logger] = None


def setup_logging() -> logging.Logger:
    """
    Configure project logging.

    Logs are written to:
        logs/quickcart.log
    """

    global LOGGER

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("QuickCart")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers when main.py is executed/imported repeatedly.
    if logger.handlers:
        LOGGER = logger
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(
        LOGS_DIR / "quickcart.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    LOGGER = logger

    return logger


# ============================================================
# DISPLAY HELPERS
# ============================================================

def print_banner() -> None:
    """Print QuickCart startup banner."""

    print()
    print("=" * 90)
    print(" QUICKCART")
    print(" E-COMMERCE / GROCERY SALES & CUSTOMER INTELLIGENCE PLATFORM")
    print("=" * 90)
    print(f" Version       : {PROJECT_VERSION}")
    print(f" Python        : {platform.python_version()}")
    print(f" Operating Sys : {platform.system()} {platform.release()}")
    print(f" Project Path  : {BASE_DIR}")
    print("=" * 90)
    print()


def print_section(title: str) -> None:
    """Print a formatted pipeline section."""

    print()
    print("-" * 90)
    print(f" {title}")
    print("-" * 90)


def print_success(message: str) -> None:
    print(f"  [SUCCESS] {message}")


def print_warning(message: str) -> None:
    print(f"  [WARNING] {message}")


def print_error(message: str) -> None:
    print(f"  [ERROR] {message}")


# ============================================================
# PYTHON VERSION
# ============================================================

def check_python_version() -> bool:
    """
    Check whether the installed Python version meets
    the minimum project requirement.
    """

    print_section("1. PYTHON VERSION CHECK")

    current_version = sys.version_info[:2]

    print(
        f"  Required Python : {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+"
    )
    print(
        f"  Current Python  : {current_version[0]}.{current_version[1]}"
    )

    if current_version < MIN_PYTHON:
        print_error(
            "Python version is too old for QuickCart."
        )

        if LOGGER:
            LOGGER.error(
                "Python version %s.%s is below required %s.%s.",
                current_version[0],
                current_version[1],
                MIN_PYTHON[0],
                MIN_PYTHON[1],
            )

        return False

    print_success("Python version is compatible.")

    if LOGGER:
        LOGGER.info(
            "Python version verified: %s",
            platform.python_version(),
        )

    return True


# ============================================================
# PACKAGE MANAGEMENT
# ============================================================

def is_package_installed(import_name: str) -> bool:
    """Check whether a Python package/module can be imported."""

    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False


def install_package(package_spec: str) -> bool:
    """
    Install a missing package using the same Python interpreter
    that is executing this project.
    """

    print(f"  Installing: {package_spec}")

    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        package_spec,
    ]

    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print_success(f"Installed {package_spec}.")
            return True

        print_warning(
            f"Could not automatically install {package_spec}."
        )

        if result.stderr:
            print(result.stderr.strip())

        return False

    except Exception as exc:
        print_warning(
            f"Package installation failed for {package_spec}: {exc}"
        )
        return False


def check_and_install_dependencies() -> bool:
    """
    Check all required Python dependencies.

    Missing packages are automatically installed where possible.
    """

    print_section("2. DEPENDENCY CHECK")

    installation_failures: List[str] = []

    for import_name, package_spec in REQUIRED_PACKAGES.items():

        if is_package_installed(import_name):
            print_success(f"{package_spec} is available.")
            continue

        print_warning(
            f"{package_spec} is missing."
        )

        installed = install_package(package_spec)

        if not installed:
            installation_failures.append(package_spec)

    if installation_failures:

        print_error("Some required packages could not be installed:")

        for package in installation_failures:
            print(f"    - {package}")

        print()
        print(
            "  Please install the missing packages manually and run main.py again."
        )

        if LOGGER:
            LOGGER.error(
                "Dependency installation failures: %s",
                installation_failures,
            )

        return False

    print_success("All required Python dependencies are available.")

    if LOGGER:
        LOGGER.info("Dependency verification completed successfully.")

    return True


# ============================================================
# FOLDER CREATION
# ============================================================

def create_project_directories() -> bool:
    """Create the complete QuickCart directory structure."""

    print_section("3. PROJECT DIRECTORY SETUP")

    try:
        for directory in REQUIRED_DIRECTORIES:
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            print_success(
                f"Directory ready: {directory.relative_to(BASE_DIR)}"
            )

        if LOGGER:
            LOGGER.info(
                "All project directories created successfully."
            )

        return True

    except Exception as exc:

        print_error(
            f"Could not create project directories: {exc}"
        )

        if LOGGER:
            LOGGER.exception(
                "Directory creation failed."
            )

        return False


# ============================================================
# MODULE VALIDATION
# ============================================================

PIPELINE_MODULES = [
    ("data_generator", "Data generation"),
    ("data_cleaning", "Data cleaning"),
    ("data_validation", "Data validation"),
    ("database", "Database creation and loading"),
    ("analytics", "Business analytics"),
    ("rfm_segmentation", "RFM customer segmentation"),
    ("inventory_analysis", "Inventory analysis"),
    ("delivery_analysis", "Delivery analysis"),
    ("export_data", "CSV / Excel export"),
]


def verify_pipeline_modules() -> bool:
    """
    Verify that every required source module exists.

    This allows main.py to provide a clear error instead of
    producing an unclear ModuleNotFoundError.
    """

    print_section("4. PIPELINE MODULE CHECK")

    missing_modules: List[str] = []

    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    for module_name, description in PIPELINE_MODULES:

        module_file = SRC_DIR / f"{module_name}.py"

        if not module_file.exists():
            missing_modules.append(
                f"{module_name}.py ({description})"
            )
            print_warning(
                f"Missing: src/{module_name}.py"
            )
            continue

        try:
            importlib.util.spec_from_file_location(
                module_name,
                module_file,
            )

            print_success(
                f"Found: src/{module_name}.py"
            )

        except Exception as exc:
            print_warning(
                f"Could not inspect {module_name}.py: {exc}"
            )
            missing_modules.append(
                f"{module_name}.py ({description})"
            )

    if missing_modules:

        print()
        print_warning(
            "The project is being built file-by-file."
        )
        print(
            "  main.py is ready, but the remaining source files "
            "must be created before the complete pipeline can run."
        )

        for module in missing_modules:
            print(f"    - {module}")

        if LOGGER:
            LOGGER.warning(
                "Missing pipeline modules: %s",
                missing_modules,
            )

        return False

    print_success(
        "All QuickCart pipeline modules are present."
    )

    return True


# ============================================================
# MODULE LOADING
# ============================================================

def load_module(module_name: str) -> Any:
    """
    Dynamically import a module from src/.
    """

    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    return importlib.import_module(module_name)


# ============================================================
# FUNCTION RESOLUTION
# ============================================================

def resolve_function(
    module: Any,
    possible_names: List[str],
) -> Optional[Callable[..., Any]]:
    """
    Find a callable from a list of accepted function names.

    This makes the orchestrator flexible while maintaining
    a clearly defined project pipeline.
    """

    for name in possible_names:

        candidate = getattr(module, name, None)

        if callable(candidate):
            return candidate

    return None


def run_module_stage(
    module_name: str,
    description: str,
    function_names: List[str],
) -> Any:
    """
    Import a module and execute its main pipeline function.
    """

    print_section(description.upper())

    try:

        module = load_module(module_name)

        function = resolve_function(
            module,
            function_names,
        )

        if function is None:

            raise AttributeError(
                f"No supported execution function was found in "
                f"src/{module_name}.py. "
                f"Expected one of: {', '.join(function_names)}"
            )

        if LOGGER:
            LOGGER.info(
                "Starting stage: %s",
                description,
            )

        result = function()

        print_success(
            f"{description} completed."
        )

        if LOGGER:
            LOGGER.info(
                "Completed stage: %s",
                description,
            )

        return result

    except Exception as exc:

        print_error(
            f"{description} failed: {exc}"
        )

        if LOGGER:
            LOGGER.exception(
                "Stage failed: %s",
                description,
            )

        raise


# ============================================================
# PROJECT PIPELINE
# ============================================================

def run_pipeline() -> Dict[str, Any]:
    """
    Execute the complete QuickCart analytics pipeline.

    The individual source files will contain the actual
    implementation logic.
    """

    pipeline_results: Dict[str, Any] = {}

    # --------------------------------------------------------
    # DATA GENERATION
    # --------------------------------------------------------

    pipeline_results["data_generation"] = run_module_stage(
        module_name="data_generator",
        description="5. REALISTIC BUSINESS DATA GENERATION",
        function_names=[
            "generate_all_data",
            "generate_data",
            "run",
            "main",
        ],
    )

    # --------------------------------------------------------
    # DATA CLEANING
    # --------------------------------------------------------

    pipeline_results["data_cleaning"] = run_module_stage(
        module_name="data_cleaning",
        description="6. DATA CLEANING",
        function_names=[
            "clean_all_data",
            "clean_data",
            "run",
            "main",
        ],
    )

    # --------------------------------------------------------
    # DATA VALIDATION
    # --------------------------------------------------------

    pipeline_results["data_validation"] = run_module_stage(
        module_name="data_validation",
        description="7. DATA VALIDATION",
        function_names=[
            "validate_all_data",
            "validate_data",
            "run_validation",
            "run",
            "main",
        ],
    )

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    pipeline_results["database"] = run_module_stage(
        module_name="database",
        description="8. SQL DATABASE CREATION & DATA LOADING",
        function_names=[
            "setup_database",
            "create_database",
            "initialize_database",
            "run",
            "main",
        ],
    )

    # --------------------------------------------------------
    # ANALYTICS
    # --------------------------------------------------------

    pipeline_results["analytics"] = run_module_stage(
        module_name="analytics",
        description="9. BUSINESS ANALYTICS",
        function_names=[
            "run_analytics",
            "calculate_analytics",
            "generate_analytics",
            "run",
            "main",
        ],
    )

    # --------------------------------------------------------
    # RFM
    # --------------------------------------------------------

    pipeline_results["rfm"] = run_module_stage(
        module_name="rfm_segmentation",
        description="10. RFM CUSTOMER SEGMENTATION",
        function_names=[
            "run_rfm_analysis",
            "perform_rfm_analysis",
            "calculate_rfm",
            "run",
            "main",
        ],
    )

    # --------------------------------------------------------
    # INVENTORY
    # --------------------------------------------------------

    pipeline_results["inventory"] = run_module_stage(
        module_name="inventory_analysis",
        description="11. INVENTORY ANALYSIS",
        function_names=[
            "run_inventory_analysis",
            "analyze_inventory",
            "calculate_inventory_metrics",
            "run",
            "main",
        ],
    )

    # --------------------------------------------------------
    # DELIVERY
    # --------------------------------------------------------

    pipeline_results["delivery"] = run_module_stage(
        module_name="delivery_analysis",
        description="12. DELIVERY ANALYSIS",
        function_names=[
            "run_delivery_analysis",
            "analyze_delivery",
            "calculate_delivery_metrics",
            "run",
            "main",
        ],
    )

    # --------------------------------------------------------
    # EXPORT
    # --------------------------------------------------------

    pipeline_results["exports"] = run_module_stage(
        module_name="export_data",
        description="13. CSV / EXCEL / POWER BI EXPORT",
        function_names=[
            "export_all",
            "export_data",
            "generate_exports",
            "run",
            "main",
        ],
    )

    return pipeline_results


# ============================================================
# PROJECT ARTIFACT VERIFICATION
# ============================================================

EXPECTED_OUTPUTS = [
    BASE_DIR / "database" / "schema.sql",
    BASE_DIR / "database" / "seed.sql",

    BASE_DIR / "powerbi" / "DAX_Measures.txt",
    BASE_DIR / "powerbi" / "PowerBI_Data_Model.txt",
    BASE_DIR / "powerbi" / "Dashboard_Design.txt",

    BASE_DIR / "reports" / "executive_summary.csv",
    BASE_DIR / "reports" / "category_analysis.csv",
    BASE_DIR / "reports" / "city_analysis.csv",
    BASE_DIR / "reports" / "state_analysis.csv",
    BASE_DIR / "reports" / "customer_segments.csv",
    BASE_DIR / "reports" / "product_analysis.csv",
    BASE_DIR / "reports" / "payment_analysis.csv",
    BASE_DIR / "reports" / "inventory_analysis.csv",
    BASE_DIR / "reports" / "delivery_analysis.csv",

    BASE_DIR / "dashboard" / "dashboard.html",

    BASE_DIR / "README.md",
    BASE_DIR / "resume_project_description.txt",
]


def verify_project_outputs() -> Dict[str, List[str]]:
    """
    Verify generated project artifacts.
    """

    print_section("14. FINAL PROJECT ARTIFACT VERIFICATION")

    generated: List[str] = []
    missing: List[str] = []

    for file_path in EXPECTED_OUTPUTS:

        relative_path = str(
            file_path.relative_to(BASE_DIR)
        )

        if file_path.exists() and file_path.stat().st_size > 0:

            generated.append(relative_path)

            print_success(
                f"Generated: {relative_path}"
            )

        else:

            missing.append(relative_path)

            print_warning(
                f"Missing or empty: {relative_path}"
            )

    return {
        "generated": generated,
        "missing": missing,
    }


# ============================================================
# DATA DIRECTORY SUMMARY
# ============================================================

def collect_file_summary() -> Dict[str, int]:
    """
    Count generated files by project area.
    """

    summary: Dict[str, int] = {}

    directories = {
        "raw_data": RAW_DATA_DIR,
        "processed_data": PROCESSED_DATA_DIR,
        "database": DATABASE_DIR,
        "powerbi": POWERBI_DIR,
        "reports": REPORTS_DIR,
        "dashboard": DASHBOARD_DIR,
        "logs": LOGS_DIR,
    }

    for name, directory in directories.items():

        if not directory.exists():
            summary[name] = 0
            continue

        summary[name] = sum(
            1
            for path in directory.rglob("*")
            if path.is_file()
        )

    return summary


# ============================================================
# FINAL COMPLETION REPORT
# ============================================================

def print_final_report(
    pipeline_results: Dict[str, Any],
    verification: Dict[str, List[str]],
    elapsed_seconds: float,
) -> None:
    """
    Print a professional project completion report.
    """

    print()
    print("=" * 90)
    print(" QUICKCART PROJECT COMPLETION REPORT")
    print("=" * 90)

    print(f" Project             : QUICKCART")
    print(f" Version             : {PROJECT_VERSION}")
    print(f" Execution Time      : {elapsed_seconds:.2f} seconds")
    print(f" Project Directory   : {BASE_DIR}")

    print()
    print("PIPELINE STATUS")
    print("-" * 90)

    stage_names = [
        ("data_generation", "Realistic data generation"),
        ("data_cleaning", "Data cleaning"),
        ("data_validation", "Data validation"),
        ("database", "SQL database"),
        ("analytics", "Business analytics"),
        ("rfm", "RFM customer segmentation"),
        ("inventory", "Inventory analytics"),
        ("delivery", "Delivery analytics"),
        ("exports", "CSV / Excel / Power BI exports"),
    ]

    for key, label in stage_names:

        if key in pipeline_results:
            print(f"  [OK] {label}")
        else:
            print(f"  [--] {label}")

    print()
    print("OUTPUT VERIFICATION")
    print("-" * 90)

    print(
        f"  Generated artifacts : "
        f"{len(verification['generated'])}"
    )

    print(
        f"  Missing artifacts   : "
        f"{len(verification['missing'])}"
    )

    if verification["missing"]:

        print()
        print("  Missing files:")

        for file_name in verification["missing"]:
            print(f"    - {file_name}")

    else:

        print()
        print_success(
            "All expected project artifacts are available."
        )

    print()
    print("PROJECT FILE COUNTS")
    print("-" * 90)

    summary = collect_file_summary()

    for area, count in summary.items():
        print(f"  {area:<20}: {count}")

    print()
    print("IMPORTANT PROJECT OUTPUTS")
    print("-" * 90)

    print("  SQL Schema:")
    print(f"    {DATABASE_DIR / 'schema.sql'}")

    print("  SQL Seed:")
    print(f"    {DATABASE_DIR / 'seed.sql'}")

    print("  Power BI DAX:")
    print(f"    {POWERBI_DIR / 'DAX_Measures.txt'}")

    print("  Power BI Model:")
    print(f"    {POWERBI_DIR / 'PowerBI_Data_Model.txt'}")

    print("  Dashboard Preview:")
    print(f"    {DASHBOARD_DIR / 'dashboard.html'}")

    print("  README:")
    print(f"    {BASE_DIR / 'README.md'}")

    print("  Resume Description:")
    print(f"    {BASE_DIR / 'resume_project_description.txt'}")

    print()
    print("=" * 90)

    if not verification["missing"]:
        print(
            " QUICKCART BUILD STATUS: COMPLETE"
        )
    else:
        print(
            " QUICKCART BUILD STATUS: COMPLETED WITH WARNINGS"
        )

    print("=" * 90)
    print()


# ============================================================
# ERROR REPORT
# ============================================================

def print_failure_report(
    exc: BaseException,
    elapsed_seconds: float,
) -> None:
    """
    Print a clear failure report.
    """

    print()
    print("=" * 90)
    print(" QUICKCART BUILD FAILED")
    print("=" * 90)

    print(f" Error Type : {type(exc).__name__}")
    print(f" Error      : {exc}")
    print(f" Time       : {elapsed_seconds:.2f} seconds")

    print()
    print("WHAT TO CHECK")
    print("-" * 90)

    print("  1. Read the error shown above.")
    print("  2. Check logs/quickcart.log")
    print("  3. Verify that all src/*.py files are present.")
    print("  4. Verify Python and package installation.")
    print("  5. Verify MySQL configuration when MySQL mode is used.")

    print()
    print("LOG FILE")
    print("-" * 90)

    print(f"  {LOGS_DIR / 'quickcart.log'}")

    print()
    print("=" * 90)


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """
    Master QuickCart project execution function.
    """

    start_time = time.perf_counter()

    logger = setup_logging()

    print_banner()

    logger.info("=" * 70)
    logger.info("QUICKCART PROJECT EXECUTION STARTED")
    logger.info("Project path: %s", BASE_DIR)
    logger.info("=" * 70)

    try:

        # ----------------------------------------------------
        # STEP 1
        # ----------------------------------------------------

        if not check_python_version():
            return 1

        # ----------------------------------------------------
        # STEP 2
        # ----------------------------------------------------

        if not check_and_install_dependencies():
            return 1

        # ----------------------------------------------------
        # STEP 3
        # ----------------------------------------------------

        if not create_project_directories():
            return 1

        # ----------------------------------------------------
        # STEP 4
        # ----------------------------------------------------

        modules_ready = verify_pipeline_modules()

        if not modules_ready:

            elapsed = time.perf_counter() - start_time

            print()
            print("=" * 90)
            print(" QUICKCART ORCHESTRATOR READY")
            print("=" * 90)

            print()
            print(
                " main.py has been created successfully."
            )

            print(
                " The remaining project modules will be added "
                "file-by-file."
            )

            print()
            print(
                " Once all files are created, simply run:"
            )

            print()
            print("    python main.py")
            print()

            print(
                " The complete pipeline will then execute automatically."
            )

            print()
            print(
                f" Current setup time: {elapsed:.2f} seconds"
            )

            print("=" * 90)
            print()

            logger.info(
                "Orchestrator stopped because required source modules "
                "are not yet present."
            )

            return 0

        # ----------------------------------------------------
        # STEP 5–13
        # ----------------------------------------------------

        pipeline_results = run_pipeline()

        # ----------------------------------------------------
        # STEP 14
        # ----------------------------------------------------

        verification = verify_project_outputs()

        # ----------------------------------------------------
        # FINAL REPORT
        # ----------------------------------------------------

        elapsed = time.perf_counter() - start_time

        print_final_report(
            pipeline_results=pipeline_results,
            verification=verification,
            elapsed_seconds=elapsed,
        )

        logger.info(
            "QUICKCART PROJECT EXECUTION COMPLETED IN %.2f SECONDS.",
            elapsed,
        )

        return 0

    except KeyboardInterrupt:

        elapsed = time.perf_counter() - start_time

        print()
        print_warning(
            "Project execution was stopped by the user."
        )

        logger.warning(
            "Execution interrupted by user after %.2f seconds.",
            elapsed,
        )

        return 130

    except Exception as exc:

        elapsed = time.perf_counter() - start_time

        print_failure_report(
            exc=exc,
            elapsed_seconds=elapsed,
        )

        logger.exception(
            "QUICKCART BUILD FAILED."
        )

        # Also write complete traceback to log.
        traceback.print_exc()

        return 1


# ============================================================
# PYTHON ENTRY POINT
# ============================================================

if __name__ == "__main__":
    sys.exit(main())