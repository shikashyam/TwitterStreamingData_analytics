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
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
# st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)

# st.markdown("""
# <nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="background-color: #3498DB;">
#   <a class="navbar-brand" href="https://youtube.com/dataprofessor" target="_blank">Data Professor</a>
#   <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
#     <span class="navbar-toggler-icon"></span>
#   </button>
#   <div class="collapse navbar-collapse" id="navbarNav">
#     <ul class="navbar-nav">
#       <li class="nav-item active">
#         <a class="nav-link disabled" href="#">Home <span class="sr-only">(current)</span></a>
#       </li>
#       <li class="nav-item">
#         <a class="nav-link" href="https://youtube.com/dataprofessor" target="_blank">YouTube</a>
#       </li>
#       <li class="nav-item">
#         <a class="nav-link" href="https://twitter.com/thedataprof" target="_blank">Twitter</a>
#       </li>
#     </ul>
#   </div>
# </nav>
# """, unsafe_allow_html=True)
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Twitter_logo.svg/2560px-Twitter_logo.svg.png", use_column_width=True)
st.title("Social Media analytics")
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
     #print(response)
     #res=response.json()
     res = response.json()["html"] 
     return res

def tweet(df2):
     df3=df2.loc[df2['reply_count'] == df2['reply_count'].max()]
     print("inside tweet function")
     #print(df3)
     print(df3['tweet_id'])
     return df3

def NER(inputtext):
    inputtext=inputtext[0:500]
    print('In NER Function')
    ner='No Event/Episode Narratives available for the Event'
    i=0
    while(i<3):
        #print(inputtext)
        url = "https://22l4vhw043.execute-api.us-east-1.amazonaws.com/dev/qa"

        payload = json.dumps({"text": inputtext})
        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        #print("myresponse")
        #print(response)
        if 'timed out' in response.text:
            print('timedout so I try again '+str(i))
            i=i+1
        else:
            jsonresp=response.json()
            ner=jsonresp
            #print(ner)
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
          #table_id = 'iconic-nimbus-348523.Users.login'
          QUERY =(
                "SELECT email FROM `iconic-nimbus-348523.Users.login` WHERE email= '"+email+"' AND password='"+password+"';"
               )
          query_job = client.query(QUERY)  
          rows = query_job.result()  
          a=''
          for row in rows: 
               a=(row.email)
          # if(a):
          #   st.success("Login credentials are authorized") 
          # else:
          #  st.error("Login credentials do not exist")
          print(a)
          if(a!="admin@gmail.com"):
            with st.spinner('Wait for it...'):
               time.sleep(5)
            st.success("Login credentials are authorized") 
            #st.success("Login credentials are authorized") 
            input=  st.text_input("Enter the Hashtag")
            data={
                "tag":input
               } 
            #data=input
            if st.button("submit"):
               c1,c2=st.columns(2)
               login={
                    "email":email,
                    "password":password
               }
               #res=requests.post("https://iconic-nimbus-348523.ue.r.appspot.com/user/login/", json=login)
               res=requests.post("http://127.0.0.1:8000/user/login/", json=login)
               #try:
               print(res)
               res2=res.json()
               
               q='Bearer '+res2['token']
               header = { 'Authorization': q }
               #res1=requests.post("https://iconic-nimbus-348523.ue.r.appspot.com/search/", headers={ 'Authorization': q },json=data)
               res1=requests.post("http://127.0.0.1:8000/search/", headers={ 'Authorization': q },json=data)
               #print(res1)
               res3=res1.json()
               print("its res3")
               # print(res3)
               # print(type(res3))
               df=pd.read_json(res3,orient='split')
               #print(df['analysis'])
               df2=tweet(df)
               #print(df2)
               #print(df['user_screen_name'].iloc[0])
               url="https://twitter.com/{}/status/{}".format(str(df2['user_screen_name'].iloc[0]),str(df2['tweet_id'].iloc[0]))
               print(url)
               #url="https://twitter.com/TIME/status/1521324417749594113"
               #st.write(res4)
               try:
                    res4=display(url)
                    #print(res4)
                    #st.header("Tweet with most engagement")
                    c1.header("Tweet with most engagement")
                    components.html(res4,height= 700)
               except:
                    st.write(str(df2['text'].iloc[0]))
               # print(url)
               #print(res3['tweet_id'])
               #st.write(res3.tweet_id)        
               # except:
               #      st.error("Invalid login credentials/token expired. Refresh and login again")  
               # url1 = ('https://newsapi.org/v2/everything?'
               # 'q={}&'
               # 'from={}}&'
               # 'sortBy=popularity&'
               # 'apiKey=5ef7ef72dbdc43cdaac7ba895c219e85'.format(input,df_date[0]))
               url1 = ('https://newsapi.org/v2/everything?'
               'q={}&'
               'from=2022-04-28&'
               'sortBy=popularity&'
               'apiKey=5ef7ef72dbdc43cdaac7ba895c219e85'.format(input))
               nerresults=[]
               r=requests.get(url1)
               r=r.json()
               articles=r['articles']
               for article in articles[:10]:
                    c2.header(article['title'])
                    #st.markdown(f",<h2> Published At: {article['title']}</h2>",unsafe_allow_html=True)
                    c2.markdown(f",<h5> Published At: {article['publishedAt']}</h5>",unsafe_allow_html=True)
                    if article['author']:
                         c2.write(article['author'])
                    st.write(article['source']['name'])
                    data={
                         'inputtext':article['content']
                    }
                    #res=requests.post("https://iconic-nimbus-348523.ue.r.appspot.com/search/ner/", json=data)
                    res=requests.post("http://127.0.0.1:8000/search/ner/", json=data)
                    nerresults.append(res.json())
                    #st.write(res.json())
                    #print(NER(article['description']))
                    c2.write(article['description'])
                    c2.write(article['content'])
                    c2.image(article['urlToImage'])
               
               TopOrg,TopPer=TopEntities(nerresults)
               if TopOrg!='None':
                    st.write(TopOrg)
               else:
                    st.write('Did not find mentions of organizations')

               if TopPer!='None':
                    st.write(TopPer)
               else:
                    st.write('Did not find mentions of Locations')
               print(TopPer)
          elif (a == "admin@gmail.com"):
               print("inside admin page")
               st.write("new admin streamlit page")
          else:
           st.error("Login credentials do not exist")
