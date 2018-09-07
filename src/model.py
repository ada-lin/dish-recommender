import json
import numpy as np
from textblob import TextBlob
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pymongo
from pymongo import ASCENDING, DESCENDING


class DishRanker(object):
    '''A DishRanker class to find the best and worst dishes for a restaurant,
    based on Yelp reviews.

    Attributes
    ------------
    similarity_threshold: float; threshold for matches based on cosine similaritiy
    reviews: list of str; reviews of the restaurant
    menu: dictionary; menu data for the restaurant
    items: list of str; menu item names
    polarities: numpy array; polarity or sentiment scores of items
    rankings: numpy array; indices of ranked items by polarity in descending order

    Methods
    ------------
    fit: fit the DishRanker object
    best_items: return the top dishes of the restaurant
    worst_items: return the worst dishes of the restaurant

    '''

    def __init__(self, similarity_threshold=0.6):
        ''' Initialize a DishRanker object.

        Input
        ------------
        similarity_threshold: float; threshold for determining matches based on cosine similaritiy

        '''
        self.similarity_threshold = similarity_threshold

    def fit(self, reviews, menu):
        ''' Fit a DishRanker object.

        Inputs
        ------------
        reviews: list of str; reviews of the restaurant
        menu: dictionary; menu data for the restaurant

        '''
        self.reviews = reviews
        self.menu = menu

        # parse reviews by tokenizing sentences and then flattening list of sentences
        sentences = [sent_tokenize(r) for r in self.reviews]
        sentences = [s for sent in sentences for s in sent]

        # extract noun phrases from each sentence
        nps = []
        for sent in sentences:
            token = TextBlob(sent)
            tags = token.noun_phrases
            nps.append(' '.join(t for t in list(tags)))

        # extract menu item names and fit a tfidf vectorizer to items
        self.items = list(self.menu.keys())
        vect = TfidfVectorizer(stop_words='english')
        menu_tfidf = vect.fit_transform(self.items)

        # construct tfidf matrix for review sentences using the vectorizer
        review_tfidf = vect.transform(nps)

        # compute cosine similarities between review sentences and menu items
        sim_mat = cosine_similarity(menu_tfidf, review_tfidf)

        # classify a match as when the similarity metric exceeds threshold
        matches = np.argwhere(sim_mat > self.similarity_threshold)

        self.polarities = np.zeros(len(self.items))
        for i, sent_index in enumerate(matches[:,1]):
            tb = TextBlob(sentences[sent_index])
            self.polarities[matches[i][0]] += tb.sentiment.polarity

        self.rankings = np.argsort(self.polarities)[::-1]


    def best_items(self, n=3):
        ''' Find the most popular dishes for the restaurant.

        Input
        ------------
        n: number of top items to return

        Output
        ------------
        list of top n dishes; each element of the list is a tuple
        describing the menu item name, its description and price

        '''
        # find the indicies of menu items that have the top n polarity scores
        best = self.rankings[:n]

        # only return items in top n that have positive scores
        check = [self.polarities[b] > 0 for b in best]
        best = best[check]

        # find names, descriptions and prices of top items
        names = [self.items[b] for b in best]
        descriptions = [self.menu[n][0] for n in names]
        prices = [self.menu[n][1] for n in names]

        return list(zip(names, descriptions, prices))


    def worst_items(self, n=3):
        ''' Find the least popular dishes for the restaurant.

        Input
        ------------
        n: number of worst items to return

        Output
        ------------
        list of worst n dishes; each element of the list is a tuple
        describing the menu item name, its description and price

        '''
        # find the indicies of menu items that have the bottom n polarity scores
        worst = self.rankings[-n:]

        # only return items in bottom n that have negative scores
        check = [self.polarities[w] < 0 for w in worst]
        worst = worst[check]

        # find names, descriptions and prices of worst items
        names = [self.items[w] for w in worst]
        descriptions = [self.menu[n][0] for n in names]
        prices = [self.menu[n][1] for n in names]

        return list(zip(names, descriptions, prices))


if __name__ == '__main__':

    # set up MongoClient instance
    client = pymongo.MongoClient()
    db_name = 'nyc_restaurants'
    db = client[db_name]
    db.drop_collection('recommendations')
    collection_name = 'recommendations'
    RECS = db[collection_name]
    RECS.create_index([('name', ASCENDING)], unique=False)

    # Load 'reviews' data
    with open('data/reviews_clean.json', 'rb') as f:
        data = json.load(f)

    # Pickle list of restaurant names, to be used in web app
    restaurant_names = [d['menu_data'][0]['name'] for d in data]
    with open('data/restaurant_names.pkl', 'wb') as f:
        pickle.dump(restaurant_names, f)

    # Run model on each restaurant in dataset and store results to MongoDB
    for i, d in enumerate(data):
        print(i, 'of', len(data))

        review = [r[1] for r in d['reviews']]
        menu = d['menu_data'][0]['menu']
        rest_name = d['menu_data'][0]['name']
        rest_address = d['menu_data'][0]['address']
        rest_phone = d['menu_data'][0]['phone']
        rest_url = d['url']

        try:
            dr = DishRanker()
            dr.fit(review, menu)
            best = dr.best_items()
            worst = dr.worst_items()

            mongo_insert = {'name': rest_name,
                            'yelp_url': rest_url,
                            'phone': rest_phone,
                            'address': rest_address,
                            'best': best,
                            'worst': worst}

            RECS.insert_one(mongo_insert)

        except ValueError:
            print('ValueError at index', i)
            continue
