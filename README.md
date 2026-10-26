# Loan Application Readiness Agent

A student Agentic AI project that checks whether a **synthetic** loan application is complete and internally consistent, calculates transparent financial summaries, verifies arithmetic, and prepares questions for a human reviewer.

## Safety boundary
This project evaluates application readiness only. It does not approve/reject loans or determine actual creditworthiness. All example data is synthetic. Do not enter real personal or financial information.

## Features in the MVP
- Required-field and required-evidence checks
- Financial summary: monthly outgoings, simplified disposable income, existing debt-to-income ratio
- Declared-income versus supplied-record comparison
- Tool execution trace
- Independent arithmetic verification
- Reviewer questions and downloadable JSON report
- Automated tests

## Requirements
Python 3.11+ recommended.

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If activation is blocked, run `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m streamlit run app.py`.

## Run
```powershell
streamlit run app.py
```
Open the local URL printed in the terminal.

## Test
```powershell
pytest -q
```

## Agentic workflow
The orchestrator calls four tools: `check_completeness`, `calculate_financial_summary`, `check_consistency`, and `verify_financial_summary`. It combines their results into a transparent readiness status and reviewer questions. The LLM explanation layer is an optional future extension; this MVP does not pretend that deterministic rules are an LLM.

## Status rules
- **Incomplete**: required fields/evidence are missing, or financial inputs are invalid.
- **Needs clarification**: configured consistency checks find an issue, or verification fails.
- **Ready for human review**: configured checks pass. This is not loan eligibility or approval.

## Suggested next steps
1. Add a locally hosted LLM (e.g., via Ollama) to phrase questions from structured findings, while keeping tool outputs authoritative.
2. Add more synthetic test cases and test invalid/zero income.
3. Add an audit log and a more explicit review checklist.
4. Document each team member's actual contribution.
