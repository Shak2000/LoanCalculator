document.addEventListener('DOMContentLoaded', () => {
    const loanForm = document.getElementById('loanForm');
    const downPaymentType = document.getElementById('downPaymentType');
    const downPaymentValue = document.getElementById('downPaymentValue');
    const addOneTimePaymentBtn = document.getElementById('addOneTimePayment');
    const oneTimePaymentsContainer = document.getElementById('oneTimePaymentsContainer');
    const resultsDiv = document.getElementById('results');
    const baseMonthlyPaymentSpan = document.getElementById('baseMonthlyPayment');
    const totalAmountPaidSpan = document.getElementById('totalAmountPaid');
    const payoffDateSpan = document.getElementById('payoffDate');
    const amortizationTableBody = document.getElementById('amortizationTableBody');
    const messageBox = document.getElementById('messageBox');
    const messageText = document.getElementById('messageText');
    const closeMessageBoxBtn = document.getElementById('closeMessageBox');

    let oneTimePaymentCounter = 0; // To keep track of one-time payment inputs

    // Function to show a custom message box
    function showMessageBox(message) {
        messageText.textContent = message;
        messageBox.classList.remove('hidden');
    }

    // Function to close the custom message box
    closeMessageBoxBtn.addEventListener('click', () => {
        messageBox.classList.add('hidden');
    });

    // Update down payment input placeholder based on type selection
    downPaymentType.addEventListener('change', (event) => {
        if (event.target.value === 'percentage') {
            downPaymentValue.placeholder = 'e.g., 20 (for 20%)';
        } else {
            downPaymentValue.placeholder = 'e.g., 60000';
        }
    });

    // Add initial placeholder text on load
    downPaymentType.dispatchEvent(new Event('change'));

    // Add One-Time Payment fields
    addOneTimePaymentBtn.addEventListener('click', () => {
        oneTimePaymentCounter++;
        const paymentDiv = document.createElement('div');
        paymentDiv.classList.add('grid', 'grid-cols-1', 'md:grid-cols-4', 'gap-4', 'items-end', 'one-time-payment-row');
        paymentDiv.innerHTML = `
            <div>
                <label for="otAmount${oneTimePaymentCounter}" class="block text-sm font-medium text-gray-700">Amount ($)</label>
                <input type="number" id="otAmount${oneTimePaymentCounter}" name="otAmount" step="0.01" required
                       class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            </div>
            <div>
                <label for="otMonth${oneTimePaymentCounter}" class="block text-sm font-medium text-gray-700">Month (1-12)</label>
                <input type="number" id="otMonth${oneTimePaymentCounter}" name="otMonth" min="1" max="12" required
                       class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            </div>
            <div>
                <label for="otYear${oneTimePaymentCounter}" class="block text-sm font-medium text-gray-700">Year</label>
                <input type="number" id="otYear${oneTimePaymentCounter}" name="otYear" required
                       class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            </div>
            <button type="button"
                    class="remove-one-time-payment px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50 transition duration-150 ease-in-out">
                Remove
            </button>
        `;
        oneTimePaymentsContainer.appendChild(paymentDiv);

        // Add event listener to the new remove button
        paymentDiv.querySelector('.remove-one-time-payment').addEventListener('click', () => {
            paymentDiv.remove();
        });
    });

    // Handle form submission
    loanForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        // Clear previous results
        resultsDiv.classList.add('hidden');
        amortizationTableBody.innerHTML = '';

        // Gather form data
        const price = parseFloat(document.getElementById('price').value);
        const downPaymentTypeValue = downPaymentType.value;
        const downPaymentValueInput = parseFloat(downPaymentValue.value);
        let downPercentage;

        // Calculate down_percentage based on user's input type
        if (downPaymentTypeValue === 'percentage') {
            downPercentage = downPaymentValueInput;
            if (downPercentage < 0 || downPercentage > 100) {
                showMessageBox("Down payment percentage must be between 0 and 100.");
                return;
            }
        } else { // 'amount'
            const downAmount = downPaymentValueInput;
            if (downAmount < 0 || downAmount > price) {
                showMessageBox(`Down payment amount must be between 0 and the total price (${price.toFixed(2)}).`);
                return;
            }
            if (price === 0 && downAmount > 0) {
                showMessageBox("Cannot have a down payment amount if the item price is 0.");
                return;
            }
            downPercentage = (downAmount / price) * 100;
        }

        const term = parseInt(document.getElementById('term').value);
        const rate = parseFloat(document.getElementById('rate').value);
        const startMonth = parseInt(document.getElementById('startMonth').value);
        const startYear = parseInt(document.getElementById('startYear').value);
        const monthlyExtraPayment = parseFloat(document.getElementById('monthlyExtraPayment').value) || 0;
        const yearlyExtraPayment = parseFloat(document.getElementById('yearlyExtraPayment').value) || 0;

        // Gather one-time payments
        const oneTimePayments = [];
        document.querySelectorAll('.one-time-payment-row').forEach(row => {
            const amount = parseFloat(row.querySelector('[name="otAmount"]').value);
            const month = parseInt(row.querySelector('[name="otMonth"]').value);
            const year = parseInt(row.querySelector('[name="otYear"]').value);

            if (isNaN(amount) || isNaN(month) || isNaN(year) || amount < 0 || month < 1 || month > 12) {
                showMessageBox("Please ensure all one-time payment fields are valid (amount >= 0, month 1-12). Skipping invalid payments.");
                return; // Skip this invalid row
            }

            // Basic date validation for one-time payments not being before loan start
            const otDate = new Date(year, month - 1, 1); // month - 1 because Date object months are 0-indexed
            const startDate = new Date(startYear, startMonth - 1, 1);
            if (otDate < startDate) {
                showMessageBox(`One-time payment on ${month}/${year} cannot be before loan start date (${startMonth}/${startYear}). Skipping this payment.`);
                return; // Skip this invalid row
            }

            oneTimePayments.push({ amount, month, year });
        });

        // Construct the payload for the API call
        const payload = {
            price: price,
            down_percentage: downPercentage,
            term: term,
            rate: rate,
            start_month: startMonth,
            start_year: startYear,
            monthly_extra_payment: monthlyExtraPayment,
            yearly_extra_payment: yearlyExtraPayment,
            one_time_payments: oneTimePayments
        };

        try {
            const response = await fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                showMessageBox(`Error: ${errorData.detail || response.statusText}`);
                return;
            }

            const data = await response.json();

            // Display summary results
            baseMonthlyPaymentSpan.textContent = `$${data.monthly_payment.toFixed(2)}`;
            totalAmountPaidSpan.textContent = `$${data.total_amount_paid.toFixed(2)}`;
            payoffDateSpan.textContent = data.payoff_date || 'N/A';

            // Populate amortization table
            data.amortization_schedule.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${row['Month']}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${row['Year']}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$${row['Principal Payment'].toFixed(2)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$${row['Interest Payment'].toFixed(2)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$${row['Principal Paid'].toFixed(2)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$${row['Interest Paid'].toFixed(2)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$${row['Loan Balance'].toFixed(2)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$${row['Total Amount Paid'].toFixed(2)}</td>
                `;
                amortizationTableBody.appendChild(tr);
            });

            resultsDiv.classList.remove('hidden'); // Show results section

        } catch (error) {
            console.error('Fetch error:', error);
            showMessageBox(`An unexpected error occurred: ${error.message}`);
        }
    });
});
