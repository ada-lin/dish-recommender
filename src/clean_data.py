import pickle
import json


def clean_data(reviews, menus, urls, biz_data):
    ''' Clean scraped data as well as combine menu and review data
    into one dictionary for each restaurant

    Inputs
    ------------
    reviews: json file of scraped Yelp reviews
    menus: json file of scraped menu data
    urls: pickled list of review page urls
    biz_data: business metadata data from Yelp API search

    Output
    ------------
    cleaned list of dictionaries containing restaurant information, menu data and reviews

    '''

    # Convert menu prices from string to float
    for m in menus:
        for v in m['menu'].values():
            v[1] = float(v[1].replace('$','').replace(',',''))
    # Remove menu items less than $3
    for m in menus:
        m['menu'] = {k:v for k,v in m['menu'].items() if v[1] >= 3}

    # Clean 'reviews' data--
    ## Step 1: remove restaurants with empty review results and adjust the 'urls' list
    ## so that it matches up correctedly with cleaned reviews data
    remove_indices = [i for i, r in enumerate(reviews) if len(r['reviews']) == 0]
    reviews = [i for j, i in enumerate(reviews) if j not in remove_indices]
    urls = [i for j, i in enumerate(urls) if j not in remove_indices]

    ## Step 2: flatten 'businesses' lists from 'biz_data' into one 'lookup' list
    ## and remove utm tags from urls
    lookup = [b['businesses'] for b in biz_data]
    lookup = [b for biz in lookup for b in biz]
    sep = '?adjust_creative'
    for l in lookup:
        l['url'] = l['url'].split(sep)[0]

    ## Step 3: create 'names' and 'phones' lists to update reviews data using 'lookup' list
    names = []
    phones = []
    for url in urls:
        temp_names = []
        temp_phones = []
        for l in lookup:
            if url == l['url']:
                temp_names.append(l['name'])
                temp_phones.append(l['phone'])
        temp_names = list(set(temp_names))
        temp_phones = list(set(temp_phones))
        names.append(temp_names)
        phones.append(temp_phones)

    ## Step 4: add name and phone data to 'reviews'
    for i, r in enumerate(reviews):
        r['name'] = names[i][0]
        r['phone'] = phones[i][0]

    ## Step 5: add corresponding menu data to 'reviews'
    for i, r in enumerate(reviews):
        menu_data = []
        for m in menus:
            if r['phone'] == m['phone']:
                menu_data.append(m)
        r['menu_data'] = menu_data

    ## Step 6: taking care of cases with multiple menu entries per restaurant in 'reviews'
    multiple = [i for i, r in enumerate(reviews) if len(r['menu_data']) > 1]

    for m in multiple:
        lst = reviews[m]['menu_data']
        for l in lst:
            if l['name'].lower().strip() == reviews[m]['name'].lower().strip():
                reviews[m].update({'menu_data': [l]})

    ## Step 7: getting rid of unmatchable menus by restaurant name
    unmatched = [i for i, r in enumerate(reviews) if len(r['menu_data']) > 1 or len(r['menu_data']) == 0]
    reviews_clean = [i for j, i in enumerate(reviews) if j not in unmatched]

    return reviews_clean


if __name__ == '__main__':
    with open('data/reviews_raw.json', 'r') as f:
        reviews = json.load(f)

    with open('data/menus.json', 'r') as f:
        menus = json.load(f)

    with open('data/review_urls.pkl', 'rb') as f:
        urls = pickle.load(f)

    with open('data/biz_data_clean.json', 'r') as f:
        biz_data = json.load(f)

    reviews_clean = clean_data(reviews, menus, urls, biz_data)

    with open('data/reviews_clean.json', 'w') as f:
        json.dump(reviews_clean, f)
