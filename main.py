import math
import pandas as pd
from datetime import datetime, timedelta  # Used for date formatting


class Loan:
    def __init__(self):
        self.price = 0
        self.down = 0
        self.principal = 0
        self.term = 0
        self.rate = 0
        self.tp = 0  # Total Payment (monthly payment based on original term, P&I)
        self.total = 0  # Total amount paid over the actual loan term (including all extra payments)

        self.start_month = 0
        self.start_year = 0
        self.payoff_month = None  # Month when loan is paid off
        self.payoff_year = None  # Year when loan is paid off

        self.df = pd.DataFrame()

    def calculate(
        self, price, down_percentage, term, rate, start_month, start_year,
        monthly_extra_payment=0, yearly_extra_payment=0, one_time_payments=None
    ):

        self.price = price
        self.down = down_percentage / 100
        self.principal = price * (1 - self.down)
        self.term = term
        self.rate = rate / 100
        self.start_month = start_month
        self.start_year = start_year

        if one_time_payments is None:
            one_time_payments = []

        monthly_rate = self.rate / 12
        num_payments_original_term = term * 12  # Max possible payments based on original term

        # Calculate base monthly payment (P&I) for the original term
        if monthly_rate == 0:
            if num_payments_original_term == 0:  # Handle 0 term
                self.tp = 0
            else:
                self.tp = self.principal / num_payments_original_term
        else:
            if num_payments_original_term == 0:  # Handle 0 term
                self.tp = 0
            else:
                self.tp = (
                        self.principal
                        * monthly_rate
                        * math.pow(1 + monthly_rate, num_payments_original_term)
                        / (math.pow(1 + monthly_rate, num_payments_original_term) - 1)
                )

        # Define DataFrame columns, including Month and Year
        columns = [
            'Month', 'Year', 'Principal Payment', 'Interest Payment',
            'Principal Paid', 'Interest Paid', 'Loan Balance', 'Total Amount Paid'
        ]

        # We will build the DataFrame row by row to accurately capture early payoff
        data = []

        # Add initial row for month 0 (loan inception)
        data.append({
            'Month': self.start_month,
            'Year': self.start_year,
            'Principal Payment': 0.0,
            'Interest Payment': 0.0,
            'Principal Paid': 0.0,
            'Interest Paid': 0.0,
            'Loan Balance': self.principal,
            'Total Amount Paid': 0.0
        })

        current_loan_balance = self.principal
        principal_paid_total = 0
        interest_paid_total = 0
        cumulative_total_paid = 0

        # Start tracking current date from the input start month/year
        current_date = datetime(self.start_year, self.start_month, 1)

        # Loop for a slightly extended period than the original term to ensure final payment is captured,
        # but will break early if loan is paid off.
        # +2 is a safe margin for early payoff scenarios to ensure the last payment is recorded.
        for i in range(1, num_payments_original_term + 2):
            # Break if loan is already paid off from previous month's calculations
            if current_loan_balance <= 0:
                self.payoff_month = current_date.month
                self.payoff_year = current_date.year
                break

                # Move to the next month for the current payment period
            current_date += timedelta(days=32)  # Go to next month, then adjust to 1st
            current_date = current_date.replace(day=1)

            # Calculate interest for the current month based on the beginning balance
            interest_for_month = current_loan_balance * monthly_rate

            # Regular principal payment from the base monthly payment
            regular_principal_payment = self.tp - interest_for_month

            # Ensure regular principal payment does not exceed the current balance
            regular_principal_payment = min(regular_principal_payment, current_loan_balance)

            # --- Apply extra payments for this month ---
            extra_principal_payment_this_month = 0

            # Monthly extra payment
            extra_principal_payment_this_month += monthly_extra_payment

            # Yearly extra payment (assuming made in January, i.e., current_date.month == 1)
            if current_date.month == 1:
                extra_principal_payment_this_month += yearly_extra_payment

            # One-time payments for this specific month/year
            payments_applied_this_month = []
            # Iterate through a copy or by index to safely remove applied payments
            for op_idx, op in enumerate(list(one_time_payments)):  # Use list() to iterate over a copy
                if op['month'] == current_date.month and op['year'] == current_date.year:
                    extra_principal_payment_this_month += op['amount']
                    payments_applied_this_month.append(op)  # Store payment to remove it later

            # Remove applied one-time payments from the original list
            for op in payments_applied_this_month:
                one_time_payments.remove(op)

            # Total principal reduction for this month (regular + all extra payments)
            total_principal_reduction = regular_principal_payment + extra_principal_payment_this_month

            # Ensure total principal reduction does not cause the loan balance to go excessively negative
            actual_principal_payment_this_month = min(total_principal_reduction, current_loan_balance)

            # Actual total cash paid out this month (base payment + extra payments)
            actual_total_cash_out_this_month = self.tp + extra_principal_payment_this_month

            # Adjust if the total principal reduction was capped
            if total_principal_reduction > current_loan_balance:
                # If total payments would have overpaid, the final payment is just remaining balance + interest
                actual_total_cash_out_this_month = interest_for_month + current_loan_balance

            current_loan_balance -= actual_principal_payment_this_month
            current_loan_balance = max(0, current_loan_balance)  # Ensure loan balance doesn't become negative

            principal_paid_total += actual_principal_payment_this_month
            interest_paid_total += interest_for_month
            cumulative_total_paid += actual_total_cash_out_this_month

            data.append({
                'Month': current_date.month,
                'Year': current_date.year,
                'Principal Payment': actual_principal_payment_this_month,
                'Interest Payment': interest_for_month,
                'Principal Paid': principal_paid_total,
                'Interest Paid': interest_paid_total,
                'Loan Balance': current_loan_balance,
                'Total Amount Paid': cumulative_total_paid
            })

            # If loan balance is zero or less after this month's payment, record payoff date and break
            if current_loan_balance <= 0:
                self.payoff_month = current_date.month
                self.payoff_year = current_date.year
                break

        self.df = pd.DataFrame(data, columns=columns)
        self.total = cumulative_total_paid  # Final cumulative total paid over the actual loan term

        # Special handling for loans with 0 principal or 0 term (already paid off at start)
        if self.principal <= 0 or num_payments_original_term == 0:
            self.payoff_month = self.start_month
            self.payoff_year = self.start_year
            self.total = 0.0
            self.tp = 0.0
            self.df = pd.DataFrame(data=[{  # Create a minimal DataFrame for 0 principal loan
                'Month': self.start_month, 'Year': self.start_year,
                'Principal Payment': 0.0, 'Interest Payment': 0.0,
                'Principal Paid': 0.0, 'Interest Paid': 0.0,
                'Loan Balance': 0.0, 'Total Amount Paid': 0.0
            }], columns=columns)

        return self.tp, self.total, self.df, self.payoff_month, self.payoff_year


