import math

def _number(application: dict, field: str, label: str, errors: list) -> float:
    """Read a finite, non-negative numeric value."""
    value = application.get(field)

    if isinstance(value, bool) or value is None:
        errors.append(f"{label} is missing or invalid.")
        return 0.0

    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        errors.append(f"{label} is missing or not numeric.")
        return 0.0

    if not math.isfinite(number):
        errors.append(f"{label} must be a finite number.")
        return 0.0

    if number < 0:
        errors.append(f"{label} cannot be negative.")
        return 0.0

    return number


def calculate_financial_summary(application: dict) -> dict:
    """Calculate transparent financial summaries from application inputs."""
    errors = []

    income = _number(
        application, "declared_monthly_income",
        "Declared monthly income", errors
    )
    expenses = _number(
        application, "monthly_expenses",
        "Monthly expenses", errors
    )
    debt = _number(
        application, "monthly_debt_payments",
        "Existing monthly debt payments", errors
    )
    instalment = _number(
        application, "proposed_monthly_instalment",
        "Proposed monthly instalment", errors
    )

    total_outgoings = expenses + debt
    disposable = income - total_outgoings

    # Avoid division by zero when income is zero.
    dti = None if income == 0 else (debt / income) * 100

    post_proposed_disposable = disposable - instalment

    return {
        "gross_monthly_income": round(income, 2),
        "monthly_expenses": round(expenses, 2),
        "existing_monthly_debt_payments": round(debt, 2),
        "total_monthly_outgoings": round(total_outgoings, 2),
        "disposable_income": round(disposable, 2),
        "debt_to_income_ratio_percent": (
            None if dti is None else round(dti, 2)
        ),
        "proposed_monthly_instalment": round(instalment, 2),
        "disposable_income_after_proposed_instalment": round(
            post_proposed_disposable, 2
        ),
        "input_errors": errors,
        "definitions": {
            "disposable_income": (
                "Declared gross monthly income minus declared living "
                "expenses and existing monthly debt payments; this is "
                "a simplified illustrative measure."
            ),
            "debt_to_income_ratio_percent": (
                "Existing monthly debt payments divided by declared "
                "gross monthly income, multiplied by 100. It excludes "
                "the proposed instalment."
            ),
        },
    }
