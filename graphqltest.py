import requests
import json as json_lib
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from datetime import datetime, timezone
from flask import Flask, render_template, request
import requests

url = "https://countries.trevorblades.com/"

json_query = {'query': '''
{
  countries() {
    name
    continent {
      name
    }
    capital
    languages {
      code
      name
    }
  }
}
'''}

# Set your filter criteria
# filter_code = "pt" # Change this to the language code you want
# filter_name = "Portuguese" # Change this to the language name you want

# filters = ["pt","english"]

def requestCountry(filters):
    r = requests.post(url, json=json_query)
    data = r.json()

    def matches_language_criteria(country, filters):
        if filters is None or len(filters) == 0:
            return True
        for language in country['languages']:
            for f in filters:
                if str(language['code']).lower() == str(f).lower() or str(language['name']).lower() == str(f).lower():
                    return True
        return False

    # Filter countries
    filtered_countries = [country for country in data['data']['countries'] if matches_language_criteria(country, filters)]

    print(json_lib.dumps(filtered_countries, indent=2))
    return filtered_countries

def convertJSONtoXML(filters, jsonObj):
    root = ET.Element("queries")

    queries = []
    for lan in filters:
        queries.append({"language": lan})

    qObj = []
    for query in queries:
        current_time_iso = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        qObj.append(ET.SubElement(root, "query", language=query["language"], queryTime=current_time_iso))

    for obj in qObj:
        for country in jsonObj:
            for language in country["languages"]:
                if language["code"].lower() == obj.attrib["language"].lower() or language["name"].lower() == obj.attrib["language"].lower():
                    country_element = ET.SubElement(obj, "country")
                    ET.SubElement(country_element, "name").text = country["name"]
                    ET.SubElement(country_element, "continent").text = country["continent"]["name"]
                    ET.SubElement(country_element, "capital").text = country["capital"]
                    break # Exit the language loop once a match is found

    tree = ET.ElementTree(root)
    tree.write("output.xml", encoding='utf-8', xml_declaration=True)

    # Parse the XML file
    #tree = ET.parse('your_file.xml')
    #root = tree.getroot()

    # Get a string representation of the XML
    xml_str = ET.tostring(root, encoding='unicode')

    # Parse the string with minidom and pretty print
    pretty_xml = parseString(xml_str).toprettyxml()

    # Print the pretty XML
    print(pretty_xml)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

filterInput = input("Please input what languages you wish to search for: ")
filters = filterInput.split(',')
filters = [item.strip() for item in filters]
convertJSONtoXML(filters, requestCountry(filters))
