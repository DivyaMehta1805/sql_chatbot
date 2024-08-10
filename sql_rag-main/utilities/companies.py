import json
import csv
def csv_to_json(csv_file_path, json_file_path):
    # Read the CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = list(csv_reader)

    # Convert to JSON
    json_data = json.dumps(data, indent=2)

    # Write JSON to file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(json_data)

    print(f"Conversion complete. JSON data written to {json_file_path}")

# Usage
csv_file_path = 'event_info_updated.csv'  # Replace with your CSV file path
json_file_path = 'events.json'  # Replace with your desired output JSON file path

csv_to_json(csv_file_path, json_file_path)