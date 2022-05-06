from sre_constants import ANY
from numpy import double, empty
from fastapi import FastAPI, Depends,HTTPException,Body
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
from PIL import Image
from auth.model import  UserSchema, UserLoginSchema
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT
import gcsfs
import os
from google.cloud import bigquery
import pandas as pd
import itertools
import json
import requests
from pandas.io import gbq
from textblob import TextBlob
from fastapi.responses import JSONResponse
users = []

app = FastAPI()

class Hashtag(BaseModel):
    tag:str

class res(BaseModel):
    inputtext:str

class User(BaseModel):
    fullname: str
    email: str
    password: str


def read_tweets(tag):
    credentials_path ='cloud_storage_creds.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    client = bigquery.Client()         
    query="SELECT * FROM `iconic-nimbus-348523.twitterstreamingdata.transformedtweets` where text like %tag%"
    QUERY =(
            query
        )
    df = (
        client.query(QUERY)
        .result()
        .to_dataframe()
    )
    return "jst"

def NER(inputtext):
    print('In NER Function')
    ner='No Event/Episode Narratives available for the Event'
    i=0
    while(i<3):
        url = "https://22l4vhw043.execute-api.us-east-1.amazonaws.com/dev/qa"

        payload = json.dumps({"text": inputtext})
        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        print("myresponse")
        print(response)
        if 'timed out' in response.text:
            print('timedout so I try again '+str(i))
            i=i+1
        else:
            jsonresp=response.json()
            ner=jsonresp
            print(ner)
            break
    return ner

def getval(df):
  STATES = ['Alabama', 'AL', 'Alaska', 'AK', 'American Samoa', 'AS', 'Arizona', 'AZ', 'Arkansas', 'AR', 'California', 'CA', 'Colorado', 'CO', 'Connecticut', 'CT', 'Delaware', 'DE', 'District of Columbia', 'DC', 'Federated States of Micronesia', 'FM', 'Florida', 'FL', 'Georgia', 'GA', 'Guam', 'GU', 'Hawaii', 'HI', 'Idaho', 'ID', 'Illinois', 'IL', 'Indiana', 'IN', 'Iowa', 'IA', 'Kansas', 'KS', 'Kentucky', 'KY', 'Louisiana', 'LA', 'Maine', 'ME', 'Marshall Islands', 'MH', 'Maryland', 'MD', 'Massachusetts', 'MA', 'Michigan', 'MI', 'Minnesota', 'MN', 'Mississippi', 'MS', 'Missouri', 'MO', 'Montana', 'MT', 'Nebraska', 'NE', 'Nevada', 'NV', 'New Hampshire', 'NH', 'New Jersey', 'NJ', 'New Mexico', 'NM', 'New York', 'NY', 'North Carolina', 'NC', 'North Dakota', 'ND', 'Northern Mariana Islands', 'MP', 'Ohio', 'OH', 'Oklahoma', 'OK', 'Oregon', 'OR', 'Palau', 'PW', 'Pennsylvania', 'PA', 'Puerto Rico', 'PR', 'Rhode Island', 'RI', 'South Carolina', 'SC', 'South Dakota', 'SD', 'Tennessee', 'TN', 'Texas', 'TX', 'Utah', 'UT', 'Vermont', 'VT', 'Virgin Islands', 'VI', 'Virginia', 'VA', 'Washington', 'WA', 'West Virginia', 'WV', 'Wisconsin', 'WI', 'Wyoming', 'WY']
  for val in STATES:
    if val in df:
      return val
  return ''

def ratio(x):
    print("inside ratio")
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1

@app.get("/")
def read_root():
    return {"message": "Welcome from the twitter API"}

def check_user(data: UserLoginSchema):
    fs = gcsfs.GCSFileSystem(project='My First Project', token = 'cloud_storage_creds.json')
    credentials_path ='cloud_storage_creds.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    client = bigquery.Client()
    table_id = 'iconic-nimbus-348523.Users.login'
    QUERY =(
            "SELECT * FROM `iconic-nimbus-348523.Users.login` ;"
        )
    query_job = client.query(QUERY)  
    rows = query_job.result()  
    for row in rows:
        
        if data.email == row.email and data.password == row.password:
            return True
    return False

def modify_df(df):
    df.drop_duplicates(subset=['tweet_id'],keep='first',inplace=True)
    df[['polarity', 'subjectivity']] = df['text'].apply(lambda Text: pd.Series(TextBlob(Text).sentiment))
    df['location']=df['location'].astype(str)
    df['State'] = df['location'].apply(getval)
    df1=df
    print(df1)
    return df1

def write_to_bq(df):
    credentials_path ='cloud_storage_creds.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    client = bigquery.Client()   
    query=" TRUNCATE table `iconic-nimbus-348523.visualize.dataframe_analysis`"
    QUERY=(
        query
    )
    client.query(QUERY)  

    bigqueryClient = bigquery.Client(project='iconic-nimbus-348523')
    tableRef = bigqueryClient.dataset("visualize").table("dataframe_analysis")
    bigqueryJob = bigqueryClient.load_table_from_dataframe(df, tableRef)
    bigqueryJob.result()
    print(df.shape)

@app.post('/search/',dependencies=[Depends(JWTBearer())], tags=["posts"])
async def search_hashtag(tag: Hashtag):
    print("inside hashtag function")
    #read_tweets(Hashtag.tag)
    credentials_path ='cloud_storage_creds.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    client = bigquery.Client()         
    tag1=tag.tag
    query="SELECT * FROM `iconic-nimbus-348523.twitterstreamingdata.transformedtweets` where lower(text) like lower('%"+tag1+"%')"
    QUERY =(
            query
        )
    df = (
        client.query(QUERY)
        .result()
        .to_dataframe()
    )
    print("This is DF")
    df=modify_df(df)
    write_to_bq(df)
    temp=df.to_json(orient='split',index=False)
    return temp

@app.post("/search/ner",tags=["posts"])
async def ner(input: res):
    print('In NER Function')
    ner='No Event/Episode Narratives available for the Event'
    i=0
    while(i<3):
        url = "https://22l4vhw043.execute-api.us-east-1.amazonaws.com/dev/qa"
        payload = json.dumps({"text": input.inputtext})
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload)
        if 'timed out' in response.text:
            print('timedout so I try again '+str(i))
            i=i+1
        else:
            jsonresp=response.json()
            ner=jsonresp
            break
    return ner

@app.post("/user/signup", tags=["user"])
async def create_user(user: User):
    users.append(user)
    p=signJWT(user.email)
    fs = gcsfs.GCSFileSystem(project='My First Project', token = 'cloud_storage_creds.json')
    credentials_path ='cloud_storage_creds.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    client = bigquery.Client()
    table_id = 'iconic-nimbus-348523.Users.login'
    rows_to_insert = [
        {u'fullname':user.fullname, 
        u'email':user.email, 
        u'password':user.password, 
        u'access_token':p['access_token'],
        u'No_of_Attempts': 0},
    ]
    client.insert_rows_json(table_id, rows_to_insert)  
    return p['access_token']

@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        p=signJWT(user.email)
        return {
            'token': p['access_token']
        }
    return {
        "error": "Wrong login details!"
    }


