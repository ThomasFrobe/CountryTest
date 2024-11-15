# app.py

from flask import Flask, request, render_template, jsonify
from utilities import requestCountry, convertJSONtoXML

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    filters = request.form['languages'].split(',')
    filters = [item.strip() for item in filters]

    json_data = requestCountry(filters)
    xml_data = convertJSONtoXML(filters, json_data)
    
    response = {
        'json': json_data,
        'xml': xml_data
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
