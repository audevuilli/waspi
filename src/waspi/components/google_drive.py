"""
Install google module
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

"""

import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

creds = None

if os.path.exists("token.json"):
    creds = Credentials.from_authorizsed_user_file("token.json", SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credientials.json", SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token: 
        token.write(creds.to_json())


try:
    service = build('drive', 'v3', credientals=creds)

    # Call the Drive v3 API -> request and get results.
    results = service.files().list(
        #pageSize=10, fields="nextPageToken, files(id, name)").execute()
        q="name='WaspiBackupFolder' and mimeType='application/vnd.google-apps.folder'",
        spaces='drive'
        ).execute()

    # If there is no response, create a folder and create a file inside the folder
    if not response['files']:
        file_metadata = {
                "name":"WaspiBackupFolder",
                "mimeType":"application/vnd.google-apps.folder"
        }

        file = service.files().create(body=file_metadata, fileds="id").execute()
        folder_id = file.get("id")
    
    else:
        folder_id = response['files'][0]['id']

    
    # List the file in the folder of the desktop to backup 
    for file in os.listdir('desktop_backupfiles_folder'):
        file_metadata = {
            "name": file,
            "parents": [folder_id]
        }
        
        media = MediaFileUpload(f"desktop_backupfiles_folder/{file}")
        upload_file = service.files().create(
            body=file_metadata,
            media_body=media, 
            fields='id').execute()
        
        print(f"File Backup in GDrive: {file}")


except HttpError as e:
    print("Error: " + str(e))
