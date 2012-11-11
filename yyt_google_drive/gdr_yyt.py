#!/usr/bin/python
import sys
import httplib2
import pprint

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from apiclient import errors

def download_file(service, drive_file):
  download_url = drive_file.get('downloadUrl')
  if download_url:
    resp, content = service._http.request(download_url)
    if resp.status == 200:
      print 'Status: %s ' % resp
      print content
      return content
    else:
      print 'Status: %s ' % resp
      return None
  else:
      return None


def retrieve_all_files(service):
 result = []
 page_token = None
 while True:
  try:
   param = {}
   if page_token:
    param['pageToken'] = page_token
   files = service.files().list(**param).execute()
   result.extend(files['items'])
   page_token = files.get('nextPageToken')
   if not page_token:
    break
  except errors.HttpError, error:
   print 'An error occurred: %s' % error
   break
 return result


# Copy your credentials from the APIs Console
CLIENT_ID = '1021813612028.apps.googleusercontent.com'
CLIENT_SECRET = 'eZmvRwEGtJkXQRdsvsz1DQhS'

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
# Path to the file to upload
#FILENAME = 'document.txt'

# Run through the OAuth flow and retrieve credentials
flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
authorize_url = flow.step1_get_authorize_url()
print 'Go to the following link in your browser: ' + authorize_url
code = raw_input('Enter verification code: ').strip()
credentials = flow.step2_exchange(code)
#credentials = flow.step2_exchange('4/78nDZVnwuMY5zv6nP1SNdoMiy2-V.Muiy4JdEnUkbuJJVnL49Cc8GdR_FdQI') 

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)

result = retrieve_all_files(drive_service);

for tmp in result:
  print tmp
  print 'title'+tmp['title']
  if tmp.get('downloadUrl'):
    print 'download link:'+tmp['downloadUrl']
    content = download_file(drive_service, tmp)
    print 'content:'+content

"""
# Insert a file
media_body = MediaFileUpload(FILENAME, mimetype='text/plain', resumable=True)
body = {
  'title': 'My document',
  'description': 'A test document',
  'mimeType': 'text/plain'
}

file = drive_service.files().insert(body=body, media_body=media_body).execute()
pprint.pprint(file)
"""
