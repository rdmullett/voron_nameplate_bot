#!/usr/bin/python3

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.pickle.
#SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
#For now give ultimate scope. It's only running on one system with one google user dedicated to this. No need to limit during initial testing
SCOPES = ['https://www.googleapis.com/auth/drive']

def service():    
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return(service)

def serial_folder_create(service, serials):
    page_token = None
    nameplatesResponse = service.files().list(q="name='nameplates' and mimeType='application/vnd.google-apps.folder'",
                                     spaces='drive',
                                     fields='files(id)').execute()
    nameplatesID = nameplatesResponse["files"][0]['id']

    for serial in serials:
        response = service.files().list(q="name='" + serial + "' and mimeType='application/vnd.google-apps.folder' and trashed = false",
                                          spaces='drive',
                                          fields='nextPageToken, files(id, name)',
                                          pageToken=page_token).execute()
        page_token = response.get('nextPageToken', None)

        try:
            response_check = serial in response["files"][0]["name"]
        except:
            response_check = False

        print(response_check)
        if not response_check:
            file_metadata = {
                'name': serial,
                'mimeType': 'application/vnd.google-apps.folder',
                'permissions': {'displayName': 'anyone', 'role': 'reader'},
                'role': 'reader',
                'parents': [nameplatesID]
                }
            file = service.files().create(body=file_metadata, fields='id, webViewLink').execute()
        else:
            continue

#    print('Folder ID: %s' % file.get('id'))

def serial_stl_upload(service, serials):
    shareLinks = {}
    for serial in serials:
        response = service.files().list(q="name='" + serial + "' and mimeType='application/vnd.google-apps.folder' and trashed = false",
                                    spaces='drive',
                                    fields='files(id, webViewLink)').execute()
        folderID = response["files"][0]['id']
        folderURL = response["files"][0]['webViewLink']
        print(folderURL)

        #TODO:changes parents to grab ID instead of serial https://developers.google.com/drive/api/v3/folder#python_1
        noLogo = {'name': serial + "-NoLogo.stl",
                'parents': [folderID]
                }
        withLogo = {'name': serial + ".stl",
                'parents': [folderID]
                }
        mediaNoLogo = MediaFileUpload("/nameplates/" + "/" + serial + "-NoLogo.stl",
                resumable=True)
        mediaWithLogo = MediaFileUpload("/nameplates/" + serial + ".stl",
                resumable=True)
        fileUploadNoLogo = service.files().create(body=noLogo,
                media_body=mediaNoLogo,
                fields='id, parents').execute()
        fileUploadwithLogo = service.files().create(body=withLogo,
                media_body=mediaWithLogo,
                fields='id, parents').execute()

        shareLinks[serial] = [folderURL]
    return shareLinks

def main(service):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    
    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

if __name__ == '__main__':
    main()
