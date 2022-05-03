import streamlit as st
import os
from google.cloud import bigquery
import gcsfs
import requests
from PIL import Image
from datetime import date,datetime
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
                "SELECT * FROM 'iconic-nimbus-348523.Users.login' WHERE email= '"+email+"' AND password='"+password+"';"
               )
          query_job = client.query(QUERY)  
          rows = query_job.result()  
          a=[]
          for row in rows: 
               a.append(row.email)
          if(a):
            st.success("Login credentials are authorized") 
          else:
           st.error("Login credentials do not exist")
# input=  st.text_input("Enter the Hashtag")
# data={
#      "tag":input
# }                    
# if st.button("Predict"):
#      res=requests.post("http://127.0.0.1:8000/search/",json=data)
#      res2=res.json() 
#      #print(res2)
#      st.write(res2)
      