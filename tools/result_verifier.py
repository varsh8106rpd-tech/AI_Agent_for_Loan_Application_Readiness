def verify_financial_summary(application: dict, summary: dict, tolerance: float = 0.01) -> dict:
    """Independently recompute key arithmetic and compare with tool output."""
    try:
        income = float(application["declared_monthly_income"])
        expenses = float(application["monthly_expenses"])
        debt = float(application["monthly_debt_payments"])
        instalment = float(application["proposed_monthly_instalment"])
        expected_disposable = income - expenses - debt
        expected_outgoings = expenses + debt
        expected_post_instalment = expected_disposable - instalment

        checks = {
            "total_monthly_outgoings": abs(summary["total_monthly_outgoings"] - expected_outgoings) <= tolerance,
            "disposable_income": abs(summary["disposable_income"] - expected_disposable) <= tolerance,
            "disposable_income_after_proposed_instalment": abs(summary["disposable_income_after_proposed_instalment"] - expected_post_instalment) <= tolerance,
        }
        passed = all(checks.values()) and not summary["input_errors"]
        return {
            "passed": passed,
            "checks": checks,
            "summary": "Independent arithmetic checks passed." if passed else "One or more arithmetic checks failed or inputs were invalid.",
        }
    except (KeyError, TypeError, ValueError):
        return {"passed": False, "checks": {}, "summary": "Verification could not complete because required values were unavailable."}
