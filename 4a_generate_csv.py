import json
import csv

input_file = 'data-augmented.json'
output_file = 'result.csv'

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

items = []
for item in data['Items']:
    # print(item.get('EventGuideNumber'), item.get('Title'))
    
    for item_venue in item.get('ProcessedVenues', {}):
        for item_category in item.get('Category', {}):

            if item_category.get('Value') == "Promotions":
                continue # Skip Promotion category      

            title = item.get('Title', '-')
            if len(item.get('ProcessedVenues', {})) > 1:
                title += f" ({item_venue.get('Value')})"
            items.append({
                'Title': title,
                'Latitude': item.get('Latitude', ''),
                'Longitude': item.get('Longitude', ''),
                'MappingAddress': item_venue.get('Address') + ", Central Area, Singapore"
            })

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