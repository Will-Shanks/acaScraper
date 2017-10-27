from __future__ import print_function
import logging
from secrets import CAL_ID

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime


class GoCal:
    def __init__(self):
        try:
            import argparse
            self.flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        except ImportError:
            self.flags = None

        # If modifying these scopes, delete your previously saved credentials
        # at ~/.credentials/calendar-python-quickstart.json
        self.SCOPES = 'https://www.googleapis.com/auth/calendar'
        self.CLIENT_SECRET_FILE = 'client_secret.json'
        self.APPLICATION_NAME = 'Google Calendar API Python Quickstart'

        self.credentials = self.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = service = discovery.build('calendar', 'v3', http=self.http)
        # Cal ID for my personal 'RAGE' google calendar
        self.CalID = CAL_ID


    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """

        store = Storage('calendar-python.json')  # credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            logging.critical('No valid credentials found')
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            # flow = client.flow_from_clientsecrets('client_secret.json', 'https://www.googleapis.com/auth/calendar')
            flow.user_agent = self.APPLICATION_NAME
            if self.flags:
                credentials = tools.run_flow(flow, store, self.flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            # print('Storing credentials')  # to ' + credential_path)
        return credentials

    def add(self, event):
        logging.debug('Adding ' + event.name)
        try:
            self.service.events().insert(calendarId=self.CalID, body=self.eventinfo(event)).execute()
            logging.debug('Added Sucessfully')
        except Exception:
            logging.warning('Failed to add ' + event.name + 'Trying to update ' + event.name + ' instead')
            self.update(event)

    def update(self, event):
        logging.debug('Updating ' + event.name)
        try:
            self.service.events().update(calendarId=self.CalID, eventId=event.ID, body=self.eventinfo(event)).execute()
            logging.debug('Update Sucessfull')
        except Exception:
            logging.warning('Failed to update ' + event.name)

    def remove(self, event):
        logging.debug('Deleting ' + event.name)
        try:
            self.service.events().delete(calendarId=self.CalID, eventId=event.ID).execute()
        except Exception:
            logging.warning('Failed to delete ' + event.name + ' on ' + event.date)

    def eventinfo(self, event):
        eventDate = event.date[6:10] + '-' + event.date[0:5]
        info = 'To find out more go to\n' + event.flyer
        if event.email or event.phone:
            contact = '\nYou can contact the promoter by\n'
            if event.email:
                contact += 'email at\n' + event.email + '\n'
            if event.phone:
                contact += 'phone at\n' + event.phone + '\n'
            info += contact
        if event.web:
            info += 'To find out about the promoter go to\n' + event.web
        calEvent = {
            'id': event.ID,
            'summary': event.name,
            'start': {
                'date': eventDate,
                'timeZone': 'America/Denver',
            },
            'end': {
                'date': eventDate,
                'timeZone': 'America/Denver',
            },
            'description': info,
        }
        return calEvent
