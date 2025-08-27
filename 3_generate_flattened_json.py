import json
import csv

input_file = 'data-combined.json'
output_file = 'data-flattened.json'

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

items = data['Items']

# If the JSON is a list of dicts
if isinstance(items, list):

    data2 = []
    formatted_items = []
    for item in items:
        # Helper to concatenate list of dicts into a string using 'Value'
        def concat_values(val):
            if isinstance(val, list):
                return ', '.join(str(d.get('Value', '')) for d in val if isinstance(d, dict))
            return val.get('Value', '') if isinstance(val, dict) else str(val) if val else ''

        item['Venue'] = [item['Venue']]
        #print(item)

        # Custom fixes for specific items with multiple venues
        if item.get('Title') == 'All Things Singapore (AT SG) 2025':
            item['Venue'] = [
                {'Value': 'National Library Building', 'Address': 'National Library Building'}, 
                {'Value': 'National Archives of Singapore', 'Address': 'National Archives of Singapore'}
            ]
        if item.get('Title') == 'The Island Dreamer - A Wander-Wonder Experience':
            item['Venue'] = [
                {'Value': 'Reflection Pool at Bras Basah MRT Station', 'Address': '65 Bras Basah Rd'}, 
                {'Value': 'Waterloo Centre Artspace', 'Address': 'Waterloo Centre Artspace'}
            ]
        if item.get('Title') == 'Bugis Night Lights':
            item['Venue'] = [
                {'Value': 'Bugis Junction', 'Address': 'Bugis Junction'}, 
                {'Value': 'Bugis+', 'Address': 'Bugis+'},
                {'Value': 'Bugis Street', 'Address': 'Bugis Street'}
            ]

        item_duplicate_count = 0
        for item_venue in item.get('Venue', {}):
            for item_category in item.get('Category', {}):
                formatted_item = {
                    'Title': item.get('Title', ''),
                    'Artist': item.get('Artist', ''),
                    'Venue': item_venue.get('Value', ''),
                    'Dates': item.get('Dates', ''),
                    'Time': item.get('Time', ''),
                    'Admission': item.get('Admission', ''),
                    'Category': item_category.get('Value', ''),
                    'ItemId': item.get('ItemId', '') + '-' + str(item_duplicate_count),
                    'OriginalItemId': item.get('ItemId', ''),
                    'Url': 'https://www.heritage.sg' + item.get('Url', ''),            
                    'Content': item.get('Content', ''),
                    'ImageSrc': 'https://www.heritage.sg' + item.get('ImageSrc', ''),
                    'ImageAlt': item.get('ImageAlt', ''),            
                    'Latitude': item.get('Latitude', ''),
                    'Longitude': item.get('Longitude', ''),
                    'MappingAddress': item_venue.get('Address') + ", Central Area, Singapore",
                }

                # Append venue to title if multiple venues exist
                if len(item.get('Venue', {})) > 1:
                    formatted_item['Title'] += f" ({item_venue.get('Value')})"

                formatted_items.append(formatted_item)
                item_duplicate_count += 1

    for item in formatted_items:
        if item['Latitude'] == '' and item['Longitude'] == '':
            # item['Latitude'] = '1.293034'
            # item['Longitude'] = '103.843740'
            pass
        else:
            item['MappingAddress'] = "" # Clear address if coordinates are present so that Google Maps does not get confused
else:
    # If the JSON is a dict of dicts or other structure, adjust as needed
    raise ValueError("JSON root is not a list. Please adjust the code for your data structure.")

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(formatted_items, f, indent=2)