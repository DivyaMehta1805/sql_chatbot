from flask import Flask, request, jsonify
import json
from flask_cors import CORS
from database_api import process
import pandas as pd


app = Flask(__name__)
CORS(app)
last_query_result = None
previous_query = ""
result=""

def custom_json_encoder(obj):
    if isinstance(obj, str):
        return obj.replace('\n', '\\n')
    return obj

app = Flask(__name__)

CORS(app)

@app.route('/api/query', methods=['POST'])
def handle_query():
    global result
    global last_query_result, previous_query
    data = request.json
    query = data.get('query')
    print(f"Received query: {query}")
    
    if query:
        previous_query = query
        result = process(query)
        last_query_result = result  
        return jsonify({'status': 'Query processed'})
    else:
        return jsonify({'status': 'No query received'})

@app.route('/api/result', methods=['GET'])
def get_result():
    if isinstance(result, pd.DataFrame):
        result_list = result.to_dict(orient='records')
        return jsonify({'response': result_list})
    elif result is not None:
        # Use json.dumps with the custom encoder
        return app.response_class(
            json.dumps({'response': result}, default=custom_json_encoder),
            mimetype='application/json'
        )
    else:
        return jsonify({'response': 'No result available'})

def run_flask():
    app.run(debug=True, use_reloader=False, port=6001)

if __name__ == "__main__":
    run_flask()