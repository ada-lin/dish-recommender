# Menu Cheatsheets NYC
**Galvanize 12 Week Data Science Immersive Program - New York, NY - September 2018**

## Table of Contents
* [Background](#background)
* [Data Collection](#data-collection)
* [Data Cleaning](#data-cleaning)
* [Model Building](#model-building)
  - [Named Entity Recognition](#named-entity-recognition)
  - [Sentiment Analysis](#sentiment-analysis)
* [Data Product](#data-product)
* [Limitations and Future Goals](#limitations-and-future-goals)
* [Tools](#tools)

## Background
As a food enthusiast (I hate the term 'foodie') living in New York, I rely heavily on review aggregator sites to guide my culinary adventures and satisfy my incessant appetite for discovering new restaurants (and for emptying my wallet). In fact, I can't remember the last time I visited a restaurant without checking out its Yelp page first. Like me, many people browse Yelp to help them decide on a place to eat. But even after picking a destination, diners are faced with more choices when sitting down and ordering from a foreign or notoriously long menu of food options (I'm looking at you, The Cheesecake Factory). In such cases, Yelp reviews come in handy again, as they often contain valuable tips from past diners about dishes that they liked or disliked.

The motivation behind my project was to build a machine learning model that would automate the process of manually scouring Yelp reviews for menu item recommendations, so that diners would be able to spend a few more minutes catching up with friends at the table (or flipping through their Instagram feed, as most people these days do anyway). While Yelp did roll out a 'Popular Dishes' feature in June 2018 that attempts to tackle this proposition, it currently does not include information about disliked dishes. My project, on the other hand, reveals both popular and unpopular dishes at each restaurant so that diners can be equally informed about what to order and what to avoid.

The final deliverable for my project is a web app, powered by my algorithm, from which users can look up a restaurant by name and receive a "cheatsheet" page that contains information on the best and worst menu items, according to what reviewers are saying on Yelp. Check it out live by visiting this address in your browser: 18.216.75.143

<img src="img/search_demo.gif" alt="web app demo" width="750"/>

## Data Collection
My project required gathering two sets of data:
1. menu data
2. restaurant reviews

Although Yelp pages contain both menu data and reviews, I found that the menu listings for a  restaurant were often incomplete or outdated. As a result, I decided to gather menu data from a separate source and then match up each menu entry to the restaurant's Yelp page. As the first step of this process, I scraped menupages.com for all available restaurants in New York, NY using BeautifulSoup in Python. I stored the results as a dictionary, which listed information on each restaurant's name, address, phone number and menu items (item name, description and price).

The Yelp data was a bit trickier to collect and required some scrappiness. I initially tried working with their API, named Yelp Fusion, but I was disappointed to find that the endpoint for review data only returns a maximum of three review excerpts per listing, which is way too limited for the scope of my project. I, thus, resorted to scraping the reviews manually from Yelp. Before scraping the reviews, I needed to get the url of each restaurant's Yelp page. To do this, I used Yelp Fusion's phone search endpoint, which returns a list of businesses based on a provided phone number and data about each business, including its Yelp page url. The phone numbers I used to search were the scraped numbers from menupages.com, which also served as a key that I used to match up these two datasets afterwards.

## Data Cleaning
After scraping both menupages.com and Yelp, I had a bit of cleaning and preprocessing to perform in order to join these disparate datasets into one and then start building my model.

The main headache for this part was that the Yelp phone search API sometimes returned multiple listings per number, usually for chain stores that share one phone number or for a new business that replaced a previous one at the same address (and presumably inherited the phone line). My workaround for the latter case was to identify the listing from the API results that had the same restaurant name as that which came from menupages.com. I then dropped the few instances in which none of the Yelp API results matched the menupages.com restaurant name, as these made up less than 2% of the entire dataset.

Another preprocessing step I performed was to remove menu items with prices under $3, as these items corresponded mostly to beverages or small side dishes, which were not the main focus of my recommendation engine.

## Model Building
The model I used to generate my recommendations relied on two techniques in Natural Language Processing: Named Entity Recognition and Sentiment Analysis. I used named entity recognition to identify mentions of menu items in each review and then I relied on sentiment analysis to evaluate whether these items were mentioned in a positive manner or a negative manner.

### Named Entity Recognition
Named entities are terms or phrases that refer to real-world objects that can be denoted with a proper name, such as people, organizations, companies or products. The technique known as Named Entity Recognition (NER) refers to the tagging of these entities in a body of text. Unlike Part-Of-Speech (POS) tagging, which identifies and tags single words according to which grammatical group each belongs to (ie Noun, Adjective, Verb), NER tagging can apply to a group of multiple words such as "The United Nations" and "The Statue of Liberty".

In my data of Yelp review text, I needed to identify phrases that could refer to menu items and specific dishes, which were the named entities in this case. This undertaking would be a simple task if every Yelp reviewer used the proper menu item names to refer to each dish so that I would just need to search the text for exact matches. Natural language is, of course, messier than this and people generally use colloquial or generic phrases to refer to menu items instead of their actual menu names. For example, a review for my favorite Thai spot in the city says, "I personally recommend the pork bbq sticks. That is the best!". While a manual look through the menu would allow us to identify these "pork bbq sticks" as the "Moo Ping Kati Sod" item based on its description ("Grilled coconut milk marinated pork skewers"), it becomes more complicated task to create an algorithm that could do so as well.

There are a few popular models currently used for NER purposes, such as the Conditional Random Field algorithm. I explored some of these options and then ended up relying on my own algorithm that I created based on POS tagging and Tfidf-weighted classification, which I found to work more accurately for my purposes: First, I split up each Yelp review into separate sentences. For each sentence, I filtered out only the entities identified by TextBlob's entity tagger. Next, I trained a Tfidf vectorizer on the corresponding restaurant's menu item names and descriptions. I then fit the vectorizer on each sentence (which, remember, has been filtered to contain only tagged entities) and then computed the cosine similarity for each sentences and menu item combination. Finally, I considered a match between a sentence and a menu item to be when the cosine similarity of the two exceeded 0.6.

### Sentiment Analysis
After picking out the named entities using my matching algorithm, I then needed to calculate how favorably reviewers were speaking about them, a technique that is referred to as sentiment analysis.

Instead of relying on review ratings to determine the polarity of a Yelp review, I wanted to analyze each sentence in the review separately. I chose to do so because I figured that within the same review, a user could mention dishes that they both liked and disliked. Additionally, ratings are influenced by factors other than food satisfaction, such as restaurant service and ambiance. I did not want these factors influencing my dish recommendations, so I chose to analyze only those sentences that mentioned menu items (identified through my NER model).

I calculated the polarities of these sentences by initiating a TextBlob object for each sentence and then using the `sentiment.polarity` attribute from the class. The polarity score ranges from -1 to 1, with positive scores representing favorable attitudes and more negative scores representing the degree of dislike. Since I had previously identified mentions of menu items in each sentence, I determined the ratings of these items by the summed polarity of all sentences in which they were mentioned.

Using these two techniques, I built a class called DishRanker that would analyze the reviews for a restaurant and then rank the menu items accordingly. It then could return the top three and bottom three menu items.

## Data Product
I ran my model on each restaurant in my dataset and then stored the results of the best and worst dishes, as well as some restaurant metadata, on MongoDB. Using Flask and Bootstrap, I created a web app that pulls in data from the MongoDB database and presents my recommendations for each restaurant in a "cheatsheet." To access a cheatsheet for a particular restaurant, a visitor to my website would search for the restaurant by name in the search bar.

<img src="img/search_demo.gif" alt="web app demo" width="750"/>

Additionally, I included an interactive section on the homepage that showcases the top menu items of all restaurants in my dataset, which I called "Crowd Favorites":
<img src="img/crowd_favs.gif" alt="crowd favorites" width="750"/>

Finally, I used an AWS EC2 instance to host my app so that it can be accessed using the public IP address http://18.216.75.143/.

## Limitations and Future Goals
A general limitation of recommendation systems is that they are often difficult to evaluate, especially in the development of a new product, a dilemma that is often referred to as the "cold start" problem. Similarly, I could not rely on a simple metric to evaluate how well my model and menu recommendations performed. For example, to evaluate and pick a model, I resorted to manually choosing a few restaurant samples, reading through their Yelp reviews and then evaluating the recommendations of various models based on my gathered impressions. As a future goal, however, I could fine-tune the final algorithm I created by training my own entity tagger and sentiment polarity calculator using a manually tagged training set.

Given the two-week timeline for my capstone, I had to limit the scope of my project to only consider restaurants in New York City. A future goal would be to expand this product to all restaurants on Yelp in all cities. Additionally, I could personalize the recommendations of each cheatsheet by incorporating a quiz on my website to detect personal preferences and thus, employ collaborative-filtering into my recommendation engine.

## Tools
### Version Control
- Git
- Markdown
- Bash

### Data Collection
- Python packages:
  - BeautifulSoup
  - Requests
  - os

### Data Storage
- MongoDB
- AWS EC2
- JSON
- Python packages:
  - PyMongo
  - pickle

### Natural Language Processing
- Python packages:
  - TextBlob
  - Natural Language Toolkit
  - scikit-learn

### Data Product
- Flask
- Bootstrap
- Jinja2
- HTML
- CSS
- JavaScript
