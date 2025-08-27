import json
import csv
import xml.etree.ElementTree as ET

input_file = 'data-flattened.json'
output_file = 'output3.kml'

def dicts_to_kml(data, kml_path):
    kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    doc = ET.SubElement(kml, 'Document')
    name = ET.SubElement(doc, 'name')
    name.text = 'Singapore Night Festival Locations'
    description = ET.SubElement(doc, 'description')
    description.text = 'Locations from Singapore Night Festival 2025'

    for item in data:
        placemark = ET.SubElement(doc, 'Placemark')
        name = ET.SubElement(placemark, 'name')
        name.text = str(item.get('Title', '-'))
        desc = ET.SubElement(placemark, 'description')
        desc.text = str(item.get('Content'))
        point = ET.SubElement(placemark, 'Point')
        coords = ET.SubElement(point, 'coordinates')
        coords.text = f"{item['Longitude']},{item['Latitude']},0"

        extended = ET.SubElement(placemark, 'ExtendedData')
        for key, value in item.items():
            if key not in ['Title', 'Content', 'Latitude', 'Longitude']:
                data_elem = ET.SubElement(extended, 'Data', name=key)
                value_elem = ET.SubElement(data_elem, 'value')
                value_elem.text = str(value)

    tree = ET.ElementTree(kml)
    ET.indent(tree, space="\t", level=0)
    tree.write(kml_path, encoding='utf-8', xml_declaration=True)



with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

items = data

# If the JSON is a list of dicts
if isinstance(items, list):    
    dicts_to_kml(items, output_file)
else:
    # If the JSON is a dict of dicts or other structure, adjust as needed
    raise ValueError("JSON root is not a list. Please adjust the code for your data structure.")

print(f"KML file '{output_file}' generated successfully.")