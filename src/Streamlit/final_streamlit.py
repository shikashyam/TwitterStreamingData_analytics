import streamlit as st
import os
from google.cloud import bigquery
import gcsfs
import requests
from PIL import Image
from datetime import date,datetime
import streamlit.components.v1 as components
import json
import re
import pandas as pd
import time
from streamlit_option_menu import option_menu
import hydralit_components as hc
import matplotlib.pyplot as plt
from wordcloud import WordCloud

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.sidebar.image("https://raw.githubusercontent.com/shikashyam/TitanicSurvivalPrediction/main/image2vector.svg", use_column_width=True)
st.title("Social Media Campaign Analytics")
with st.expander("About the App"):
     st.write("""
         The next era of social media marketing is here and it is driven by social media. As more and more organizations move to this trend of social media marketing, there is a recognizable gap in understanding audience response to these campaigns. The leadership level still looks to see sales metrics and quarter-on-quarter growth and familiar metrics which is not explained in terms of hashtag and mention counts.

Our project aims to bridge this gap by creating a pipeline which derives valuable intelligence from social media and visualize metrics that determine the success or failure of marketing campaigns based on social media chatter.
     """)

def TopEntities(results):
  Orgs=[]
  Pers=[]

  for ner in results:
    for key in ner.keys():
      if ('ORG' in key) & ('#' not in ner[key]) & (bool(re.match('^[a-zA-Z0-9]*$',ner[key]))) & (len(ner[key])>1):
        Orgs.append(ner[key])
      if ('LOC' in key) & ('#' not in ner[key]) & (bool(re.match('^[a-zA-Z0-9]*$',ner[key]))) & (len(ner[key])>1):
        Pers.append(ner[key])
  if len(Orgs)!=0:
    TopOrg=max(set(Orgs), key=Orgs.count)
  else:
    TopOrg='None'
  
  if len(Pers)!=0:
    TopPer=max(set(Pers), key=Pers.count)
  else:
    TopPer='None'
  print(Orgs)
  print(Pers)
  return TopOrg,TopPer

def display(tweet_url):
     api="https://publish.twitter.com/oembed?url={}".format(tweet_url)
     response=requests.get(api)
     res = response.json()["html"] 
     return res

def tweet(df2):
     df3=df2.loc[df2['reply_count'] == df2['reply_count'].max()]
     print("inside tweet function")
     print(df3['tweet_id'])
     return df3

def NER(inputtext):
    inputtext=inputtext[0:500]
    print('In NER Function')
    ner='No Event/Episode Narratives available for the Event'
    i=0
    while(i<3):
        url = "https://22l4vhw043.execute-api.us-east-1.amazonaws.com/dev/qa"

        payload = json.dumps({"text": inputtext})
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



