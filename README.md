TwitterStreamingAnalytics
==============================

Welcome to our project - Social Media Marketing Campaign analysis.
We have a WebApp that we would love for you to explore : https://share.streamlit.io/sairaghav1999/bigdata-final-streamlit/main/final_streamlit.py

If you need help navigating the App, please refer to our user manual at : https://codelabs-preview.appspot.com/?file_id=1svD8mPao9wf53r7UqlHff6tfM8X3xSzbhtAsoIU4vCc#0

The official technical documentation can be found at : https://codelabs-preview.appspot.com/?file_id=1JS8_4MFa0frkV36Z6O8jt_z-c7eIDKdx5Hh4WKpsqVI#0

Problem Statement and Objectives
===================================
The next era of social media marketing is here and it is driven by social media. As more and more organizations move to this trend of social media marketing, there is a recognizable gap in understanding audience response to these campaigns.  The leadership level still looks to see metrics at one glance as well as customer/audience engagement which cannot be directly seen by scrolling through social media platforms.

Our project aims to bridge this gap by creating a pipeline which derives valuable intelligence from social media and visualize metrics that determine the success or failure of marketing campaigns based on social media chatter.

Project Architecture
===================================
Our project architecture is as shown below:

Our Architecture can be divided broadly into 3 parts. 
* First, we have the ingestion pipeline. The first step of the ingestion pipeline workflow reads the authenticated Twitter Stream using Python tweepy library and writes it to a GCP Pub/Sub topic. The Pub/Sub topic writes the tweets in real-time into a BigQuery table with the help of a cloud function that is triggered by the arrival of a message in Pub/Sub. As a second step in the workflow, we have used Apache Beam hosted on Cloud Dataflow to transform the raw data from the first bigquery table and move it to another BigQuery table as our final data store. The transformation consists of some text preprocessing for the tweets. 
* The entire Ingestion pipeline as described above is orchestrated using Airflow to run on an hourly schedule. Since Twitter API places a limit on the number of tweets that can be streamed, we stream only the first 10000 tweets of an hour.
* Secondly, we have the modelling pipeline. With the second BigQuery table as our Data Source, we perform Sentiment analysis on the tweets using  Huggingface models hosted on AWS lambda using Docker and the serverless framework. We also perform some analytics over time to identify the date with the most engagement for a given hashtag, and based on that use the NewsAPI to get related news articles. We also perform NER on the news articles to find out top mentioned Organizations and Locations. The entire modelling aspect is wrapped in a FastAPI framework and is authenticated with JWT tokens and hosted on GCP App Engine.
* Finally, we have our front end and the intelligence part. We have a dynamic Google Datastudio dashboard embedded in our streamlit UI, along with few other interesting metrics such as WordCloud, Related Articles, Top mentioned organization, top mentioned location. We also have a login functionality to enable only authenticated users to access the project.
* We are also using some other tools such as Github Actions for CI/CD, for airflow scripts which automatically push the updated airflow script to GCP Buckets for airflow to pick up. We also have used Git Projects and Issues to track the project at a granular level. We have used Cloud Logging for debugging and Pytest for Python testing and Postman for API testing.

Technology Stack used
===================================
* Programming Language:  Python 3.8
* Cloud Platforms:  Google Cloud Platform, Amazon Web Services
* Data Pipeline:  Airflow, Apache Beam, Cloud Pub/Sub, Cloud Function
* Storage:  Google Cloud Storage, Google Big Query, Elastic Container Repository
* API:  FastAPI, JWT Tokens
* Deployment:  Docker, AWS Lambda, Serverless, GCP App Engine
* CI/CD Workflow:  GitHub Actions
* NLP Models:  Sentiment Analysis, NER Model
* Web Application:  Streamlit
* Data Visualization:  Google Data Studio
* Testing Frameworks:  Pytest, Coverage test, Postman
* Other tools and technologies:  Google Co-lab, Jupyter Notebook, Cloud Composer, Cloud Build, IAM

