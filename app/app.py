from flask import Flask, render_template, request
import pymongo


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cheatsheet', methods=['POST'] )
def display_recs():
    input = str(request.form['restaurant_name'])
    results = list(RECS.find({'name': input}))[0]
    name = results['name']
    yelp_url = results['yelp_url']
    menu_url = results['menu_url']
    phone = results['phone']
    address = results['address']
    best = results['best']
    worst = results['worst']
    return render_template('cheatsheet.html', name=name, yelp=yelp_url, menu=menu_url, phone=phone, address=address, best=best, worst=worst)


if __name__ == '__main__':

    # access database from MongoClient
    client = pymongo.MongoClient()
    db_name = 'nyc_restaurants'
    db = client[db_name]
    collection_name = 'recommendations'
    RECS = db[collection_name]

    app.run(host='0.0.0.0', port=80, debug=True)
