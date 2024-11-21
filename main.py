from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
import vertexai
from google.oauth2 import service_account
import google.auth
from google.auth.transport.requests import Request
from typing import List
import re
from vertexai.generative_models import GenerativeModel
from datetime import datetime
from google.cloud import aiplatform

app = FastAPI()
from listBucket import gcp_create_bucket, list_buckets , upload_files_to_gcs , process_text

class BucketRequest(BaseModel):
    bucket_name: str
    location: str = "US"  

class UploadFileRequest(BaseModel):
    bucket_name: str
    object_names: List[str] 
    file_paths: List[str] 

class InputText(BaseModel):
    text: str


@app.post("/create_bucket")
async def create_bucket(request: BucketRequest):
    """Endpoint to create a GCS bucket with a specified name and location."""
    result = gcp_create_bucket(request.bucket_name, request.location)
    return {"message": result}

@app.get("/list_buckets")
async def get_buckets():
    """Endpoint to retrieve a list of all buckets in the project."""
    return {"buckets": list_buckets()}

@app.post("/upload_file")
async def upload_file(request: UploadFileRequest):
    """Endpoint to upload files to a GCS bucket."""
    return upload_files_to_gcs(request.bucket_name, request.object_names, request.file_paths)

@app.post("/process_text")
async def process_text_endpoint(input: InputText):
    """Endpoint to process the input text using Vertex AI."""
    formatted_output = process_text(input.text)
    return {"formatted_output": formatted_output}