st.sidebar.title("Login Portal")
menu=["Login"]
choice=st.sidebar.selectbox("Menu",menu)
if choice == "Login":
     email=  st.sidebar.text_input("Enter the Email")
     password=st.sidebar.text_input("Enter the password ",type='password')
     if st.sidebar.checkbox("Submit"):
          fs = gcsfs.GCSFileSystem(project='My First Project', token = 'cloud_storage_creds.json')
          credentials_path ='cloud_storage_creds.json'
          os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
          client = bigquery.Client()
          QUERY =(
                "SELECT email FROM `iconic-nimbus-348523.Users.login` WHERE email= '"+email+"' AND password='"+password+"';"
               )
          query_job = client.query(QUERY)  
          rows = query_job.result()  
          a=''
          for row in rows: 
               a=(row.email)

          print(a)
          if(a):

               st.success("Login credentials are authorized") 
               
               
               input=  st.text_input("Enter the Hashtag")
               data={
                    "tag":input
               } 
               
               submit=st.button('Submit data')
               if "submit_state" not in st.session_state:
                    st.session_state.submit_state = False
               if submit or st.session_state.submit_state:
                    st.session_state.submit_state = True
                    login={
                         "email":email,
                         "password":password
                    }
                    res=requests.post("https://iconic-nimbus-348523.ue.r.appspot.com/user/login/", json=login)

                    print(res)
                    res2=res.json()
                    
                    q='Bearer '+res2['token']
                    header = { 'Authorization': q }
                    res1=requests.post("https://iconic-nimbus-348523.ue.r.appspot.com/search/", headers={ 'Authorization': q },json=data)
                    res3=res1.json()
                    print("its res3")

                    df=pd.read_json(res3,orient='split')
                    df['Dates'] = pd.to_datetime(df['created_at']).dt.date
                    d=df.Dates.mode().iloc[0]

                    df2=tweet(df)

                    url="https://twitter.com/{}/status/{}".format(str(df2['user_screen_name'].iloc[0]),str(df2['tweet_id'].iloc[0]))
                    print(url)
                    selected2 = option_menu(None, ["Dashboard", "Most-Engaging-tweet", "News-Articles-with-NER", 'Word-Cloud'], 
                    icons=['house', 'cloud-upload', "list-task", 'gear'], 
                    menu_icon="cast", default_index=0, orientation="horizontal")
                    c1,c2=st.columns(2)
                    nerresults=[]
                    
                    if selected2=="Dashboard":
                         st.markdown("""
                    # <iframe width="900" height="1500" src="https://datastudio.google.com/embed/reporting/9a1789a5-f9fc-4117-9152-e1ed5dcbd684/page/f69rC" frameborder="0" style="border:0" allowfullscreen></iframe>
                    # """, unsafe_allow_html=True)
                    elif selected2=="Most-Engaging-tweet":
                         try:
                              res4=display(url)
                              st.header("Tweet with most engagement")
                              components.html(res4,height= 700)
                         except:
                              st.text_area(label ="Most engaging tweet",value=str(df2['text'].iloc[0]))
                              st.text_area(label ="url to the tweet",value=url)          
                    elif selected2=="News-Articles-with-NER":
                         url1 = ('https://newsapi.org/v2/everything?'
                         'q={}&'
                         'from={}&'
                         'sortBy=popularity&'
                         'apiKey=5ef7ef72dbdc43cdaac7ba895c219e85'.format(input,d))
                         r=requests.get(url1)
                         r=r.json()
                         articles=r['articles']
                         for article in articles:
                              if(str(d) in str(article['publishedAt'])):
                                   c1.header(article['title'])
                                   
                                   c2.markdown(f",<h5> Published At: {article['publishedAt']}</h5>",unsafe_allow_html=True)
                                   if article['author']:
                                        c1.write(article['author'])
                                   st.write(article['source']['name'])
                                   data={
                                        'inputtext':article['content']
                                   }
                                   res=requests.post("https://iconic-nimbus-348523.ue.r.appspot.com/search/ner/", json=data)
                                   
                                   nerresults.append(res.json())
                                   
                                   c1.write(article['description'])
                                   
                                   c2.image(article['urlToImage'],width=400)
                                   st.text("  \n  \n  \n") 
                         TopOrg,TopPer=TopEntities(nerresults)
                         if TopOrg!='None':
                              st.text_area(label ="Top Organisation",value=TopOrg,height=100)
                         else:
                              st.text_area('Did not find mentions of organizations')
                         if TopPer!='None':
                              st.text_area(label ="Top Location",value=TopPer,height=100)
                         else:
                              st.text_area('Did not find mentions of Locations')
                         print(TopPer)
                    elif selected2=="Word-Cloud":
                         allwords = " ".join([twts for twts in df['text']])
                         wordCloud = WordCloud(width = 500, height = 500, random_state = 21, max_font_size = 119).generate(allwords)
                         plt.figure(figsize=(20, 20), dpi=80)
                         plt.imshow(wordCloud, interpolation = "bilinear")
                         plt.axis("off")
                         st.pyplot(plt)
          else:
               st.error("Login credentials do not exist")
