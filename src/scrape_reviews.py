import json
import os
import requests


def get_phone_numbers(json_file):
    ''' Extract phone numbers from json file that contains scraped menu data

    Input
    ------------
    json_file: path to the json file that contains the menu data scraped from menupages.com

    Output
    ------------
    a list of phone numbers for each restaurant

    '''
    with open(json_file) as f:
        data = json.load(f)

    return [restaurant['phone'] for restaurant in data]


def get_yelp_biz_data(phone_list):
    ''' Use the Yelp Fusion API to search for business information based on phone number

    Input
    ------------
    a list of phone numbers to use as search queries (output of get_phone_numbers)

    Output
    ------------
    a list of API responses

    '''
    headers = {'Authorization': 'bearer %s' % os.environ['YELP_API_KEY']}
    biz_data = []
    for i, phone in enumerate(phone_list):
        print(i)
        params = {'phone': phone}
        r = requests.get('https://api.yelp.com/v3/businesses/search/phone',
                         params=params, headers=headers)
        biz_data.append(r.json())

    return biz_data


def clean_biz_data(biz_data):
    ''' Cleans get_yelp_biz_data output by removing restaurants not in NY
    and empty search results from API response

    Input
    ------------
    a list of raw API responses (output of get_yelp_biz_data)

    Output
    ------------
    a cleaned list of metadata for relevant restaurants

    '''
    for i, biz in enumerate(biz_data):
        for j, listing in enumerate(biz['businesses']):
            if listing['location']['state'] != 'NY':
                print(listing['location']['state'])
                del biz['businesses'][j]
        if len(biz['businesses']) == 0:
            del biz_data[i]

    return biz_data


def get_urls(biz_data):





if __name__ == '__main__':
    phone_list = get_phone_numbers('data/menus.json')
    print('get phone numbers completed')

    biz_data = get_yelp_biz_data(phone_list)
    with open('data/biz_data.json', 'w') as f:
        json.dump(biz_data, f)
    print('get Yelp business data completed')

    cleaned_data = clean_biz_data(biz_data)
    with open('data/cleaned_biz_data.json', 'w') as f:
        json.dump(biz_data, f)
    print('clean business data completed')
