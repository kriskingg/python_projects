import os
import io
from flask import Flask, render_template, request, send_from_directory, jsonify
import pandas as pd

app = Flask(__name__)

# Directory to save uploaded and processed files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    """Render the main page with upload and text input options."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and deduplication."""
    if 'file' not in request.files:
        return jsonify({"message": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    try:
        # Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Read the file and remove duplicates
        df = pd.read_csv(file_path)
        cleaned_df = df.drop_duplicates()

        # Save the deduplicated file
        deduplicated_file_path = os.path.join(
            app.config['UPLOAD_FOLDER'], f"deduplicated_{file.filename}")
        cleaned_df.to_csv(deduplicated_file_path, index=False)

        return render_template('deduplicate.html', filename=f"deduplicated_{file.filename}")

    except Exception as e:
        return jsonify({"message": f"Error processing file: {str(e)}"}), 500


@app.route('/process_text', methods=['POST'])
def process_text():
    """Handle text input deduplication."""
    try:
        # Get the input text
        text_data = request.form.get("text", "")
        if not text_data.strip():
            return jsonify({"message": "No text provided"}), 400

        # Convert the text into a DataFrame, assuming it is CSV-like
        data_io = io.StringIO(text_data)
        df = pd.read_csv(data_io)

        # Remove duplicates
        cleaned_df = df.drop_duplicates()

        # Convert back to CSV format
        output = io.StringIO()
        cleaned_df.to_csv(output, index=False)
        output.seek(0)

        return render_template('deduplicate_text.html', deduplicated_data=output.getvalue())
    except Exception as e:
        return jsonify({"message": f"Error processing text: {str(e)}"}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Serve the deduplicated file for download."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/instructions')
def instructions():
    """Render the instructions page."""
    return render_template('instructions.html')


@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
