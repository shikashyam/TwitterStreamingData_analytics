import streamlit as st
import os
from google.cloud import bigquery
import gcsfs
import requests
from PIL import Image
from datetime import date,datetime
import streamlit.components.v1 as components
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.sidebar.image("https://amazelaw.com/wp-content/uploads/2019/02/Best-Twitter-Advertising-Agencies-2019.png", use_column_width=True)
st.title("Social Media analytics")
with st.expander("About the App"):
     st.write("""
         The next era of social media marketing is here and it is driven by social media. As more and more organizations move to this trend of social media marketing, there is a recognizable gap in understanding audience response to these campaigns. The leadership level still looks to see sales metrics and quarter-on-quarter growth and familiar metrics which is not explained in terms of hashtag and mention counts.

Our project aims to bridge this gap by creating a pipeline which derives valuable intelligence from social media and visualize metrics that determine the success or failure of marketing campaigns based on social media chatter.
     """)

def display(tweet_url):
     api="https://publish.twitter.com/oembed?url={}".format(tweet_url)
     response=requests.get(api)
     #res=response.json()
     res = response.json()["html"] 
     return res

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
          a=[]
          for row in rows: 
               a.append(row.email)
          # if(a):
          #   st.success("Login credentials are authorized") 
          # else:
          #  st.error("Login credentials do not exist")
          if(a):
            st.success("Login credentials are authorized") 
            input=  st.text_input("Enter the Hashtag")
            data={
                "tag":input
               } 
            if st.button("submit"):
               login={
                    "email":email,
                    "password":password
               }
               res=requests.post("http://127.0.0.1:8000/user/login/", json=login)
               #try:
               res2=res.json()
               #print(res2)
               q='Bearer '+res2['token']
               header = { 'Authorization': q }
               res1=requests.post("http://127.0.0.1:8000/search/", headers={ 'Authorization': q },json=data)
               res3=res1.json()
               #print(res3['text'])
               #url="https://twitter.com/'{}'/status/'{}'".format(res3['user_screen_name'],res3['tweet_id'])
               url="https://twitter.com/TIME/status/1521324417749594113"
               res4=display(url)
               #st.write(res4)
               components.html(res4,height= 700)
               print(url)
               #print(res3['tweet_id'])
               #st.write(res3.tweet_id)        
               # except:
               #      st.error("Invalid login credentials/token expired. Refresh and login again")  
          else:
           st.error("Login credentials do not exist")
# input=  st.text_input("Enter the Hashtag")
# data={
#      "tag":input
# }                    