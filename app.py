from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from main import Loan

# Initialize the Loan object globally or per request if state management is complex
# For this simple example, a global instance is fine, but be mindful in larger apps.
loan = Loan()
app = FastAPI()


# Pydantic model for a single one-time payment
class OneTimePayment(BaseModel):
    amount: float
    month: int
    year: int


# Pydantic model for the entire loan calculation request payload
class LoanCalculationRequest(BaseModel):
    price: float
    down_percentage: float
    term: int
    rate: float
    start_month: int
    start_year: int
    monthly_extra_payment: Optional[float] = 0.0
    yearly_extra_payment: Optional[float] = 0.0
    one_time_payments: Optional[List[OneTimePayment]] = []


@app.get("/")
async def get_ui():
    """Serves the main HTML page."""
    return FileResponse("index.html")


@app.get("/styles.css")
async def get_styles():
    """Serves the CSS file."""
    return FileResponse("styles.css")


@app.get("/script.js")
async def get_script():
    """Serves the JavaScript file."""
    return FileResponse("script.js")


@app.post("/calculate")
async def calculate_loan(request: LoanCalculationRequest):
    """
    Calculates loan payments and amortization schedule based on the provided data.
    Expects a JSON body matching the LoanCalculationRequest model.
    """
    try:
        # Call the calculate method from the Loan class
        # Access parameters directly from the request object
        monthly_payment, total_amount_paid, amortization_schedule_df, payoff_month, payoff_year = loan.calculate(
            price=request.price,
            down_percentage=request.down_percentage,
            term=request.term,
            rate=request.rate,
            start_month=request.start_month,
            start_year=request.start_year,
            monthly_extra_payment=request.monthly_extra_payment,
            yearly_extra_payment=request.yearly_extra_payment,
            one_time_payments=[p.dict() for p in request.one_time_payments]  # Convert Pydantic models to dicts
        )

        # Format payoff date for display
        payoff_date_str = "N/A"
        if payoff_month is not None and payoff_year is not None:
            try:
                payoff_date_str = datetime(payoff_year, payoff_month, 1).strftime('%B %Y')
            except ValueError:
                payoff_date_str = "Invalid Date"

        # Convert DataFrame to a list of dictionaries for JSON serialization
        amortization_schedule_list = amortization_schedule_df.to_dict(orient='records')

        # Return the calculated results
        return {
            "monthly_payment": monthly_payment,
            "total_amount_paid": total_amount_paid,
            "amortization_schedule": amortization_schedule_list,
            "payoff_date": payoff_date_str
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Input Error: {ve}")
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Calculation Error: Division by zero. Check price or rates.")
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {e}")
