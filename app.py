from fastapi import FastAPI
from fastapi.responses import FileResponse

from main import Loan

loan = Loan()
app = FastAPI()


@app.get("/")
async def get_ui():
    return FileResponse("index.html")


@app.get("/styles.css")
async def get_styles():
    return FileResponse("styles.css")


@app.get("/script.js")
async def get_script():
    return FileResponse("script.js")


@app.post("/calculate")
async def calculate(
    price, down_percentage, term, rate, start_month, start_year,
    monthly_extra_payment=0, yearly_extra_payment=0, one_time_payments=None
):
    loan.calculate(
        price, down_percentage, term, rate, start_month, start_year,
        monthly_extra_payment, yearly_extra_payment, one_time_payments
    )
