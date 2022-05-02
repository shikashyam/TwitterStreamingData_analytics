
import apache_beam as beam
import argparse
from apache_beam.options.pipeline_options import PipelineOptions
from sys import argv
import re

PROJECT_ID = 'iconic-nimbus-348523'
SCHEMA = 'text:STRING,created_at:STRING,tweet_id:STRING,location:STRING,user_screen_name:STRING,source:STRING,retweet_count:INTEGER,like_count:INTEGER,reply_count:INTEGER'


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

def cleantext(data):
    
    data['text'] = data['text'].lower()
    data['text'] = re.sub(r"rt[\s]+", "", data['text']) # Remove Retweets
    data['text'] = re.sub(r"http\S+", "", data['text'])
    data['text'] = re.sub(r"www.\S+", "", data['text'])
    data['text'] = re.sub('[():#@]', ' ', data['text'])
    data['text']=clean(data['text'], no_emoji=True)
    return data


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    known_args = parser.parse_known_args(argv)

    p = beam.Pipeline(options=PipelineOptions())

    (p | 'ReadData' >> beam.io.ReadFromText('gs://beampipeline1/inputdata.csv', skip_header_lines =1)
       | 'SplitData' >> beam.Map(lambda x: x.split(','))
       | 'FormatToDict' >> beam.Map(lambda x: {"text": x[0], "bio": x[1], "created_at": x[2], "tweet_id": x[3], "location": x[4], "user_name": x[5], "user_screen_name": x[6], "source": x[7], "retweet_count": x[8], "like_count": x[9], "reply_count": x[10]}) 
       | 'ChangeDataType' >> beam.Map(convert_types)
       | 'DeleteUnwantedData' >> beam.Map(del_unwanted_cols)
       | 'CleanUpTweets' >> beam.Map(clean_tweets)
       | 'WriteToBigQuery' >> beam.io.WriteToBigQuery(
           '{0}:twitterstreamingdata.transformedtweets'.format(PROJECT_ID),
           schema=SCHEMA,
           write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND))
    
    result = p.run()