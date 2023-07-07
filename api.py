import requests
import time
import xml.etree.ElementTree as ET

last_reset_time = time.time()
request_count = 0


def handle_response(response):
    global request_count,last_reset_time
    request_count += 1
    if request_count >= 45:
        current_time = time.time()
        if current_time - last_reset_time < 60:
            # Wait for the remaining time until a minute has passed
            wait_time = 60 - (current_time - last_reset_time)
            time.sleep(wait_time)
            last_reset_time = time.time()

        # Reset the request count
        request_count = 0
        last_reset_time = time.time()
    if response.status_code == 200:
        try:
            content_type = response.headers.get('Content-Type', '')
            if 'json' in content_type:
                if not response.content:
                    return []
                return response.json()
            elif 'xml' in content_type:
                if not response.content:
                    return []
                xml_root = ET.fromstring(response.content)
                # Process the XML data and return the desired result
                return xml_root
            else:
                print("Unsupported content type:", content_type)
                return []
        except requests.exceptions.RequestException as e:
            print("Request error:", e)
            return []
        except ValueError as e:
            print("Error decoding JSON:", e)
            return []
        except ET.ParseError as e:
            print("Error parsing XML:", e)
            return []
    elif response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 5))
        time.sleep(retry_after)
        # need to call function another time or just make a window that hit 429
    else:
        print('Error occurred:', response)
        return None


def extract_results(data):
    if data is not None:
        return data['results']
    else:
        return []

def get_specific_series(seriesid):
    url=f'https://api.mangaupdates.com/v1/series/{seriesid}'
    response = requests.get(url)
    data = handle_response(response)
    if data is not None:
        extracted_result = {
            'url': data['url']
        }
        return extracted_result
    else:
        return []

def get_group_scanlating(seriesid):
    url=f'https://api.mangaupdates.com/v1/series/{seriesid}/groups'
    response = requests.get(url)
    data = handle_response(response)
    if data is not None:
        extracted_result = {
            'groups': data['group_list']
        }
        return extracted_result
    else:
        return []

def getlastchapterofmanga(seriesid,groupname):
    url=f'https://api.mangaupdates.com/v1/series/{seriesid}/rss'
    response = requests.get(url)
    data = handle_response(response)
    if data is not None:
        channel = data.find('channel')
        if channel.find('item') is not None: # if there's chapters and chapter is from needed group it returns last chapter added by them
            for item in channel.findall('item'):
                if item.find('description').text == groupname:
                    return item.find('title').text
        else:
            return None
    else:
        return []

def search_manga(search_query,numpage):
    url = 'https://api.mangaupdates.com/v1/series/search'
    payload = {
        "search": search_query,
        "stype": "title",
        "page": numpage,
        "perpage": 5,
        "pending": True
    }
    response = requests.post(url, json=payload)
    data = handle_response(response)

    if data is not None:
        results = data['results']
        extracted_results = []
        for result in results:
            extracted_result = {
                'series_id': result['record']['series_id'],
                'title': result['record']['title'],
                'url': result['record']['url'],
                'thumb': result['record']['image']['url']['original']
            }
            extracted_results.append(extracted_result)
        return extracted_results
    else:
        return []

# Define other API functions here