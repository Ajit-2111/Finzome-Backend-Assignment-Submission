from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    """Check if the file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def calculate_volatility(data, input_type):
    """
       Calculate daily and annualized volatility for a given dataset.

       Parameters:
       - data (str): The file path or directory path depending on the input type.
       - input_type (str): The type of input, either 'file' or 'directory'.

       Returns:
       - df (pd.DataFrame): The DataFrame containing the input data.
       - daily_volatility (float): The calculated daily volatility.
       - annualized_volatility (float): The calculated annualized volatility.
    """
    if input_type == 'file':
        if isinstance(data, str) and data.endswith('.csv'):
            # If input is a file path, read data from the CSV file
            df = pd.read_csv(data)
        else:
            return jsonify({'error': 'Invalid file format. Use CSV files only.'})
    elif input_type == 'directory':
        # If input is a directory path, fetch data from files in the directory
        if data.endswith('.csv') and os.path.exists(data):
            df = pd.read_csv(data)
        else:
            return jsonify({'error': 'Invalid file format or file not found.'})

    else:
        raise ValueError("Invalid input type. Use either 'file' or 'directory'.")
    df.columns = [c.strip() for c in df.columns.values.tolist()]
    # Calculate daily returns
    df['Daily Returns'] = (df['Close'] / df['Close'].shift(1)) - 1

    # Calculate daily volatility
    daily_volatility = df['Daily Returns'].std()

    # Calculate annualized volatility (length of dataset as trading days per year)
    annualized_volatility = daily_volatility * np.sqrt(len(df))
    return df, daily_volatility, annualized_volatility


@app.route('/', methods=['GET'])
def index():
    """Render the index.html page."""
    return render_template('index.html')


@app.route('/calculate_volatility', methods=['POST'])
def calculate_volatility_endpoint():
    """
        Endpoint to calculate volatility based on user input.

        Returns:
        - JSON response containing calculated volatility values and DataFrame records.
    """
    input_type = request.form.get('inputType')
    file = request.files.get('file')
    directory = request.form.get('directory')

    if input_type == 'file':
        # If 'file' key is present, it means a file was uploaded
        if file and allowed_file(file.filename):
            # Save the file to the UPLOAD_FOLDER
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Now use the file path for further processing
            data = filepath
        else:
            return jsonify({'error': 'Invalid file format. Use CSV files only.'})
    elif input_type == 'directory':
        # If 'directory' key is present, it means a directory parameter was provided
        data = directory
    else:
        return jsonify({'error': 'No data provided'})

    # Calculate volatility
    result_df, daily_volatility, annualized_volatility = calculate_volatility(data, input_type)

    # Create a dictionary for the response
    response_dict = {
        'data': result_df.to_dict(orient='records'),
        'daily_volatility': daily_volatility,
        'annualized_volatility': annualized_volatility
    }

    return jsonify(response_dict)


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
