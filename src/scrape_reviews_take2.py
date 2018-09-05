import json
import requests
from bs4 import BeautifulSoup
import pickle


def get_more_pages(review_urls):
    '''
    '''
    page2_urls = [r+'?start=20' for r in review_urls]
    page3_urls = [r+'?start=40' for r in review_urls]
    return (page2_urls + page3_urls)

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

        except AttributeError:
            print('error at index ', i)
            continue

    return yelp_reviews


if __name__ == '__main__':

    with open('data/review_urls.pkl', 'rb') as f:
        review_urls = pickle.load(f)

    all_urls = get_more_pages(review_urls)

    yelp_reviews = get_reviews(all_urls)

    with open('data/reviews_take2.json', 'w') as f:
        json.dump(yelp_reviews, f)

    print('get Yelp reviews completed...done scraping!')
