"""Google Sheets API interface."""
import os.path
import pickle
import socket

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from gsheets_cell_counter import __credentials__, __token__

SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
socket.setdefaulttimeout(600)


def get_service() -> Resource:
    """Get the API service resource used for further interaction."""
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(__token__):
        with open(__token__, 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(__credentials__, SCOPE)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(__token__, 'wb') as token:
            pickle.dump(credentials, token)

    return build('sheets', 'v4', credentials=credentials)
