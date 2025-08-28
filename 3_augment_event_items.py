import requests
import json
from datetime import date, timedelta

items_dict = {}

input_file = 'data-combined.json'
output_file = 'data-augmented.json'

event_number_list = []
import csv
with open('data-event-numbers.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        event_number_list.append(row)

print(event_number_list)


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
    if item.get('Title') == "Waterloo Street Stories by #WaterlooStKakis":
        return [
            {'Value': 'Waterloo Street', 'Address': 'Waterloo Street'}, 
        ]
    return [item['Venue']]


def process_complex_event(item):
    # For complex events which are actually multiple separate events, split them up
    if item.get('Title') == "Waterloo Street Stories by #WaterlooStKakis":
        item1 = item.copy()
        item1['Title'] = "Waterloo Street Stories: Outdoor Photo Exhibition"
        item1['Artist'] = "Objectifs"
        item1['Venue'] = {'Value': 'Courtyard, Objectifs', 'Address': 'Objectifs'}
        item1['Dates'] = "22 Aug to 06 Sep"
        item1['Time'] = "Tues to Thurs 12pm to 7pm | Fri & Sat 12pm to 9pm | Sun 12pm to 4pm (closed Mondays)"
        item2 = item.copy()
        item2['Title'] = "Waterloo Street Stories: Photography series by Isaiah Cheng"
        item2['Artist'] = "SMU-ACM"
        item2['Venue'] = {'Value': 'Back courtyard of Stamford Arts Centre', 'Address': 'Stamford Arts Centre'}
        item1['Dates'] = "22 Aug to 06 Sep"
        item1['Time'] = ""
        # There are actually 6 items under the listing for Waterloo Street Stories, 
        # but the rest already have their own separate listings in the JSON
        return [item1, item2]


event_numbers_used = []

def add_event_number(item):
    if item.get('Category')[0].get('Value') == "Promotions":
        return # Skip Promotion category as those are not in the event guide

    # Add event number if multiple dates
    for event in event_number_list:
        if item.get('Title').lower().startswith(event[1].lower()):
            event_numbers_used.append(event[0])
            return event[0]
    print("No event number found for:", item.get('Title'))

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

    items = data['Items']

    # Split items if they are complex (i.e. actually multiple events)
    new_items = []
    for item in items:
        complex_events = process_complex_event(item)
        if complex_events:
            new_items.extend(complex_events)
    # Delete old complex events
    items = [item for item in items if not process_complex_event(item)]
    # Add new split-up events
    items.extend(new_items)
    
    for item in items:
        item['ProcessedVenues'] = process_venue(item)
        item['EventGuideNumber'] = add_event_number(item)

    data['Items'] = items

# Recount the total count
own_format_data = data
own_format_data['TotalCount'] = len(own_format_data['Items'])
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(own_format_data, f, indent=2)

# Debug to see which event numbers are missing
event_numbers_used.sort(key=lambda x: '{0:0>8}'.format(x).lower())
print("Event numbers used:", event_numbers_used)