from sre_constants import ANY
from numpy import double, empty
from sqlite3 import Date
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Optional, List
import configparser
import tweepy
from textblob import TextBlob
import pandas as pd
import re
import nltk
nltk.download('stopwords')
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from nltk.corpus import stopwords 
from io import BytesIO
from starlette.responses import StreamingResponse

app = FastAPI()

class Hashtag(BaseModel):
    tag:str

def authorization():
    api_key = 'NP7v43PRlKcEWbH5b9fuCYnfq'
    api_key_secret = 'QX6KzoA5y3vdo3VND4aYecyLplregpphgGiO030RUyq9T9F1fK'
    access_token = '3237471510-Q56fvogIyQfo23ixDiRSQ1T1VvgFJbDxc3oKLdd'
    access_token_secret = 'oEzvfHnS1QRPFwTmFE7cPrNXChOo9OUunrhsS2BwM6NnA'
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

def search(tag):
    #authorization()
    api_key = 'NP7v43PRlKcEWbH5b9fuCYnfq'
    api_key_secret = 'QX6KzoA5y3vdo3VND4aYecyLplregpphgGiO030RUyq9T9F1fK'
    access_token = '3237471510-Q56fvogIyQfo23ixDiRSQ1T1VvgFJbDxc3oKLdd'
    access_token_secret = 'oEzvfHnS1QRPFwTmFE7cPrNXChOo9OUunrhsS2BwM6NnA'
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    df = pd.DataFrame(columns=('tweet_text', 'tweet_sentiment', 'tweet_subjectivity',
                           'user_followers_count', 'user_friends_count',
                           'user_account_age', 'user_verified',
                           'user_favourites_count', 'user_tweets',
                           'tweet_retweeted', 'tweet_retweet_count', 'tweet_favorite_count'))
    # Remove duplicates
    df.sort_values("tweet_text", inplace = True) 
    df.drop_duplicates(subset ="tweet_text", keep = False, inplace = True) 
    tweets = api.search_tweets(tag, count=100)
    for tweet in tweets:
        sentimentText = TextBlob(tweet.text)
        df = df.append({'tweet_text': re.sub(r'http\S+', '', tweet.text), # Removing any URL's in the tweet text here
                        'tweet_sentiment': sentimentText.sentiment.polarity,
                        'tweet_subjectivity': sentimentText.sentiment.subjectivity,
                        'user_followers_count': tweet.user.followers_count, 
                        'user_friends_count': tweet.user.friends_count,
                        'user_account_age': tweet.user.created_at, 
                        'user_verified': tweet.user.verified,
                        'user_favourites_count': tweet.user.favourites_count,
                        'user_tweets': tweet.user.statuses_count,
                        'tweet_retweeted': tweet.retweeted,
                        'tweet_retweet_count': tweet.retweet_count,
                        'tweet_favorite_count': tweet.favorite_count},
                    ignore_index=True) 
    stop_words = stopwords.words('english') 
    new_stopwords = ['RT']
    stop_words.extend(new_stopwords)
    stop_words = set(stop_words)


    text = " ".join(review for review in df.tweet_text)
    clean_text = " ".join(word for word in text.split() if word not in stop_words)

    #print ("There are {} words in all tweets.".format(len(text)))
    #print ("There are {} words in  all tweets with stopwords removed.".format(len(clean_text)))

    wordcloud = WordCloud(background_color="white").generate(clean_text)

    plt.figure( figsize=(15,7))
    plt.axis("off")
    plt.imshow(wordcloud, interpolation='bilinear')
    return df.iloc[0]



@app.get("/")
def read_root():
    return {"message": "Welcome from the twitter API"}


@app.post('/search/')
async def search_hashtag(hash: Hashtag):
    return search(hash.tag)
