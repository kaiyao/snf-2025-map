import requests
import json
from datetime import date, timedelta

items_dict = {}

start_date = date(2025, 8, 22)
end_date = date(2025, 9, 6)

current_date = start_date
while current_date <= end_date:
    date_string = current_date.strftime('%m/%d/%Y')
    print(f"Processing date {date_string}...")

    date_string_file = current_date.strftime('%Y-%m-%d')

    with open(f'data-{date_string_file}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

        items = data['Items']
        for item in items:
            items_dict[item['ItemId']] = item

    current_date += timedelta(days=1)

own_format_data = data
own_format_data['Items'] = list(items_dict.values())
own_format_data['TotalCount'] = len(own_format_data['Items'])
with open(f'data-combined.json', 'w', encoding='utf-8') as f:
    json.dump(own_format_data, f, indent=2)