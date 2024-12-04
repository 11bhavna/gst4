from flask import Flask, request, render_template, redirect, url_for
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__,template_folder='/var/www/html/gst4/gst4/templates')

# Configure server upload folder and public URL

SERVER_UPLOAD_FOLDER = 'var/www/html/gst4/gst4/templates'  # Replace with the actual server folder path
SERVER_UPLOAD_FOLDER1='var/www/html/gst4/gst4'
SERVER_PUBLIC_URL = 'http://167.71.237.12:5000'  # Replace with the actual server public URL

# Google Sheets API authentication
def authenticate_google_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
    ]
    file_path = os.path.join(SERVER_UPLOAD_FOLDER1)
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

    # Save uploaded file to the server
    billphoto = request.files.get('billphoto')
    billphoto_link = ''
    if billphoto and billphoto.filename:
        filename = billphoto.filename
        file_path = os.path.join(SERVER_UPLOAD_FOLDER, filename)
        billphoto.save(file_path)  # Save the file to the server
        # Create a public URL for the uploaded file
        billphoto_link = f'=HYPERLINK("{SERVER_PUBLIC_URL}{filename}", "View Bill")'

    # Append data to Google Sheet
    try:
        client = authenticate_google_sheets()
        sheet = client.open_by_key('1wNnP_GCw9fQMKDER8ug8TwIVKa59g257P5WJY2MJq6w').sheet1
        row = [date, productname, companyname, status, billphoto_link]
        sheet.append_row(row, value_input_option='USER_ENTERED')  # Ensures formulas are rendered as clickable
    except Exception as e:
        return f"Error submitting form: {e}"

    # Redirect back to the form page after submission
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure the server upload folder exists
    os.makedirs(SERVER_UPLOAD_FOLDER, exist_ok=True)
    app.run(host='167.71.237.12', port=5000, debug=True) 
