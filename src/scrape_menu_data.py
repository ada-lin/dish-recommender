import requests
from bs4 import BeautifulSoup
import json


def get_site_pages(page_list, n_pages):
    ''' Get URLs for all pages that list NYC restaurant menus on menupages.com

    Inputs
    ------------
    page_list: a list whose first element is the URL of the first listing page
    n_pages: the number of total listing pages

    Output
    ------------
    page_list populated with all listing page URLs

    '''
    for i in range(2, n_pages+1):
        page_list.append('https://menupages.com/restaurants/ny-new-york/'+str(i))

    return page_list


def get_menu_urls(page_list):
    ''' Extracts the URLs of restaurant menus from each listing page on menupages.com

    Input
    ------------
    page_list: a list containing the URLs of all listing pages (output of get_site_pages)

    Output
    ------------
    a list of all URLs that link to restaurant menus

    '''
    menu_urls = []
    for page in page_list:
        r = requests.get(page)
        txt = r.text
        soup = BeautifulSoup(txt, 'html.parser')
        for item in soup.find_all(class_='restaurant__title'):
            menu_urls.append('https://menupages.com'+item.find('a')['href'])

    return menu_urls


def scrape_menu_data(menu_urls):
    ''' Scrape relevant data from each restaurant's menu page

    Input
    ------------
    menu_urls: a list containing the URLs of all restaurant menus (output of get_menu_urls)

    Output
    ------------
    a list of dictionaries, with each dictionary describing an individual restaurant;
    dictionaries contain data on the restaurant's name, address, phone number and
    menu items (a nested dictionary with item name as keys and with item description,
    if any, and price as values)

    '''
    restaurant_list = []
    for menu in menu_urls:
        r = requests.get(menu)
        txt = r.text
        soup = BeautifulSoup(txt, 'html.parser')

        name = soup.find_all(class_='header__restaurant-name')
        # Case when a listing has expired for a closed restaurant:
        if len(name) == 0:
            continue

        restaurant = {}
        restaurant['name'] = name[0].text.strip()
        restaurant['address'] = soup.find_all(class_='header__restaurant-address')[0].text.strip()
        restaurant['phone'] = soup.find_all(class_='restaurant-phone')[0].find('a')['href'].replace('tel:','')

        print(restaurant['name'])

        menu_items = {}
        for item in soup.find_all(class_='menu-item'):
            dish = item.find(class_='menu-item__title').text
            if item.find(class_='menu-item__description') is None:
                descr = ''
            else:
                descr = item.find(class_='menu-item__description').text.strip()
            price = item.find(class_='menu-item__price').text.replace('+','').strip()
            menu_items[dish] = (descr, price)

        restaurant['menu'] = menu_items
        restaurant_list.append(restaurant)

    return restaurant_list


if __name__ == '__main__':
    page_list = get_site_pages(['https://menupages.com/restaurants/ny-new-york'], 86)
    print('get site pages completed')

    menu_urls = get_menu_urls(page_list)
    print('get menu urls completed')

    restaurant_list = scrape_menu_data(menu_urls)
    with open('data/menus.json', 'w') as f:
        json.dump(restaurant_list, f)
