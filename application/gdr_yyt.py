#!/usr/bin/python
import sys
import glob
import httplib2
import pprint
import logging
import oauth2client.client
import webbrowser
from boxdotnet import XMLNode
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from apiclient import errors

class NeedLoginException():
  """Needs to call autenti"""

class GOOGLE_VIEW:
    metadata = []
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
    SCOPES = 'https://www.googleapis.com/auth/drive'
    #'https://www.googleapis.com/auth/userinfo.email',
    #'https://www.googleapis.com/auth/userinfo.profile',
    # Add other requested scopes.
    # Copy your credentials from the APIs Console
    CLIENT_SECRET = 'eZmvRwEGtJkXQRdsvsz1DQhS'
    CLIENT_ID = '1021813612028.apps.googleusercontent.com'
    Drive_Service = False
    credentials = None
    def __init__(self):
       if glob.glob('GOOGLE_CREDENTIAL'):
            def get_stored_credentials():
                 f = open('GOOGLE_CREDENTIAL', 'r+')
                 cred = f.read();
                 f.close()
                 return cred
            self.credentials = oauth2client.client.Credentials.new_from_json(get_stored_credentials())
            self._build_service();
        
    def authent(self):
        flow = OAuth2WebServerFlow(self.CLIENT_ID, self.CLIENT_SECRET, self.SCOPES, self.REDIRECT_URI)
        authorize_url = flow.step1_get_authorize_url()
        print 'Go to the following link in your browser: '+ authorize_url
        webbrowser.open_new_tab(authorize_url);
        code = raw_input('Enter verification code: ').strip()
        self.credentials = flow.step2_exchange(code)
        # def store_credentials(credentials):
        f = open('GOOGLE_CREDENTIAL', 'w+')
        f.write(self.credentials.to_json())
        f.close()
        self._build_service();

    def _build_service(self):
        http = httplib2.Http()
        http = self.credentials.authorize(http)
        self.Drive_Service = build('drive', 'v2', http=http)

    def download_file(self, download_url, path):
        if  not self.Drive_Service: 
            raise NeedLoginException(None)
        resp, content = service._http.request(download_url)
        if resp.status == 200:
            print 'Download Succeed'
            if path == 'metadata.xml':
                self.metadata = XMLNode.parseXML(content, True)
                return self.metadata
                
            f = open(path, 'w+')
            f.write(content)
            f.close()
        else:
            print 'Download Failed'


    def retrieve_metadata(self):
        if  not self.Drive_Service: 
            raise NeedLoginException(None)
        result = []
        page_token = None
        while True:
            try:
                param = {}
                if page_token:
                    param['pageToken'] = page_token
                files = self.Drive_Service.files().list(**param).execute()
                result.extend(files['items'])
                page_token = files.get('nextPageToken')
                if not page_token:
                    break
            except errors.HttpError, error:
                print 'An error occurred: %s' % error
                break
        print 'titles in google drive'
        for tmp in result:
            print tmp['title']
            if tmp['title'] == 'metadata.xml':
                return (download_file(tmp['download_url'], 'metadata.xml'))
                break

    def upload(self, title, filename):
        if  not self.Drive_Service: 
            raise NeedLoginException(None)
        # upload a file
        media_body = MediaFileUpload(filename, mimetype='text/plain', resumable=True)
        body = {
            'title': title,
            'mimeType': ''
        }

        file = self.Drive_Service.files().insert(body=body, media_body=media_body).execute()
        return file

    def delete(self, file_id):
        if  not self.Drive_Service: 
            raise NeedLoginException(None)
        self.Drive_Service.files().delete(fileId=file_id).execute() 