Steps to deploy Beam ingestion pipeline
===========================================

We will be making use of Cloud Dataflow to run Apache Beam. In the GCP account of your choice open the cloud shell, and clone this repository.
Navigate to the Apache_Beam folder as below:

```
cd BigDataSystemsFinalProject/src/Apache_Beam/
```

Now, run the below script to trigger the Beam pipeline. Make sure Cloud Dataflow is enabled billing in your account.

```
python3 beam_catchup_script.py --runner DataFlowRunner --project <your-project-name> --temp_location gs://<your-bucket-name>/temp/ --staging_location gs://<your-bucket-name>/staging/ --region <compute-region> --job_name <job-name>
```

We can also create a template of the job, and trigger a Dataflow job from Dataflow console or externally through a python script. Below is the script to create a template.

```
python beam_pipeline.py \
    --runner DataflowRunner \
    --project <your-project-name> \
    --staging_location gs://<your-bucket-name>/staging/\
    --temp_location gs://<your-bucket-name>/temp/ \
    --template_location gs://<your-bucket-name>/MyTemplate \
    --region <compute-region> \
    --setup_file ./BigDataSystemsFinalProject/src/Apache_Beam/setup.py \
    --job_name <job-name>
```
The template will be stored at ```gs://<your-bucket-name>/MyTemplate```

Steps to deploy FastAPI to GCP App Engine
===========================================

Make sure you have billing enabled for App Engine in GCP and the API is enabled. Open the cloud shell and clone our repository. Navigate to the folder with the FastAPI code as shown below:

```
cd BigDataSystemsFinalProject/src/fastapi/
```

The app.yaml file is already configured for our settings, but should you choose to, you can change the configurations for instance_class. Information about various instance classes can be found at : https://cloud.google.com/appengine/docs/standard/python3/runtime

```
runtime : python37
instance_class: F4_1G
entrypoint: uvicorn main:app --port $PORT
```

Once your app.yaml is configured, all you have to do is give the following command:

```
gcloud app deploy app.yaml
```

You can see build logs in the cloud Build and see any errors in Logger in GCP console.

Steps to deploy Streamlit code to Streamlit Cloud
====================================================

Create a streamlit account at www.streamlit.io and navigate to Create new app >> Deploy. Enter the github URL of this repo, and choose cd BigDataSystemsFinalProject/src/Streamlit/final_streamlit.py

In your local terminal with streamlit installed, navigate to the path of the file, run the following command to get a requirements.txt file.

```
pipreqs
```
Upload this file along with other files from this repo, and then run the streamlit deployment.

To run streamlit locally, you can use:

```
cd BigDataSystemsFinalProject/src/Streamlit/
streamlit run final_streamlit.py
```
Steps to use our testcases to test this code
====================================================

In your local terminal, clone this github repository and execute the below commands for FastAPI and Airflow Scripts testing.

* For FastAPI testing we have created a script test_main.py

```
cd BigDataSystemsFinalProject/Pytest_Scripts
mv test_main.py BigDataSystemsFinalProject/src/fastapi/
```
Once we have the file in the same location as FastAPI code, we can execute :

```
pytest test_main.py
```
This command will give the individual testing results of each of the testcases written to test the entireity of FastAPI code.
For coverage test run:
```
BigDataSystemsFinalProject/src/fastapi/
coverage run
```
To generate report of the coverage test, execute:
```
coverage report -m
```

* For Airflow Scripts testing we have created a script test_DAG.py

```
cd BigDataSystemsFinalProject/Pytest_Scripts
mv test_DAG.py BigDataSystemsFinalProject/src/airflow scripts/
```
Once we have the file in the same location as airflow code, we can execute :

```
pytest test_DAG.py
```
This command will give the individual testing results of each of the testcases written to test the entireity of airflow DAGs
For coverage test run:
```
BigDataSystemsFinalProject/src/airflow scripts/
coverage run
```
To generate report of the coverage test, execute:
```
coverage report -m
```

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
