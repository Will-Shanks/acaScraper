from __future__ import print_function
import logging
import re
import requests
import os
from datetime import datetime
from Event import Event
from Schedule import Schedule
from GoCal import GoCal


def GetDate(day):
    eventDate = re.findall(r'>\d{2} - \d{2} - \d{4}<', day)
    eventDate = str(eventDate)
    eventDate = eventDate[3:5] + '-' + eventDate[8:10] + '-' + eventDate[13:17]
    return eventDate


def getEventDays():
    response = requests.get('https://www.coloradocycling.org/calendar')  # urllib2.urlopen('https://www.coloradocycling.org/calendar')
    html = response.text
    eventDays = re.findall(r'ID-has-event \w{3} is-current.*?</ul>\s+</div>\s+</div>', html, re.DOTALL)
    return eventDays


def getCurrentEvents(Sched):
    eventDays = getEventDays()               # returns html from days with races
    for day in eventDays:                     # populates Races
        Date = GetDate(day)                   # finds the date of the day its going through
        events = re.findall(r'<li class=.*?>\s+<h3>.*?</h3>.*?</li>', day, re.DOTALL)  # goes through day's html and finds html important to each race that day
        for event in events:                  # goes through each event and creates an Event object with relevent data
            race = Event(Date, event)
            Sched.addEvent(race)


def getOldEvents(Sched):
    # open file then close it to ensure it exists
    open('Events.csv', 'a').close()
    with open('Events.csv', 'r') as f:
        for line in f:
            line = line.strip('\n')
            info = line.split('","')
            race = Event(*info)
            Sched.addEvent(race)


def emailLog(currTime):
    import smtplib

    with open(currTime.strftime('Logs/%Y-%m-%d.log'), 'r') as f:
        msg = f.read()

    gmail_user = ''
    gmail_pwd = ''
    FROM = ''
    TO = ['']
    SUBJECT = 'ACA Scraper Status'
    TEXT = msg

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
    except Exception:
        pass


def main():
    if not os.path.exists('Logs'):
        try:
            os.makedirs('Logs')
        except OSError:
            print("Failure to create Logs directory")

    currTime = datetime.now()
    logging.basicConfig(filename=currTime.strftime('Logs/%Y-%m-%d.log'), format='%(levelname)s: %(asctime)s %(module)s %(funcName)s %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
    logging.debug('############################## START OF PROGRAM ##############################')
    currSched = Schedule()
    oldSched = Schedule()
    logging.debug('Searching for events on BRAC Calendar')
    getCurrentEvents(currSched)          # Fills currSched with Event objects for each event on BRAC calendar
    logging.debug('Found ' + str(len(currSched.events)) + ' current events on BRAC Calendar')
    logging.debug('Checking Events.csv for saved Events')
    getOldEvents(oldSched)               # Fill oldSched with Event objects for each line in Events.csv
    logging.debug('Found ' + str(len(oldSched.events)) + ' current events in Records')
    logging.debug('Removing old events from list')
    currSched.update()                   # Gets rid of any events that already happened
    oldSched.update()                    # Gets rid of any events that already happened
    logging.debug('Finding diferences between BRAC calendar and saved calendar')
    currSched.checkChanges(oldSched)     # Finds any changes in schedule and notifies user
    if currSched.newEvents == [] and currSched.updatedEvents == [] and currSched.delEvents == []:
        logging.info('No Changes to Calendar were found')

    try:
        if currSched.newEvents or currSched.updatedEvents or currSched.delEvents:
            logging.info('Updating Google Calendar')
            Cal = GoCal()
            if currSched.newEvents:
                for event in currSched.newEvents:
                    Cal.add(event)
            if currSched.updatedEvents:
                for event in currSched.updatedEvents:
                    Cal.update(event)
            if currSched.delEvents:
                for event in currSched.delEvents:
                    Cal.remove(event)
    except Exception:
        logging.error('Google Calendar failed to update')

    logging.debug('Updating Events.csv with current BRAC calendar listings')
    currSched.save()                     # saves currSched to Events.csv updating local schedule

    logging.debug('############################## END OF PROGRAM ##############################\n\n\n')

    if(int(currTime.strftime('%H')) >= 18):
        emailLog(currTime)

    return 0


if __name__ == '__main__':
    pass
    import sys
    sys.exit(main())
