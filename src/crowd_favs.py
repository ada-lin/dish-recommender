from src.model import *
import json

def get_crowd_favorites(reviews_data):

    all_items = []
    for i, d in enumerate(reviews_data):
        print(i, 'of', len(reviews_data))

        review = [r[1] for r in d['reviews']]
        menu = d['menu_data'][0]['menu']
        rest_name = [d['menu_data'][0]['name']] * len(menu)

        dr = DishRanker()
        dr.fit(review, menu)

        all_items.append(list(zip(rest_name, dr.items, dr.polarities)))

    all_items = [item for restaurant in all_items for item in restaurant]
    all_polarities = [a[2] for a in all_items]
    ranked = np.argsort(all_polarities)
    top_items = [all_items[index] for index in ranked[::-1][:500]]

    return top_items


if __name__ == '__main__':

    with open('data/reviews_clean.json', 'r') as f:
        data = json.load(f)

    top_items = get_crowd_favorites(data)

    print('Top menu items of all restaurants, ranked in descending order:', top_items)
