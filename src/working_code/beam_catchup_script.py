
import apache_beam as beam
import argparse
from apache_beam.options.pipeline_options import PipelineOptions
from sys import argv
import re


PROJECT_ID = 'iconic-nimbus-348523'
SCHEMA = 'text:STRING,created_at:STRING,tweet_id:STRING,location:STRING,user_screen_name:STRING,source:STRING,retweet_count:INTEGER,like_count:INTEGER,reply_count:INTEGER'
table_spec = 'iconic-nimbus-348523:twitterstreamingdata.streamingdataset'



def convert_types(data):
    """Converts string values to their appropriate type."""
    
    data['retweet_count'] = int(data['retweet_count']) if 'retweet_count' in data else None
    data['like_count'] = int(data['like_count']) if 'like_count' in data else None
    data['reply_count'] = int(data['reply_count']) if 'reply_count' in data else None
    
    return data

def del_unwanted_cols(data):
    """Delete the unwanted columns"""
    del data['bio']
    del data['user_name']
    return data

def clean_tweets(data):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        "]+", re.UNICODE)

    data['text'] = data['text'].lower()
    data['text'] = re.sub(r"rt[\s]+", "", data['text']) # Remove Retweets
    data['text'] = re.sub(r"http\S+", "", data['text'])
    data['text'] = re.sub(r"www.\S+", "", data['text'])
    data['text'] = re.sub('[():#@]', ' ', data['text'])
    data['text'] = re.sub(emoj, '', data['text'])
    return data


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    known_args = parser.parse_known_args(argv)

    p = beam.Pipeline(options=PipelineOptions())

    (p | 'ReadTable' >> beam.io.ReadFromBigQuery(query='SELECT * FROM '\
              '[iconic-nimbus-348523:twitterstreamingdata.streamingdataset]')
       | 'ChangeDataType' >> beam.Map(convert_types)
       | 'DeleteUnwantedData' >> beam.Map(del_unwanted_cols)
       | 'CleanUpTweets' >> beam.Map(clean_tweets)
       | 'WriteToBigQuery' >> beam.io.WriteToBigQuery(
           '{0}:twitterstreamingdata.transformedtweets'.format(PROJECT_ID),
           schema=SCHEMA,
           write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND))
    
    result = p.run()