from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


"""Shows basic usage of the Google Calendar API.

Creates a Google Calendar API service object and outputs a list of the next
10 events on the user's calendar.
"""


def getCurrentEvents():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now_time = datetime.datetime.utcnow()
    #restrict interval so relevant events
    #don't get clobbered by all past and future events
    #due to the maxResults limit
    future_time = now_time + datetime.timedelta(days=1)
    past_time = now_time + datetime.timedelta(days=-1)

    now = now_time.isoformat() + 'Z' # 'Z' indicates UTC time
    future = future_time.isoformat() + 'Z'
    past = past_time.isoformat() + 'Z'
    # This part is a hack as using service.events() with both a timeMin=now
    # and a timeMax=now seems to return nothing... but the intersection of the
    # two requested separately will give the current events

    eventsResultMin = service.events().list(
        calendarId='primary',\
    timeMin=now,timeMax=future, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    eventsResultMax = service.events().list(
        calendarId='primary',\
    timeMax=now, timeMin=past, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()

    eventsMin = {event['id'] + event['summary'] for event in eventsResultMin.get('items', [])}
    eventsMax = {event['id'] + event['summary'] for event in eventsResultMax.get('items', [])}

    print(eventsMin)
    print(eventsMax)

    currentEvents = eventsMin.intersection(eventsMax)
    print(currentEvents)
    return currentEvents



if __name__ == '__main__':
   getCurrentEvents()

