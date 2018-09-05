import json
import os
import requests
from bs4 import BeautifulSoup


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
        print(i, ' of ', len(phone_list))

        params = {'phone': phone}
        r = requests.get('https://api.yelp.com/v3/businesses/search/phone',
                         params=params, headers=headers)
        biz_data.append(r.json())

    return biz_data


def remove_all(lst, val):
    '''Remove all instances of a given value from a list

    Input
    ------------
    lst: list to iterate through
    val: value to remove from list

    Output
    ------------
    None

    '''
    lst[:] = (x for x in lst if x != val)


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
    for biz in biz_data:
        try:
            for listing in biz['businesses']:
                if listing['location']['state'] != 'NY':
                    remove_all(biz['businesses'], listing)
            if len(biz['businesses']) == 0:
                remove_all(biz_data, biz)
        except KeyError:
            remove_all(biz_data, biz)

    return biz_data


def get_urls(biz_data):
    ''' Extract review page URLs from cleaned business metadata

    Input
    ------------
    a list of metadata for restaurants (output of clean_biz_data)

    Output
    ------------
    a list of unduplicated review page URLs

    '''
    review_urls = []
    for biz in biz_data:
        review_urls.append( [biz['businesses'][i]['url'] for i in range(len(biz['businesses'] )) ] )

    # Flatten list and eliminate duplicate URLs:
    review_urls = list(set([url for r in review_urls for url in r]))

    # Clean URLs by removing UTM tags at the end:
    sep = '?adjust_creative'
    clean_urls = [r.split(sep)[0] for r in review_urls]

    return clean_urls


def get_reviews(review_urls):
    ''' Scrape reviews from each page

    Input
    ------------
    a list of URLs to review pages (output of get_urls)

    Output
    ------------
    a list of dictionaries; each dictionary contains values for the keys 'phone'
    and 'reviews'; 'reviews' value is a list of reviews scraped from the first
    page of the restaurant's Yelp page

    '''
    yelp_reviews = []

    for i, url in enumerate(review_urls):
        print(i, ' of ', len(review_urls))

        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')

            phone = soup.find(class_='biz-phone').text.strip().replace('(','+').replace(')','').replace('-','').replace(' ','')

            reviews = []
            for item in soup.find_all(class_='review-content'):
                for p in item.find_all('p',{'lang':'en'}):
                    for br in p.find_all('br'):
                        br.replace_with('\n')
                    reviews.append(p.text)

            rest_dict = {'phone': phone}
            rest_dict['reviews'] = reviews
            rest_dict['url'] = url

            yelp_reviews.append(rest_dict)

        except AttributeError:
            print('error at index ', i)
            continue

    return yelp_reviews


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

    review_urls = get_urls(cleaned_data)
    with open('data/review_urls.pkl', 'wb') as f:
        pickle.dump(review_urls, f)
    print('get review page URLs completed')

    yelp_reviews = get_reviews(review_urls)
    with open('data/reviews.json', 'w') as f:
        json.dump(yelp_reviews, f)
    print('get Yelp reviews completed...done scraping!')
