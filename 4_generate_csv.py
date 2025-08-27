import json
import csv

input_file = 'data-flattened.json'
output_file = 'output3.csv'

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

items = []
for row in data:
    item = {k: row[k] for k in ('Title', 'Artist', 'Venue', 'Dates', 'Time', 'Admission', 'Category', 'Url', 'Latitude', 'Longitude', 'MappingAddress', 'ItemId') if k in row}
    item['Link'] = item.pop('Url')
    item['Latitude'] = item.pop('Latitude')
    item['Longitude'] = item.pop('Longitude')
    item['MapAddr'] = item.pop('MappingAddress')
    item['ItemId'] = item.pop('ItemId')
    items.append(item)

# If the JSON is a list of dicts
if isinstance(items, list):
    
    fieldnames = list(items[0].keys()) if items else []
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item)
else:
    # If the JSON is a dict of dicts or other structure, adjust as needed
    raise ValueError("JSON root is not a list. Please adjust the code for your data structure.")

print(f"CSV file '{output_file}' generated successfully.")