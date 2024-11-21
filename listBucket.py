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

# def neutralize_json_blocks(text):
#     json_pattern = re.compile(r'```json(.*?)```', re.DOTALL)
#     def process_json(match):
#         json_string = match.group(1).strip()  
#         try:
            
#             json_data = json.loads(json_string)
#             return str(json_data).replace('{', '').replace('}', '')
#         except json.JSONDecodeError:
#             return json_string 
        
   
#     return json_pattern.sub(process_json, text)

# def get_credentials():
#     credentials_info = json.loads(os.getenv("API_KEY"))
#     return service_account.Credentials.from_service_account_info(credentials_info)

def get_access_token():
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    # quota_project_id = PROJECT
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


def upload_files_to_gcs(bucket_name: str, object_names: List[str], file_paths: List[str]):
    """Uploads files to the specified GCS bucket."""
    access_token, project = get_access_token()

    # Set the API endpoint and headers
    url_template = f"https://storage.googleapis.com/upload/storage/v1/b/{bucket_name}/o?uploadType=media&name={{}}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
    }

    if len(file_paths) != len(object_names):
        raise HTTPException(status_code=400, detail="The number of file paths does not match the number of object names.")

    # Upload each file
    for i, file_path in enumerate(file_paths):
        try:
            with open(file_path, "rb") as file:
                file_content = file.read()
        except FileNotFoundError:
            raise HTTPException(status_code=400, detail=f"File not found at {file_path}")

        object_name = object_names[i]
        url = url_template.format(object_name)

        # Make the request to upload the file
        response = requests.post(url, headers=headers, data=file_content)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"{response.status_code}: Failed to upload file '{object_name}': {response.text}")

    return {"message": "Files uploaded successfully."}

# def process_text(input_text: str):
#     input_text = neutralize_json_blocks(input_text)

#     credentials = get_credentials()
#     vertexai.init(project="firstsource-vertex", location="us-central1", credentials=credentials)

#     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     prompt = f"""
#     Your task is to provide formatting of input {input_text} based on Output Format:

#     Output Format:
#     "formatted_output": [
#         {{
#           "Step": "Step description",
#           "Reason": "",
#           "Action": "",
#           "api_name": "creative name based on action",
#           "execution_time": "{current_time}",
#           "input_variable": key:value based on action execution,
#           "status": "compliant"
#         }}
#       ]
      
#     Instruction:
#     - Do not provide any additional text other than JSON
#     - Use {current_time} for the execution time
#     - Provide the input variable name:value as string
#     """

#     model = GenerativeModel("gemini-1.5-flash-001")
#     response = model.generate_content([prompt])

#     formatted_response = response.text.replace('*', '').replace('#', '')
#     return formatted_response