import requests
import logging
from requests.auth import HTTPBasicAuth
import shutil
from xml.dom import minidom
import xml.etree.ElementTree as ET

h = '2b1ba156-2f73-48e1-b5ec-180127f54a53'
loc = "POLYGON((8.89 47.79,13.42 48.54,16.90 48.68,16.97 46.67,9.58 47.09,8.89 47.79))"


def get_product_name_from_uuid(uuid):
    url = "https://scihub.copernicus.eu/dhus/odata/v1/Products('%s')/Name/$value" % (uuid)
    response = requests.get(url, auth=HTTPBasicAuth('ouassim', '747400Co'))
    print(response.text)
    return response.text


def download_product_quick_look(uuid):
    product_name = get_product_name_from_uuid(uuid)
    product_name += '.SAFE'
    url = "https://scihub.copernicus.eu/dhus/odata/v1/Products('%s')/Nodes('%s')/Nodes('preview')/Nodes('quick-look.png')/$value" % (
        uuid, product_name)
    print(url)
    response = requests.get(url, auth=HTTPBasicAuth('ouassim', '747400Co'))
    with open(uuid + '.png', 'wb') as f:
        f.write(response.content)
    return response


def download_product_tiff(uuid):
    product_name = get_product_name_from_uuid(uuid)
    product_name_lower = product_name.lower()
    product_name += '.SAFE'
    print(product_name_lower)
    product_name_lower.replace("_", "-")
    product_name_lower += '-001.tiff'
    url = "https://scihub.copernicus.eu/dhus/odata/v1/Products('%s')/$value" % (uuid)
    print(url)
    response = requests.get(url, auth=HTTPBasicAuth('ouassim', '747400Co'), stream=True)
    with open(uuid + '.zip', 'wb') as f:
        i = 1
        for chunk in response.iter_content(chunk_size=1024):
            i += 1
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                print(i * 1024)
    return response


def get_product_list_by_time_location(date, polygon):
    url = "https://scihub.copernicus.eu/dhus/search?start=0&rows=100&q="
    location_filter = 'footprint:"Intersects(%s)"' % polygon
    type_filter = "producttype:GRD"
    date_filter = "beginposition:[NOW-1MONTHS TO NOW] AND endposition:[NOW-1MONTHS TO NOW]"
    filter = location_filter + " AND " + type_filter + " AND " + date_filter
    url += filter
    print(url)
    response = requests.get(url, auth=HTTPBasicAuth('ouassim', '747400Co'))
    print(response.text)
    return response.text


def get_all(date, polygon):
    xml = get_product_list_by_time_location('133', loc)
    tree = ET.ElementTree(ET.fromstring(xml))
    root = tree.getroot()
    i = 1
    for node in root.findall('{http://www.w3.org/2005/Atom}entry'):
        uuid = node.find('{http://www.w3.org/2005/Atom}id').text
        print("*" * 40)
        print(i)
        i += 1
        print(uuid)
        # print(node.find('{http://www.w3.org/2005/Atom}str[@name="gmlfootprint"]').text)
        # print(node.find('{http://www.opengis.net/gml/srs/epsg.xml#4326}coordinates').text)
        s = node.find('{http://www.w3.org/2005/Atom}str[@name="footprint"]').text
        s = s[s.find("(") + 2:s.find(")")]
        list_1 = s.split(",")
        print(list_1)
        list_2 = []
        for item in list_1:
            tmp_list = item.split(" ")
            list_2.append(tmp_list)
        print(list_2)
        print(list_2[1][1])
        # download_product_quick_look(uuid)
        # download_product_tiff(uuid)
    return tree


get_all(h, loc)