def main():
    while True:
        print("\nDo you want to:")
        print("(1) Calculate your loan payments")
        print("(2) Quit")

        choice = input("Enter your choice (1 or 2): ")

        if choice == '1':
            try:
                price = float(input("Enter the total price of the item (e.g., 300000): "))
                if price < 0:
                    raise ValueError("Price cannot be negative.")

                # --- Down Payment Input ---
                down_input_type = input(
                    "Do you want to enter down payment as (P)ercentage or (A)mount? ").strip().upper()
                down_payment_percentage = 0.0

                if down_input_type == 'P':
                    down_percentage = float(input("Enter the down payment percentage (e.g., 20 for 20%): "))
                    if not (0 <= down_percentage <= 100):
                        raise ValueError("Down payment percentage must be between 0 and 100.")
                    down_payment_percentage = down_percentage
                elif down_input_type == 'A':
                    down_amount = float(input("Enter the down payment amount (e.g., 60000): "))
                    if not (0 <= down_amount <= price):
                        raise ValueError(f"Down payment amount must be between 0 and the price ({price}).")
                    if price == 0 and down_amount > 0:
                        raise ValueError("Cannot have a down payment amount if the item price is 0.")
                    elif price == 0 and down_amount == 0:
                        down_payment_percentage = 0
                    else:
                        down_payment_percentage = (down_amount / price) * 100
                else:
                    raise ValueError("Invalid down payment input type. Please enter 'P' or 'A'.")

                term = int(input("Enter the loan term in years (e.g., 30): "))
                if term < 0:
                    raise ValueError("Loan term cannot be negative.")

                rate = float(input("Enter the annual interest rate percentage (e.g., 5 for 5%): "))
                if rate < 0:
                    raise ValueError("Interest rate cannot be negative.")

                # --- Start Month and Year Input ---
                start_month = int(input("Enter the loan start month (1-12, e.g., 1 for January): "))
                if not (1 <= start_month <= 12):
                    raise ValueError("Start month must be between 1 and 12.")
                start_year = int(input("Enter the loan start year (e.g., 2023): "))
                # Basic validation for year
                if start_year < 1900 or start_year > 2100:
                    print("Warning: Start year seems unrealistic (outside 1900-2100). Proceeding anyway.")

                # --- Monthly Extra Payment Input ---
                monthly_extra_payment = 0
                extra_monthly_choice = input("Do you want to make a monthly extra payment? (yes/no): ").strip().lower()
                if extra_monthly_choice == 'yes':
                    monthly_extra_payment = float(input("Enter the monthly extra payment amount: "))
                    if monthly_extra_payment < 0:
                        print("Monthly extra payment cannot be negative. Setting to 0.")
                        monthly_extra_payment = 0
                elif extra_monthly_choice != 'no':
                    print("Invalid choice for monthly extra payment. Assuming no extra monthly payment.")

                # --- Yearly Extra Payment Input ---
                yearly_extra_payment = 0
                extra_yearly_choice = input("Do you want to make a yearly extra payment? (yes/no): ").strip().lower()
                if extra_yearly_choice == 'yes':
                    yearly_extra_payment = float(input("Enter the yearly extra payment amount: "))
                    if yearly_extra_payment < 0:
                        print("Yearly extra payment cannot be negative. Setting to 0.")
                        yearly_extra_payment = 0
                elif extra_yearly_choice != 'no':
                    print("Invalid choice for yearly extra payment. Assuming no extra yearly payment.")

                # --- One-Time Payments Input ---
                one_time_payments = []
                num_one_time_payments = int(
                    input("How many additional one-time payments do you want to make? (0 for none): "))
                if num_one_time_payments < 0:
                    print("Number of one-time payments cannot be negative. Setting to 0.")
                    num_one_time_payments = 0

                for i in range(num_one_time_payments):
                    print(f"\n--- One-Time Payment {i + 1} Details ---")
                    ot_amount = float(input(f"Enter amount for payment {i + 1}: "))
                    if ot_amount < 0:
                        print("One-time payment amount cannot be negative. Skipping this payment.")
                        continue
                    ot_month = int(input(f"Enter month for payment {i + 1} (1-12): "))
                    if not (1 <= ot_month <= 12):
                        print("Invalid month (must be 1-12). Skipping this payment.")
                        continue
                    ot_year = int(input(f"Enter year for payment {i + 1}: "))
                    # Basic validation for one-time payment date not being before loan start
                    ot_date_str = f"{ot_year}-{ot_month}-01"
                    start_date_str = f"{start_year}-{start_month}-01"

                    try:
                        ot_date = datetime.strptime(ot_date_str, '%Y-%m-%d')
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                        if ot_date < start_date:
                            print("One-time payment date cannot be before loan start date. Skipping this payment.")
                            continue
                    except ValueError:  # If date conversion fails for some reason
                        print("Invalid date format for one-time payment. Skipping this payment.")
                        continue

                    one_time_payments.append({'amount': ot_amount, 'month': ot_month, 'year': ot_year})

                loan = Loan()
                # Unpack all return values from calculate()
                monthly_payment, total_amount_paid, amortization_schedule, payoff_month, payoff_year = \
                    loan.calculate(price, down_payment_percentage, term, rate,
                                   start_month, start_year,
                                   monthly_extra_payment, yearly_extra_payment, one_time_payments)

                print(f"\nYour estimated base monthly payment (Principal & Interest): ${monthly_payment:.2f}")
                print(
                    f"Total amount paid over the actual loan term (including all extra payments): ${total_amount_paid:.2f}")

                if payoff_month is not None and payoff_year is not None:
                    # Format the payoff date nicely
                    print(f"Loan paid off on: {datetime(payoff_year, payoff_month, 1).strftime('%B %Y')}")
                else:
                    print("Loan payoff date could not be determined.")

                print("\nAmortization Schedule:")

                # Display the DataFrame intelligently for large schedules
                if len(amortization_schedule) > 26:  # If more than 25 rows + header
                    print(amortization_schedule.head(13).to_string())  # Show first 12 months + header
                    print("...")
                    print(amortization_schedule.tail(12).to_string())  # Show last 12 months
                else:
                    print(amortization_schedule.to_string())

            except ValueError as ve:
                print(f"Input Error: {ve}. Please ensure all inputs are valid.")
            except ZeroDivisionError:
                print("Error: Cannot calculate with zero price or other invalid zero values.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        elif choice == '2':
            print("Exiting the loan calculator. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
