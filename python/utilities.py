# utilities.py

import requests
import json as json_lib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

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

    filtered_countries = [country for country in data['data']['countries'] if matches_language_criteria(country, filters)]
    return filtered_countries

def convertJSONtoXML(filters, jsonObj):
    root = ET.Element("queries")

    queries = []
    for lan in filters:
        queries.append({"language": lan})

    qObj = []
    for query in queries:
        current_time_iso = datetime.now(timezone.utc).isoformat(timespec='seconds')
        qObj.append(ET.SubElement(root, "query", language=query["language"], queryTime=current_time_iso))

    for obj in qObj:
        for country in jsonObj:
            for language in country["languages"]:
                if language["code"].lower() == obj.attrib["language"].lower() or language["name"].lower() == obj.attrib["language"].lower():
                    country_element = ET.SubElement(obj, "country")
                    ET.SubElement(country_element, "name").text = country["name"]
                    ET.SubElement(country_element, "continent").text = country["continent"]["name"]
                    ET.SubElement(country_element, "capital").text = country["capital"]
                    break

    tree = ET.ElementTree(root)
    return ET.tostring(root, encoding='unicode')
