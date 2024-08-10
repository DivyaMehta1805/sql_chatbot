import csv
import re

def parse_employee_range(n_employees):
    if not n_employees:
        return None, None
    
    match = re.search(r'(\d+)(?:-(\d+))?', str(n_employees))
    if match:
        lower = int(match.group(1))
        upper = int(match.group(2)) if match.group(2) else lower
        return lower, upper
    
    return None, None

def standardize_revenue(revenue):
    if not revenue:
        return ""
    
    match = re.search(r'(\d+(?:\.\d+)?)\s*(\w+)', str(revenue))
    if match:
        value = float(match.group(1))
        unit = match.group(2).lower()
        
        if unit.startswith('b'):  # billion
            return f"{value * 1000:.2f}"
        elif unit.startswith('m'):  # million
            return f"{value:.2f}"
        elif unit.startswith('k'):  # thousand
            return f"{value / 1000:.2f}"
    
    return revenue

# Read the input CSV file
input_file = 'output.csv'
output_file = 'company_info_updated.csv'

with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.DictReader(infile)
    fieldnames = [f for f in reader.fieldnames if f != 'n_employees'] + ['employee_range_lower', 'employee_range_upper', 'revenue_millions']
    
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        new_row = {k: v for k, v in row.items() if k != 'n_employees'}
        
        lower, upper = parse_employee_range(row.get('n_employees', ''))
        new_row['employee_range_lower'] = lower if lower is not None else ''
        new_row['employee_range_upper'] = upper if upper is not None else ''
        
        new_row['revenue_millions'] = standardize_revenue(row.get('company_revenue', ''))
        
        writer.writerow(new_row)

print(f"Updated data has been written to {output_file}")