import json
import csv
import copy
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

input_file = 'data-augmented.json'
input_coordinate_ref_file = 'Singapore Night Festival Map Ref.kml'
output_file = 'result.kml'

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
    # Default to some fallback coordinate in Marina Bay if not found
    # We can then import into Google My Maps, adjust the coordinates manually, and re-export the KML as the input_coordinate_ref_file
    return "103.85716,1.27888,0"  

def cleanup_html(raw_html):
    if not raw_html:
        return ""
    # Use BeautifulSoup to clean up HTML
    soup = BeautifulSoup(raw_html, 'html.parser')
    # Remove script and style elements
    for script_or_style in soup(['script', 'style', 'img']):
        script_or_style.decompose()
    # Get text
    #text = soup.get_text(separator='<br>', strip=False)
    return soup.prettify()


def generate_description_content(item, item_venue, item_category):
    content = ""
    if item.get('Artist'):
        content += f"<p><strong>by</strong> {item.get('Artist')}</p>"
    if item.get('Dates'):
        content += f"<p><strong>Dates:</strong> {item.get('Dates')}</p>"
    if item.get('Time'):
        content += f"<p><strong>Time:</strong> {item.get('Time')}</p>"
    if item.get('Admission'):
        content += f"<p><strong>Admission:</strong> {item.get('Admission')}</p>"
    if item_venue:
        content += f"<p><strong>Venue:</strong> {item_venue.get('Value')}</p>"
    # if item_category:
    #     content += f"<p><strong>Category:</strong> {item_category.get('Value')}</p>"
    if item.get('EventGuideNumber'):
        content += f"<p><strong>Event Guide Number:</strong> {item.get('EventGuideNumber')}</p>"
    if item.get('Url'):
        content += f"<p><strong>Link:</strong> https://heritage.sg{item.get('Url')}</p>"
    if item.get('Content'):
        html = item.get('Content').replace('src="/-/media/', 'src="https://heritage.sg/-/media/')
        html = cleanup_html(html)
        content += f"<p>{html}</p>"
    if item.get('ImageSrc'):
        # We don't bother formatting the image here, because Google My Maps will just extract the image for display instead of rendering the full HTML
        content += f'<img src="https://heritage.sg{item.get('ImageSrc')}" alt="Image" style="max-width:200px;"><br>'
    return content

