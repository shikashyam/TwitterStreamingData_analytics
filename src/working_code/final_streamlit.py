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
st.title("Social Media analytics")
with st.expander("About the App"):
     st.write("""
         The next era of social media marketing is here and it is driven by social media. As more and more organizations move to this trend of social media marketing, there is a recognizable gap in understanding audience response to these campaigns. The leadership level still looks to see sales metrics and quarter-on-quarter growth and familiar metrics which is not explained in terms of hashtag and mention counts.

Our project aims to bridge this gap by creating a pipeline which derives valuable intelligence from social media and visualize metrics that determine the success or failure of marketing campaigns based on social media chatter.
     """)
input=  st.text_input("Enter the Hashtag")
data={
     "tag":input
}                    
if st.button("Predict"):
     res=requests.post("http://127.0.0.1:8000/search/",json=data)
     res2=res.json() 
     #print(res2)
     st.write(res2)
      