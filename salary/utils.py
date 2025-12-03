"""
Salary Management Utilities

Helper functions and utilities for salary operations.
"""

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple


def parse_month_string(month_str: str) -> Optional[date]:
    """
    Parse a month string into a date object (first day of month).
    
    Supported formats:
    - YYYY-MM (e.g., "2025-05")
    - Month YYYY (e.g., "May 2025")
    - YYYY-MM-DD (returns first day of month)
    
    Args:
        month_str: Month string to parse
        
    Returns:
        Date object (first day of month) or None if parsing fails
    """
    if not month_str:
        return None

    # Try YYYY-MM format
    try:
        if len(month_str) == 7 and "-" in month_str:
            year, month = month_str.split("-")
            return date(int(year), int(month), 1)
    except (ValueError, AttributeError):
        pass

    # Try Month YYYY format
    try:
        parsed = datetime.strptime(month_str, "%B %Y")
        return date(parsed.year, parsed.month, 1)
    except (ValueError, AttributeError):
        pass

    # Try YYYY-MM-DD format
    try:
        if len(month_str) == 10:
            parsed = datetime.strptime(month_str, "%Y-%m-%d")
            return date(parsed.year, parsed.month, 1)
    except (ValueError, AttributeError):
        pass

    return None


def format_month_display(month: date) -> str:
    """Format a month date for display (e.g., 'May 2025')."""
    return month.strftime("%B %Y")


def format_currency(amount: Decimal, currency_symbol: str = "$") -> str:
    """Format a decimal amount as currency."""
    return f"{currency_symbol}{amount:,.2f}"


def calculate_percentage_change(
    current: Decimal,
    previous: Decimal
) -> Tuple[Decimal, str]:
    """
    Calculate percentage change and return direction.
    
    Args:
        current: Current value
        previous: Previous value
        
    Returns:
        Tuple of (percentage, direction) where direction is 'up', 'down', or 'same'
    """
    if previous == 0:
        if current > 0:
            return Decimal("100.00"), "up"
        return Decimal("0.00"), "same"

    change = ((current - previous) / previous) * 100
    change = change.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    if change > 0:
        return change, "up"
    elif change < 0:
        return abs(change), "down"
    return Decimal("0.00"), "same"


def normalize_month(month: date) -> date:
    """Normalize a date to the first day of its month."""
    return month.replace(day=1)


def get_month_range(year: int, month: int) -> Tuple[date, date]:
    """
    Get the start and end dates of a month.
    
    Args:
        year: Year
        month: Month (1-12)
        
    Returns:
        Tuple of (first_day, last_day)
    """
    from calendar import monthrange
    
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    
    return first_day, last_day


def get_fiscal_year_months(start_month: int = 4) -> list:
    """
    Get months in fiscal year order.
    
    Args:
        start_month: First month of fiscal year (default: April = 4)
        
    Returns:
        List of month numbers in fiscal year order
    """
    months = list(range(start_month, 13)) + list(range(1, start_month))
    return months


def validate_salary_components(
    basic_salary: Decimal,
    allowances: list,
    deductions: list
) -> dict:
    """
    Validate salary components and return computed values.
    
    Args:
        basic_salary: Base salary amount
        allowances: List of allowance dicts with 'amount' key
        deductions: List of deduction dicts with 'amount' key
        
    Returns:
        Dictionary with validation result and computed values
    """
    errors = []

    if basic_salary < 0:
        errors.append("Basic salary cannot be negative")

    total_allowances = Decimal("0.00")
    for i, allowance in enumerate(allowances):
        amount = Decimal(str(allowance.get("amount", 0)))
        if amount < 0:
            errors.append(f"Allowance {i+1} amount cannot be negative")
        total_allowances += amount

    total_deductions = Decimal("0.00")
    for i, deduction in enumerate(deductions):
        amount = Decimal(str(deduction.get("amount", 0)))
        if amount < 0:
            errors.append(f"Deduction {i+1} amount cannot be negative")
        total_deductions += amount

    net_salary = basic_salary + total_allowances - total_deductions

    if net_salary < 0:
        errors.append("Net salary cannot be negative")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "basic_salary": basic_salary,
        "total_allowances": total_allowances,
        "total_deductions": total_deductions,
        "gross_salary": basic_salary + total_allowances,
        "net_salary": net_salary,
    }


# Default allowance types for quick setup
DEFAULT_ALLOWANCES = [
    {"allowance_type": "housing", "name": "Housing Allowance"},
    {"allowance_type": "transport", "name": "Transport Allowance"},
    {"allowance_type": "medical", "name": "Medical Allowance"},
]

# Default deduction types for quick setup
DEFAULT_DEDUCTIONS = [
    {"deduction_type": "income_tax", "name": "Income Tax"},
    {"deduction_type": "pension", "name": "Pension Fund"},
    {"deduction_type": "health_insurance", "name": "Health Insurance"},
]
