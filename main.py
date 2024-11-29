from flask import Flask, jsonify, request
import pandas as pd
import io

app = Flask(__name__)

# Root URL
@app.route('/')
def home():
    return "Welcome to Remove Duplicates Service! Use the /remove_duplicates endpoint."

# Remove duplicates endpoint
@app.route('/remove_duplicates', methods=['POST'])
def remove_duplicates():
    file = request.files['file']
    df = pd.read_csv(file)
    cleaned_df = df.drop_duplicates()
    output = io.StringIO()
    cleaned_df.to_csv(output, index=False)
    output.seek(0)
    return jsonify({"message": "Success", "data": output.getvalue()})

if __name__ == "__main__":
    app.run(debug=True)
