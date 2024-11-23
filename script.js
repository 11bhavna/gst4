 

    <script>
        // Get DOM elements
        const purchaseForm = document.getElementById('purchase-form');
        const purchaseDateInput = document.getElementById('purchase-date');
        const companyNameInput = document.getElementById('company-name');
        const productNameInput = document.getElementById('product-name');
        const billFileInput = document.getElementById('bill-file');
        const purchaseListTable = document.getElementById('purchase-list').getElementsByTagName('tbody')[0];
        const downloadExcelButton = document.getElementById('download-excel');

        // Load purchases from localStorage when the page loads
        document.addEventListener('DOMContentLoaded', loadPurchases);

        // Add a new purchase entry
        purchaseForm.addEventListener('submit', function(event) {
            event.preventDefault();

            // Determine the status based on whether a bill file is uploaded
            const status = billFileInput.files[0] ? "Received" : "Pending";

            // Get form data
            const purchaseData = {
                date: purchaseDateInput.value,
                company: companyNameInput.value,
                product: productNameInput.value,
                status: status,
                billUrl: billFileInput.files[0] ? URL.createObjectURL(billFileInput.files[0]) : ''
            };

            // Save data to localStorage
            let purchases = JSON.parse(localStorage.getItem('purchases')) || [];
            purchases.push(purchaseData);
            localStorage.setItem('purchases', JSON.stringify(purchases));

            // Clear form fields
            purchaseForm.reset();

            // Reload purchases on page
            loadPurchases();

            // Send purchase data to Google Apps Script
            sendPurchaseToGoogleSheet(purchaseData);
        });

        // Load all purchase entries from localStorage
        function loadPurchases() {
            const purchases = JSON.parse(localStorage.getItem('purchases')) || [];

            // Clear the current table rows
            purchaseListTable.innerHTML = '';

            // Populate the table with stored purchases
            purchases.forEach((purchase, index) => {
                const row = purchaseListTable.insertRow();

                row.innerHTML = `
                    <td>${purchase.date}</td>
                    <td>${purchase.company}</td>
                    <td>${purchase.product}</td>
                    <td>${purchase.status}</td>
                    <td><a href="${purchase.billUrl}" target="_blank">${purchase.billUrl ? "View Bill" : "No Bill"}</a></td>
                `;
            });

            // Show the "Download Excel" button if there are any purchases
            if (purchases.length > 0) {
                downloadExcelButton.style.display = 'inline-block';
            }
        }

        // Download the purchase data as an Excel file
        downloadExcelButton.addEventListener('click', function() {
            const purchases = JSON.parse(localStorage.getItem('purchases')) || [];
            
            // Convert purchase data into an array of objects
            const purchaseArray = purchases.map(purchase => ({
                'Date': purchase.date,
                'Company Name': purchase.company,
                'Product': purchase.product,
                'Status': purchase.status,
                'Bill': purchase.billUrl ? 'Yes' : 'No'
            }));

            // Create a new Excel file using SheetJS (xlsx.js)
            const wb = XLSX.utils.book_new();
            const ws = XLSX.utils.json_to_sheet(purchaseArray);

            XLSX.utils.book_append_sheet(wb, ws, 'Purchases');

            // Generate and download the Excel file
            XLSX.writeFile(wb, 'purchases.xlsx');
        });

        // Send purchase data to Google Sheets using Google Apps Script
        function sendPurchaseToGoogleSheet(purchaseData) {
            const url = 'https://script.google.com/macros/s/your-script-id/exec';

            // Format the purchase data for the POST request
            const data = {
                command: 'append_row',
                sheet_name: 'Sheet1',
                values: `${purchaseData.date},${purchaseData.company},${purchaseData.product},${purchaseData.status},${purchaseData.billUrl ? 'Yes' : 'No'}`
            };

            // Send the data to Google Apps Script using fetch
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
                .then(response => response.text())
                .then(result => console.log(result))  // Success message from Apps Script
                .catch(error => console.log('Error:', error));
        }
    </script>
