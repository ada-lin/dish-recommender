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
    for phone in phone_list:
        params = {'phone': phone}
        r = requests.get('https://api.yelp.com/v3/businesses/search/phone',
                         params=params, headers=headers)
        biz_data.append(r.json())
    return biz_data


def get_review_page_urls(biz_data)







if __name__ == '__main__':
    phone_list = get_phone_numbers('data/menus_new.json')
    biz_data = get_yelp_biz_data(phone_list)
