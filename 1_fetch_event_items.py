import requests
import json
from datetime import date, timedelta

start_date = date(2025, 8, 22)
end_date = date(2025, 9, 6)

current_date = start_date
while current_date <= end_date:
    date_string = current_date.strftime('%m/%d/%Y')
    print(f"Fetching date {date_string}...")

    page_count = 1
    page_result_count = 9
    items = []

    while page_result_count > 0:
        print(f"Fetching Page {page_count}...")
        r = requests.post('https://www.heritage.sg/custom/snf2022/api/handlers/SnfWhatsOnListingHandler.ashx?archive=false', data={
            'page': page_count,
            'q': '',
            'category': 'All Categories',
            'venue': 'All Venues',
            'accessibility': 'All Accessibility',
            'date': date_string
            })

        data = r.json()
        page_result_count = data['TotalCount']
        print(f"{page_result_count} items fetched")

        items.extend(data['Items'])

        page_count += 1

    #print(page_items)
    date_string_file = current_date.strftime('%Y-%m-%d')

    own_format_data = data
    own_format_data['Items'] = items
    own_format_data['TotalCount'] = len(items)
    with open(f'data-{date_string_file}.json', 'w', encoding='utf-8') as f:
        json.dump(own_format_data, f, indent=2)

    current_date += timedelta(days=1)