import numpy as np
from textblob import Textblob
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class DishRanker(object):
    '''
    '''

    def __init__(self, similarity_threshold=0.6):
        '''
        similarity_threshold: threshold for matches based on cosine similaritiy
        '''
        self.similarity_threshold = similarity_threshold

    def fit(reviews, menu):
        '''
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
        '''
        n: number of top items to return
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

        return names, descriptions, prices


    def worst_items(self, n=3):
        '''
        n: number of worst items to return
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

        return names, descriptions, prices
