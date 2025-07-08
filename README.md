# Loan Calculator

A comprehensive loan calculator with both web interface and command-line interface that calculates loan payments, generates amortization schedules, and supports various types of extra payments.

## Features

### Core Functionality
- Calculate monthly loan payments based on principal, interest rate, and term
- Generate detailed amortization schedules
- Support for both percentage and dollar amount down payments
- Flexible loan start date selection
- Early payoff calculations with extra payments

### Payment Options
- **Monthly Extra Payments**: Add a fixed amount to each monthly payment
- **Yearly Extra Payments**: Make an additional payment once per year (in January)
- **One-Time Payments**: Schedule specific payments for any month/year during the loan term

### Interface Options
- **Web Interface**: Modern, responsive UI built with HTML, CSS (Tailwind), and JavaScript
- **Command Line Interface**: Interactive terminal-based calculator
- **REST API**: FastAPI backend for programmatic access

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package installer)

### Required Dependencies
```bash
pip install fastapi uvicorn pandas
```

### Project Structure
```
loan-calculator/
├── main.py           # Core loan calculation logic and CLI
├── app.py            # FastAPI web server
├── index.html        # Web interface
├── styles.css        # Styling
├── script.js         # Frontend JavaScript
└── README.md         # This file
```

## Usage

### Web Interface

1. **Start the web server:**
   ```bash
   uvicorn app:app --reload
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:8000
   ```

3. **Fill out the loan details:**
   - Total price of the item
   - Down payment (percentage or dollar amount)
   - Loan term in years
   - Annual interest rate
   - Loan start month and year
   - Optional extra payments

4. **Click "Calculate Loan"** to see results including:
   - Base monthly payment
   - Total amount paid
   - Payoff date
   - Complete amortization schedule

### Command Line Interface

Run the CLI version directly:
```bash
python main.py
```

Follow the interactive prompts to enter your loan details.

### API Usage

The web application exposes a REST API endpoint:

**POST /calculate**

Example request body:
```json
{
  "price": 300000,
  "down_percentage": 20,
  "term": 30,
  "rate": 5.0,
  "start_month": 1,
  "start_year": 2024,
  "monthly_extra_payment": 200,
  "yearly_extra_payment": 1000,
  "one_time_payments": [
    {
      "amount": 5000,
      "month": 6,
      "year": 2025
    }
  ]
}
```

## Input Parameters

### Required Fields
- **Price**: Total cost of the item being financed
- **Down Payment**: Either percentage (0-100) or dollar amount
- **Term**: Loan duration in years
- **Rate**: Annual interest rate as a percentage
- **Start Month**: Loan start month (1-12)
- **Start Year**: Loan start year

### Optional Fields
- **Monthly Extra Payment**: Additional amount added to each monthly payment
- **Yearly Extra Payment**: Annual lump sum payment (made in January)
- **One-Time Payments**: List of specific payments with amount, month, and year

## Output

### Summary Information
- **Base Monthly Payment**: Principal and interest payment for the original term
- **Total Amount Paid**: Actual total paid including all extra payments
- **Payoff Date**: When the loan will be completely paid off

### Amortization Schedule
Detailed month-by-month breakdown showing:
- Principal payment
- Interest payment
- Cumulative principal paid
- Cumulative interest paid
- Remaining loan balance
- Total amount paid to date

## Technical Details

### Core Algorithm
The calculator uses the standard loan amortization formula:
```
M = P * [r(1+r)^n] / [(1+r)^n - 1]
```
Where:
- M = Monthly payment
- P = Principal amount
- r = Monthly interest rate
- n = Total number of payments

### Extra Payment Handling
- Monthly extra payments are applied to principal each month
- Yearly extra payments are applied in January
- One-time payments are applied in their specified month/year
- All extra payments reduce the principal balance and shorten the loan term

### Edge Cases
- Handles zero interest rate loans
- Manages loans with zero principal
- Prevents negative loan balances
- Validates payment dates against loan start date

## Error Handling

### Input Validation
- Price must be non-negative
- Down payment percentage must be 0-100%
- Down payment amount cannot exceed price
- Interest rate must be non-negative
- Loan term must be positive
- Start month must be 1-12
- One-time payments cannot be scheduled before loan start

### Error Messages
The application provides clear error messages for:
- Invalid input ranges
- Calculation errors
- Server errors
- Network issues

## Browser Compatibility

The web interface is compatible with modern browsers including:
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Development

### File Structure
- `main.py`: Core `Loan` class with calculation logic
- `app.py`: FastAPI application with web server endpoints
- `index.html`: Responsive web interface
- `styles.css`: Custom styling and Tailwind CSS utilities
- `script.js`: Frontend JavaScript for form handling and API calls

### Extending the Calculator
To add new features:
1. Update the `Loan` class in `main.py` for core logic
2. Add new API endpoints in `app.py`
3. Update the web interface in `index.html` and `script.js`

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues or questions, please create an issue in the project repository or contact the maintainers.
