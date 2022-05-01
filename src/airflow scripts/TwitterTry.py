from tweepy import Stream
from tweepy import OAuthHandler
from tweepy import Stream
from google.cloud import pubsub_v1
import datetime
import os
import json
import base64
import requests

class TweetStreamListener(Stream):
    """
    A listener handles tweets that are received from the stream.
    This listener dumps the tweets into a PubSub topic
    """
    client = pubsub_v1.PublisherClient()
    pubsub_topic = client.topic_path("iconic-nimbus-348523", "twitterstreaming")
    count = 0
    tweets = []
    batch_size = 1
    total_tweets = 8000

    def write_to_pubsub(self, tweets):
        publish(self.client, self.pubsub_topic, tweets)

    def on_status(self, status):


         # Converting the time to isoformat for serialisation
        created_at = status.created_at.isoformat()
        id_str = status.id_str
        if not status.truncated:
          text=status.text
        else:
          text=status.extended_tweet['full_text']
        # text = status.text
        source = status.source
        user_name = status.user.name
        user_screen_name = status.user.screen_name
        loc = status.user.location
        bio = status.user.description
        # cantidad=data1.public_metrics.retweet_count


     
        # api-endpoint
        URL = "https://api.twitter.com/2/tweets?ids="+id_str+"&tweet.fields=public_metrics&expansions=attachments.media_keys&media.fields=public_metrics"

        # defining a params dict for the parameters to be sent to the API
        #PARAMS = {'ids': '1417669885665054722', 'tweet.fields': 'public_metrics', 'expansions': 'attachments.media_keys', 'media.fields': 'public_metrics'}

        token_twitter= 'AAAAAAAAAAAAAAAAAAAAAGUbbgEAAAAAZUBSiSMcCmZ6kzwlR%2FVT%2F%2B%2FdeXE%3DLkIm7zXOr3VkDP66zpMJbBKFMnJl0HkSijliHynixMccffeJi0'
        headersAuth = {
        'Authorization': 'Bearer ' + str(token_twitter)
        }

        # sending get request and saving the response as response object
        r = requests.get(url = URL, headers = headersAuth)

        # extracting data in json format
        data1 = r.json()

        
        if 'data' in data1:            

            for i in data1['data']:

                tw = dict(text=text, bio=bio, created_at=created_at, tweet_id=id_str,
                    location=loc, user_name=user_name,
                    user_screen_name=user_screen_name,
                    source=source,retweet_count=i['public_metrics']['retweet_count'],
                    like_count=i['public_metrics']['like_count'],
                    reply_count=i['public_metrics']['reply_count'])
                

            self.tweets.append(tw)
            if len(self.tweets) >= self.batch_size:
                self.write_to_pubsub(self.tweets)
                print(self.tweets)
                self.tweets = []

            self.count += 1
            if self.count >= self.total_tweets:
                return False
            if (self.count % 5) == 0:
                print("count is: {} at {}".format(self.count, datetime.datetime.now()))
            return True




    def on_error(self, status_code):
        print(status_code)


if __name__ == '__main__':
    print('data stream')
    stream_listener = TweetStreamListener("52JbxtgpOY6fLDjsYF5n95ei3", "Zp1lr0kBSiiBQmRlzgeWjUzRcUwKuKWmUNCSvrwjWX3Yu8AR5J","1514798296753008641-QFNgqJQDOqNNToZv6L0EpDMIlzUvfg","A6UG2QAFA8P8ULZC4MiV1ueZLzfg5b2q1m2vtizzMgsAj")
    stream_listener.filter(track=['elon','musk','twitter'], languages=["en"])