def data_to_kml(data, kml_path):
    kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    doc = ET.SubElement(kml, 'Document')
    name = ET.SubElement(doc, 'name')
    name.text = 'Singapore Night Festival Locations'
    description = ET.SubElement(doc, 'description')
    description.text = 'Locations from Singapore Night Festival 2025'

    category_names = [category['Value'] for category in data['Categories']]
    category_folder_elements = {}
    for category_name in category_names:
        # Create one folder for each category
        folder = ET.SubElement(doc, 'Folder')
        folder_name = ET.SubElement(folder, 'name')
        folder_name.text = category_name
        category_folder_elements[category_name] = folder

    for styles in ['icon_experiential_programmes', 'icon_festival_villages', 'icon_highlight_experiences', 'icon_national_day_activations', 'icon_night_lights', 'icon_performances', 'icon_projection_mapping']:
        # add base template icons
        style = ET.SubElement(doc, 'Style', id=f"{styles}")
        icon_style = ET.SubElement(style, 'IconStyle')
        icon = ET.SubElement(icon_style, 'Icon')
        scale = ET.SubElement(icon_style, 'scale')
        scale.text = "1.0"
        href = ET.SubElement(icon, 'href')
        href.text = f"https://kaiyao-snf2025.s3.ap-southeast-1.amazonaws.com/icons/template/{styles}.png"
        # Add numbered icons
        for number in range(1, 50):
            style = ET.SubElement(doc, 'Style', id=f"{styles}_{number}")
            icon_style = ET.SubElement(style, 'IconStyle')
            icon = ET.SubElement(icon_style, 'Icon')
            scale = ET.SubElement(icon_style, 'scale')
            scale.text = "1.0"
            href = ET.SubElement(icon, 'href')
            href.text = f"https://kaiyao-snf2025.s3.ap-southeast-1.amazonaws.com/icons/generated/{styles}_{number}.png"

    # Sort the items in data['Items'] by EventGuideNumber (if available), then by Title
    data['Items'].sort(key=lambda x: (int(x.get('EventGuideNumber')) if x.get('EventGuideNumber') is not None else 99999, x.get('Title').lower()))

    for item in data['Items']:
        # print(item.get('EventGuideNumber'), item.get('Title'))
        
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
                placemark_content = generate_description_content(item, item_venue, item_category)
                desc.text = str(placemark_content)
                point = ET.SubElement(placemark, 'Point')
                coords = ET.SubElement(point, 'coordinates')
                coords.text = get_coordinates_from_kml(input_coordinate_ref_file, title)
                #coords.text = f"{item['Longitude']},{item['Latitude']},0"

                styleUrl = ET.SubElement(placemark, 'styleUrl')
                if item_category.get('Value') == "Experiential Programmes":
                    if item.get('EventGuideNumber'):
                        styleUrl.text = f"#icon_experiential_programmes_{item.get('EventGuideNumber', '1')}"
                    else:
                        styleUrl.text = f"#icon_experiential_programmes"
                elif item_category.get('Value') == "Festival Villages":
                    if item.get('EventGuideNumber'):
                        styleUrl.text = f"#icon_festival_villages_{item.get('EventGuideNumber', '1')}"
                    else:
                        styleUrl.text = f"#icon_festival_villages"
                elif item_category.get('Value') == "Highlight Experiences":
                    if item.get('EventGuideNumber'):
                        styleUrl.text = f"#icon_highlight_experiences_{item.get('EventGuideNumber', '1')}"
                    else:
                        styleUrl.text = f"#icon_highlight_experiences"
                elif item_category.get('Value') == "National Day Activations":
                    if item.get('EventGuideNumber'):
                        styleUrl.text = f"#icon_national_day_activations_{item.get('EventGuideNumber', '1')}"
                    else:
                        styleUrl.text = f"#icon_national_day_activations"
                elif item_category.get('Value') == "Night Lights":
                    if item.get('EventGuideNumber'):
                        styleUrl.text = f"#icon_night_lights_{item.get('EventGuideNumber', '1')}"
                    else:
                        styleUrl.text = f"#icon_night_lights"
                elif item_category.get('Value') == "Performances":
                    if item.get('EventGuideNumber'):
                        styleUrl.text = f"#icon_performances_{item.get('EventGuideNumber', '1')}"
                    else:
                        styleUrl.text = f"#icon_performances"
                elif item_category.get('Value') == "Projection Mapping":
                    if item.get('EventGuideNumber'):
                        styleUrl.text = f"#icon_projection_mapping_{item.get('EventGuideNumber', '1')}"
                    else:
                        styleUrl.text = f"#icon_projection_mapping"

                # extended = ET.SubElement(placemark, 'ExtendedData')
                # for key, value in item.items():
                #    if key not in ['Title', 'Content', 'Latitude', 'Longitude']:
                #        data_elem = ET.SubElement(extended, 'Data', name=key)
                #        value_elem = ET.SubElement(data_elem, 'value')
                #        value_elem.text = str(value)
                
                # extended = ET.SubElement(placemark, 'ExtendedData')
                # for key, value in item.items():
                #    if key in ['Artist', 'Venue', 'Dates', 'Time', 'Admission']:
                #        data_elem = ET.SubElement(extended, 'Data', name=key)
                #        value_elem = ET.SubElement(data_elem, 'value')
                #        value_elem.text = str(value)

    tree = ET.ElementTree(kml)
    ET.indent(tree, space="\t", level=0)
    tree.write(kml_path, encoding='utf-8', xml_declaration=True)



with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

data_to_kml(data, output_file)

print(f"KML file '{output_file}' generated successfully.")