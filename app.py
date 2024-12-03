from flask import Flask, request, render_template, redirect, url_for
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploaded_files')

# Google Sheets API authentication
def authenticate_google_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    return client

@app.route('/')
def index():
    return render_template('index.html')                             

@app.route('/submit', methods=['POST'])
def handle_form_submission():
    # Retrieve form data
    date = request.form.get('date')
    productname = request.form.get('productname')
    companyname = request.form.get('companyname')
    status = 'Received' if 'billphoto' in request.files and request.files['billphoto'].filename else 'Pending'

    # Save uploaded file
    billphoto = request.files.get('billphoto')
    billphoto_link = ''
    if billphoto and billphoto.filename:
        filename = billphoto.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        billphoto.save(file_path)
        # Create hyperlink formula for Google Sheets
        billphoto_link = f'=HYPERLINK("file:///{file_path.replace("\\", "/")}", "View Bill")'

    # Append data to Google Sheet
    try:
        client = authenticate_google_sheets()
        sheet = client.open_by_key('1VY_0NnPCTkcXdJeppFY1o4AFERyCBtul2731nkA4MV4').sheet1
        row = [date, productname, companyname, status, billphoto_link]
        sheet.append_row(row, value_input_option='USER_ENTERED')  # Ensures formulas are rendered as clickable
    except Exception as e:
        return f"Error submitting form: {e}"

    # Redirect back to the form page after submission
    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)  # Modify this line to allow access from mobile devices
