from flask import Flask, request, jsonify
from flask_cors import CORS
from database_api import process
import pandas as pd
app = Flask(__name__)
CORS(app)
last_query_result = None
previous_query = ""
result=""
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
        return jsonify({'response': result})
    else:
        return jsonify({'response': 'No result available'})

def run_flask():
    app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    run_flask()