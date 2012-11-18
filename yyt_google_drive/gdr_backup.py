#!/usr/bin/python
import sys
import httplib2
import pprint
import logging
import oauth2client.client
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from apiclient import errors

class GetCredentialsException(Exception):
    def __init__(self, authorization_url):
        self.authorization_url = authorization_url



class CodeExchangeException(GetCredentialsException):
    """NULL"""

class NoRefreshTokenException(GetCredentialsException):
    """NULL"""


class NoUserIdException(Exception):
    """NULL"""

    # Path to client_secrets.json which should contain a JSON document such as:
    #   {
    #     "web": {
    #       "client_id": "[[YOUR_CLIENT_ID]]",
    #       "client_secret": "[[YOUR_CLIENT_SECRET]]",
    #       "redirect_uris": [],
    #       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    #       "token_uri": "https://accounts.google.com/o/oauth2/token"
    #     }
    #   }
CLIENTSECRETS_LOCATION = 'CLIENT_SECRETS.JSON'
# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    # Add other requested scopes.
]
# Copy your credentials from the APIs Console
CLIENT_ID = '1021813612028.apps.googleusercontent.com'



def get_stored_credentials(user_id):
  f = open(user_id, 'r+')
  cred = f.read();
  f.close()
  return cred
#  raise NotImplementedError()

def store_credentials(user_id, credentials):
  f = open(userid, 'w+')
  f.write(credentials.to_json())
  f.close()
#raise NotImplementedError()

def exchange_code(authorization_code):
    flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, ' '.join(SCOPES))
    flow.redirect_uri = REDIRECT_URI
    try:
        credentials = flow.step2_exchange(authorization_code)
        return credentials
    except FlowExchangeError, error:
        logging.error('An error occurred: %s', error)
        raise CodeExchangeException(None)


def get_user_info(credentials):
  user_info_service = build(
    serviceName='oauth2', version='v2',
    http=credentials.authorize(httplib2.Http()))
  user_info = None
  try:
    user_info = user_info_service.userinfo().get().execute()
  except errors.HttpError, e:
    logging.error('An error occurred: %s', e)
  if user_info and user_info.get('id'):
    return user_info
  else:
    raise NoUserIdException()

def get_authorization_url(email_address, state):
    flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, ' '.join(SCOPES))
    flow.params['access_type'] = 'offline'
    flow.params['approval_prompt'] = 'force'
    flow.params['user_id'] = email_address
    flow.params['state'] = state
    return flow.step1_get_authorize_url(REDIRECT_URI)

def get_credentials(authorization_code, state):
    email_address = ''
    try:
        credentials = exchange_code(authorization_code)
        user_info = get_user_info(credentials)
        email_address = user_info.get('email')
        user_id = user_info.get('id')
        if credentials.refresh_token is not None:
            store_credentials(user_id, credentials)
            return credentials
        else:
            credentials = get_stored_credentials(user_id)
            if credentials and credentials.refresh_token is not None:
                return credentials
    except CodeExchangeException, error:
        logging.error('An error occurred during code exchange.')
        # Drive apps should try to retrieve the user and credentials for the current
        # session.
        # If none is available, redirect the user to the authorization URL.
        error.authorization_url = get_authorization_url(email_address, state)
        raise error
    except NoUserIdException:
        logging.error('No user ID could be retrieved.')
    # No refresh token has been retrieved.
    authorization_url = get_authorization_url(email_address, state)
    raise NoRefreshTokenException(authorization_url)


def build_service(credentials):
  http = httplib2.Http()
  http = credentials.authorize(http)
  return build('drive', 'v2', http=http)

def download_file(service, drive_file):
  download_url = drive_file.get('downloadUrl')
  if download_url:
    resp, content = service._http.request(download_url)
    if resp.status == 200:
      print 'Status: %s ' % resp
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



credentials =oauth2client.client.Credentials.new_from_json(get_stored_credentials(CLIENT_ID))

drive_service = build_service(credentials)

result = retrieve_all_files(drive_service);


for tmp in result:
  print tmp['title']
  if tmp['title']=='My document':
    print 'download link:'+tmp['downloadUrl']
    content = download_file(drive_service, tmp)
    f = open('My document.txt', 'wb+')
    f.write(content)
    f.close


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
