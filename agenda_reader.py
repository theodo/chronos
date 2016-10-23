
#!/usr/bin/python
# coding=utf-8

from __future__ import print_function
import httplib2
import os
import requests
import urllib

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
    credential_dir = os.path.expanduser('.')
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

def get_upcoming_event():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming event')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=1, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming event found.') 
    event = events[0]
    eventDict = dict()

    # name
    eventDict['name'] = event['summary']
    sonos_message = "Bonjour votre prochain rendez-vous est {}".format(eventDict['name'])

    # start
    start = event['start'].get('dateTime', event['start'].get('date'))
    eventDict['start'] = start
    
    # attendees
    attendeesNames = list()
    if 'attendees' in event:
        attendees = event['attendees']
        for attendeeInfo in attendees:
            for key, attendee in attendeeInfo.items():
                if key == 'displayName':
                    attendeesNames.append(attendee)
        eventDict['attendees'] = attendeesNames
    if len(attendeesNames) > 0:
        sonos_message = sonos_message + " avec {}".format(' '.join(attendeesNames))

    # location
    if 'location' in event:     
        eventDict['location'] = event['location']
        sonos_message = sonos_message + '. Vous devez vous rendre a {}'.format(eventDict['location'])

    sonos_message = sonos_message + " a {}.".format(eventDict['start'])

    print(sonos_message)

    response = requests.get("http://192.168.12.173:8080/api/speak/fr/{}".format(sonos_message))

    print(response.status_code)

    return response.url

if __name__ == '__main__':
    print(get_upcoming_event())
