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

PROJECT_ID = os.getenv("PROJECT_ID")
PRIVATE_KEY_ID = os.getenv("PRIVATE_KEY_ID")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CLIENT_EMAIL = os.getenv("CLIENT_EMAIL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_CERT = os.getenv("CLIENT_CERT")


credentials_info = {
  "type": "service_account",
  "project_id": PROJECT_ID,
  "private_key_id": PRIVATE_KEY_ID,
  "private_key": PRIVATE_KEY,
  "client_email": CLIENT_EMAIL,
  "client_id": CLIENT_ID,
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": CLIENT_CERT,
  "universe_domain": "googleapis.com"
}


# with open('path_to_credentials.json', 'r') as file:
#     credentials_info = json.load(file)

def get_access_token():
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    quota_project_id = PROJECT_ID
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
