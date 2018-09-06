import json
import requests
from bs4 import BeautifulSoup
import pickle
import time


def get_page_two(review_urls):
    '''
    '''
    return [r+'?start=20' for r in review_urls]


def get_page_three(review_urls):
    '''
    '''
    return [r+'?start=40' for r in review_urls]


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
            r = requests.get(url, verify=False)
            soup = BeautifulSoup(r.text, 'html.parser')

            reviews = []
            for item in soup.find_all(class_='review-content'):
                rating = float(item.find('img')['alt'].replace(' star rating',''))
                for p in item.find_all('p',{'lang':'en'}):
                    for br in p.find_all('br'):
                        br.replace_with('\n')
                    reviews.append((rating, p.text))

            rest_dict = {'url': url}
            rest_dict['reviews'] = reviews

            yelp_reviews.append(rest_dict)
            print(len(reviews))
            time.sleep(2)

        except (AttributeError, requests.exceptions.SSLError, requests.ConnectionError, requests.Timeout, KeyboardInterrupt):
            print('error at index ', i)
            continue

    return yelp_reviews


if __name__ == '__main__':

    with open('data/review_urls.pkl', 'rb') as f:
        review_urls = pickle.load(f)

    page_one = get_reviews(review_urls)
    with open('data/reviews_pg1.json', 'w') as f:
        json.dump(page_one, f)
    print('first page reviews scraped')

    urls_2 = get_page_two(review_urls)
    urls_3 = get_page_three(review_urls)

    page_two = get_reviews(urls_2)
    with open('data/reviews_pg2.json', 'w') as f:
        json.dump(page_two, f)
    print('second page reviews scraped')

    page_three = get_reviews(urls_3)
    with open('data/reviews_pg3.json', 'w') as f:
        json.dump(page_three, f)
    print('third page reviews scraped')

    print('all three pages of reviews scraped successfully...we are done!')
