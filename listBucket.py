from fastapi import HTTPException
import os
import requests
import google.auth
from google.auth.transport.requests import Request
from google.auth import load_credentials_from_dict

from dotenv import load_dotenv
import tempfile
import json


load_dotenv()

credentials_info = json.loads(os.getenv("API_KEY"))
# PROJECT_ID = credentials_info['PROJECT_ID']


# with open('path_to_credentials.json', 'r') as file:
#     credentials_info = json.load(file)

def get_access_token():
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    # quota_project_id = PROJECT_ID
    quota_project_id = "firstsource-vertex"
    credentials, project = load_credentials_from_dict(credentials_info, scopes=scopes, quota_project_id=quota_project_id)
    credentials.refresh(Request())
    return credentials.token, project



def list_buckets():
    """Lists all buckets in the project using the Google Cloud Storage API."""
    access_token, project = get_access_token()
    
    url = "https://storage.googleapis.com/storage/v1/b"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    params = {"project": project}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        buckets = response.json().get("items", [])
        return [bucket["name"] for bucket in buckets]
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to list buckets: {response.text}")


def gcp_create_bucket(bucket_name: str, location: str):
    """Creates a new GCS bucket using the Google Cloud Storage API."""
    access_token, project = get_access_token()
    
    url = f"https://storage.googleapis.com/storage/v1/b?project={project}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "name": bucket_name,
        "location": location,
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return f"Bucket {bucket_name} created in {location}."
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to create bucket: {response.text}")
