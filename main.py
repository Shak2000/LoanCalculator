import math
import pandas as pd


class Loan:
    def __init__(self):
        self.price = 0
        self.down = 0
        self.principal = 0
        self.term = 0
        self.rate = 0
        self.tp = 0  # Total Payment
        self.df = pd.DataFrame()

    def calculate(self, price, down_percentage, term, rate):
        self.price = price
        self.down = down_percentage / 100  # Convert percentage to decimal
        self.principal = price * (1 - self.down)  # Principal is price minus down payment
        self.term = term
        self.rate = rate / 100  # Convert percentage to decimal

        monthly_rate = self.rate / 12
        num_payments = term * 12

        if monthly_rate == 0:
            self.tp = self.principal / num_payments
        else:
            self.tp = (
                    self.principal
                    * monthly_rate
                    * math.pow(1 + monthly_rate, num_payments)
                    / (math.pow(1 + monthly_rate, num_payments) - 1)
            )

        # Initialize DataFrame with correct dimensions and initial loan balance
        self.df = pd.DataFrame({
            'Principal Payment': [0.0] * (num_payments + 1),
            'Interest Payment': [0.0] * (num_payments + 1),
            'Principal Paid': [0.0] * (num_payments + 1),
            'Interest Paid': [0.0] * (num_payments + 1),
            'Loan Balance': [0.0] * (num_payments + 1)
        })
        self.df.loc[0, 'Loan Balance'] = self.principal

        principal_paid_total = 0
        interest_paid_total = 0

        for i in range(1, num_payments + 1):
            beginning_balance = self.df.loc[i - 1, 'Loan Balance']
            interest_payment = beginning_balance * monthly_rate
            principal_payment = self.tp - interest_payment
            ending_balance = beginning_balance - principal_payment

            principal_paid_total += principal_payment
            interest_paid_total += interest_payment

            self.df.loc[i, 'Principal Payment'] = principal_payment
            self.df.loc[i, 'Interest Payment'] = interest_payment
            self.df.loc[i, 'Principal Paid'] = principal_paid_total
            self.df.loc[i, 'Interest Paid'] = interest_paid_total
            self.df.loc[i, 'Loan Balance'] = max(0, ending_balance)  # Ensure balance doesn't go negative

        return self.tp, self.df


def run_calculator():
    while True:
        print("\nDo you want to:")
        print("(1) Calculate your loan payments")
        print("(2) Quit")

        choice = input("Enter your choice (1 or 2): ")

        if choice == '1':
            try:
                price = float(input("Enter the total price of the item (e.g., 300000): "))

                down_input_type = input(
                    "Do you want to enter down payment as (P)ercentage or (A)mount? ").strip().upper()

                down_payment_percentage = 0.0

                if down_input_type == 'P':
                    down_percentage = float(input("Enter the down payment percentage (e.g., 20 for 20%): "))
                    if not (0 <= down_percentage <= 100):
                        print("Down payment percentage must be between 0 and 100.")
                        continue
                    down_payment_percentage = down_percentage
                elif down_input_type == 'A':
                    down_amount = float(input("Enter the down payment amount (e.g., 60000): "))
                    if not (0 <= down_amount <= price):
                        print(f"Down payment amount must be between 0 and the price ({price}).")
                        continue
                    down_payment_percentage = (down_amount / price) * 100
                else:
                    print("Invalid down payment input type. Please enter 'P' or 'A'.")
                    continue

                term = int(input("Enter the loan term in years (e.g., 30): "))
                rate = float(input("Enter the annual interest rate percentage (e.g., 5 for 5%): "))

                loan = Loan()
                # Pass the calculated percentage to the calculate method
                monthly_payment, amortization_schedule = loan.calculate(price, down_payment_percentage, term, rate)

                print(f"\nYour estimated monthly payment is: ${monthly_payment:.2f}")
                print("\nAmortization Schedule:")

                # Display the DataFrame, limiting rows for large terms
                if term * 12 > 24:  # Show first 12 and last 12, or adjust as desired
                    print(amortization_schedule.head(13).to_string())
                    print("...")
                    print(amortization_schedule.tail(12).to_string())
                else:
                    print(amortization_schedule.to_string())

            except ValueError:
                print("Invalid input. Please enter valid numeric values.")
            except ZeroDivisionError:
                print("Cannot calculate percentage for a price of zero. Please enter a valid price.")
            except Exception as e:
                print(f"An error occurred: {e}")
        elif choice == '2':
            print("Exiting the loan calculator. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    run_calculator()
