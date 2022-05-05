from tweepy import Stream
from tweepy import OAuthHandler
from tweepy import Stream
from google.cloud import pubsub_v1
import datetime
import os
import json
import base64
import requests

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r"/home/airflow/gcs/data/mykey.json"
client = pubsub_v1.PublisherClient()
pubsub_topic = client.topic_path("iconic-nimbus-348523", "twitterstreaming")

def publish(data_lines):
    messages = []
    for line in data_lines:
        messages.append({'data': line})
    body = {'messages': messages}
    str_body = json.dumps([line])    
    data = base64.urlsafe_b64encode(bytearray(str_body, 'utf8'))    
    pubsub_message = base64.urlsafe_b64decode(data).decode('utf-8')
    try:
        client.publish(topic=pubsub_topic, data=data)
    except:
        print('Faced an issue while publishing')


class TweetStreamListener(Stream):
    """
    A listener handles tweets that are received from the stream.
    This listener dumps the tweets into a PubSub topic
    """

    count = 0
    tweets = []
    batch_size = 1
    total_tweets = 10000

    def write_to_pubsub(self, tweets):
        publish(tweets)

    def on_status(self, status):

        created_at = status.created_at.isoformat()
        id_str = status.id_str
        if not status.truncated:
          text=status.text
        else:
          text=status.extended_tweet['full_text']
        
        source = status.source
        user_name = status.user.name
        user_screen_name = status.user.screen_name
        
        bio = status.user.description
        retweet_count=status.retweet_count
        like_count=status.favorite_count
        reply_count=status.user.followers_count
        longitude = 0
        latitude = 0
        if status.coordinates:
            longitude = status.coordinates['coordinates'][0]
            latitude = status.coordinates['coordinates'][1]
        if ((int(latitude)!=0) & (int(longitude)!=0)):
            loc=str(latitude)+','+str(longitude)
        else:
            loc=status.user.location
        
        tw = dict(text=text, bio=bio, created_at=created_at, tweet_id=id_str,
                    location=loc, user_name=user_name,
                    user_screen_name=user_screen_name,
                    source=source,retweet_count=retweet_count,
                    like_count=like_count,
                    reply_count=reply_count)

            

        self.tweets.append(tw)
        if len(self.tweets) >= self.batch_size:
            self.write_to_pubsub(self.tweets)
            self.tweets = []

        self.count += 1
        if self.count >= self.total_tweets:
            self.disconnect()
            return False
        if (self.count % 100) == 0:
            print("count is: {} at {}".format(self.count, datetime.datetime.now()))
        return True

    def on_timeout(self):
        print("Timeout")
        return True # Don't kill the stream
        print("Stream restarted")


    def on_error(self, status_code):
        print(status_code)
        


def CallAPI():
    print('data stream')
    
    stream_listener = TweetStreamListener("52JbxtgpOY6fLDjsYF5n95ei3", "Zp1lr0kBSiiBQmRlzgeWjUzRcUwKuKWmUNCSvrwjWX3Yu8AR5J","1514798296753008641-QFNgqJQDOqNNToZv6L0EpDMIlzUvfg","A6UG2QAFA8P8ULZC4MiV1ueZLzfg5b2q1m2vtizzMgsAj")
    
    stream_listener.filter(track=['elon','musk','twitter','netflix','facebook','bezos','morgan','stanley','machine','learning','AI','Bigdata'], languages=["en"])


            