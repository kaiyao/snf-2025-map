import requests
import json
from datetime import date, timedelta

items_dict = {}

start_date = date(2025, 8, 22)
end_date = date(2025, 9, 6)

current_date = start_date

def process_venue(item):
    # Custom fixes for specific items with multiple venues
    if item.get('Title') == 'All Things Singapore (AT SG) 2025':
        return [
            {'Value': 'National Library Building', 'Address': 'National Library Building'}, 
            {'Value': 'National Archives of Singapore', 'Address': 'National Archives of Singapore'}
        ]
    if item.get('Title') == 'The Island Dreamer - A Wander-Wonder Experience':
        return [
            {'Value': 'Reflection Pool at Bras Basah MRT Station', 'Address': '65 Bras Basah Rd'}, 
            {'Value': 'Waterloo Centre Artspace', 'Address': 'Waterloo Centre Artspace'}
        ]
    if item.get('Title') == 'Bugis Night Lights':
        return [
            {'Value': 'Bugis Junction', 'Address': 'Bugis Junction'}, 
            {'Value': 'Bugis+', 'Address': 'Bugis+'},
            {'Value': 'Bugis Street', 'Address': 'Bugis Street'}
        ]
    if item.get('Title') == "Nila\u2019s Shimmering Shores \u2013 An Immersive Story Room Adventure":
        return [
            {'Value': "Children's Museum Singapore", 'Address': "Children's Museum Singapore"}, 
        ]
    return [item['Venue']]

while current_date <= end_date:
    date_string = current_date.strftime('%m/%d/%Y')
    print(f"Processing date {date_string}...")

    date_string_file = current_date.strftime('%Y-%m-%d')

    with open(f'data-{date_string_file}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

        items = data['Items']
        for item in items:
            item_id = item['ItemId']
            if item_id not in items_dict:
                # Augment the item with extracted dates and venues
                item['ProcessedEventDates'] = [current_date.strftime('%Y-%m-%d')]
                item['ProcessedVenues'] = process_venue(item)
                items_dict[item_id] = item
            else:
                items_dict[item_id]['ProcessedEventDates'].append(current_date.strftime('%Y-%m-%d'))

    current_date += timedelta(days=1)

own_format_data = data
own_format_data['Items'] = list(items_dict.values())
own_format_data['TotalCount'] = len(own_format_data['Items'])
with open(f'data-combined.json', 'w', encoding='utf-8') as f:
    json.dump(own_format_data, f, indent=2)