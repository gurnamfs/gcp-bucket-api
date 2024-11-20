from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
import google.auth
from google.auth.transport.requests import Request
from typing import List

app = FastAPI()
from listBucket import gcp_create_bucket, list_buckets , upload_files_to_gcs


class BucketRequest(BaseModel):
    bucket_name: str
    location: str = "US"  


class UploadFileRequest(BaseModel):
    bucket_name: str
    object_names: List[str] 
    file_paths: List[str] 

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
    # Call the upload function from listBucket.py
    return upload_files_to_gcs(request.bucket_name, request.object_names, request.file_paths)
