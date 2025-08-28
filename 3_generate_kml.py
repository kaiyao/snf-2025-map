import json
import csv
import copy
import xml.etree.ElementTree as ET

input_file = 'data-combined.json'
input_coordinate_ref_file = 'Singapore Night Festival 2025 (2).kml'
input_style_ref_file = 'Singapore Night Festival 2025 (2).kml'
output_file = 'data-combined.kml'

def get_coordinates_from_kml(kml_path, placemark_name):
    tree = ET.parse(kml_path)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    for placemark in root.findall('.//kml:Placemark', ns):
        name_elem = placemark.find('kml:name', ns)
        #print(f"Trying to match {placemark_name} against {name_elem.text}")
        if name_elem is not None and name_elem.text.strip() == placemark_name.strip():
            #print("Matched!")
            coords_elem = placemark.find('.//kml:coordinates', ns)
            if coords_elem is not None:
                coords_text = coords_elem.text.strip()
                return coords_text
    
    print("No match found for placemark:", placemark_name)            
    return None

def data_to_kml(data, kml_path):
    kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    doc = ET.SubElement(kml, 'Document')
    name = ET.SubElement(doc, 'name')
    name.text = 'Singapore Night Festival Locations'
    description = ET.SubElement(doc, 'description')
    description.text = 'Locations from Singapore Night Festival 2025'

    # Copy styles and styleMaps from reference KML, removing namespace
    ref_kml = ET.parse(input_style_ref_file)
    ref_root = ref_kml.getroot()
    ref_ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    ref_doc = ref_root.find('kml:Document', ref_ns)
    
    def strip_ns(tag):
        return tag.split('}', 1)[-1] if '}' in tag else tag

    if ref_doc is not None:
        for elem in ref_doc:
            tag_no_ns = strip_ns(elem.tag)
            if tag_no_ns in ['Style', 'StyleMap']:
                # Deep copy and strip namespace from all descendants
                def strip_ns_tree(e):
                    e.tag = strip_ns(e.tag)
                    for child in e:
                        strip_ns_tree(child)
                elem_copy = copy.deepcopy(elem)
                strip_ns_tree(elem_copy)
                doc.append(elem_copy)

    category_names = [category['Value'] for category in data['Categories']]
    category_folder_elements = {}
    for category_name in category_names:
        # Create one folder for each category
        folder = ET.SubElement(doc, 'Folder')
        folder_name = ET.SubElement(folder, 'name')
        folder_name.text = category_name
        category_folder_elements[category_name] = folder

    for item in data['Items']:
        
        for item_venue in item.get('ProcessedVenues', {}):
            for item_category in item.get('Category', {}):

                if item_category.get('Value') == "Promotions":
                    continue # Skip Promotion category               

                parent_element = category_folder_elements.get(item_category.get('Value'))

                placemark = ET.SubElement(parent_element, 'Placemark')

                title = item.get('Title', '-')
                if len(item.get('ProcessedVenues', {})) > 1:
                    title += f" ({item_venue.get('Value')})"

                name = ET.SubElement(placemark, 'name')
                name.text = str(title)
                desc = ET.SubElement(placemark, 'description')
                desc.text = str(item.get('Content'))
                point = ET.SubElement(placemark, 'Point')
                coords = ET.SubElement(point, 'coordinates')
                coords.text = get_coordinates_from_kml(input_coordinate_ref_file, title)
                #coords.text = f"{item['Longitude']},{item['Latitude']},0"

                # extended = ET.SubElement(placemark, 'ExtendedData')
                # for key, value in item.items():
                #    if key not in ['Title', 'Content', 'Latitude', 'Longitude']:
                #        data_elem = ET.SubElement(extended, 'Data', name=key)
                #        value_elem = ET.SubElement(data_elem, 'value')
                #        value_elem.text = str(value)
                extended = ET.SubElement(placemark, 'ExtendedData')
                for key, value in item.items():
                   if key in ['Artist', 'Venue', 'Dates', 'Time', 'Admission']:
                       data_elem = ET.SubElement(extended, 'Data', name=key)
                       value_elem = ET.SubElement(data_elem, 'value')
                       value_elem.text = str(value)

    tree = ET.ElementTree(kml)
    ET.indent(tree, space="\t", level=0)
    tree.write(kml_path, encoding='utf-8', xml_declaration=True)



with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

data_to_kml(data, output_file)

print(f"KML file '{output_file}' generated successfully.")