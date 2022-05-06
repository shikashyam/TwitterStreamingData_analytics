import googleapiclient.discovery
from pytest import *
from google.oauth2 import service_account


def CleanData():
    print('Extract job completed. Triggering Dataflow job')
    credentials = service_account.Credentials.from_service_account_file('mykey.json',)
    dataflow = googleapiclient.discovery.build('dataflow', 'v1b3', credentials=credentials, cache_discovery=False)
    project = 'iconic-nimbus-348523'
    location = 'us-east1'
    result = dataflow.projects().locations().templates().launch(
            projectId=project,
            location = location,
            body={
            "environment": {
                "zone": "us-east1-c",
                "tempLocation": "gs://beampipeline1/temp/"
            },
            "jobName": 'beamfromoutside'
            },
            gcsPath = 'gs://beampipeline1/MyTemplate'
    ).execute()

    print('Job Triggered')
    print(result)

def test_clean_data():
    assert CleanData()== 'Job Triggered' or 'Extract job completed. Triggering Dataflow job'

