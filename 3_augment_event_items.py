import requests
import json
from datetime import date, timedelta

items_dict = {}

input_file = 'data-combined.json'

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
        item2 = item.copy()
        item2['Title'] = "A Sundried Time Capsule: Collage & Mark-Making Workshop"
        item2['Artist'] = "Objectifs"
        item2['Venue'] = {'Value': 'Annexe, Objectifs', 'Address': 'Objectifs'}
        item3 = item.copy()
        item3['Title'] = "Fortune Hands"
        item3['Artist'] = "P71:SMA"
        item3['Venue'] = {'Value': 'Courtyard, Objectifs', 'Address': 'Objectifs'}
        item4 = item.copy()
        item4['Title'] = "Sound Plot Audio Plays Series"
        item4['Artist'] = "Centre 42"
        item4['Venue'] = {'Value': 'Stamford Arts Centre', 'Address': 'Stamford Arts Centre'}
        item5 = item.copy()
        item5['Title'] = "Photography series"
        item5['Artist'] = "Isaiah Cheng"
        item5['Venue'] = {'Value': 'Back courtyard of Stamford Arts Centre', 'Address': 'Stamford Arts Centre'}
        item6 = item.copy()
        item6['Title'] = "Waterloo Street Stories: Familiar Strangers"
        item6['Artist'] = "SMU-ACM"
        item6['Venue'] = {'Value': 'Stamford Arts Centre L1 Project Studio', 'Address': 'Stamford Arts Centre'}
        return [item1, item2, item3, item4, item5, item6]
    
    return None

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

with open(f'data-combined-augmented.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

# Debug to see which event numbers are missing
event_numbers_used.sort(key=lambda x: '{0:0>8}'.format(x).lower())
print("Event numbers used:", event_numbers_used)