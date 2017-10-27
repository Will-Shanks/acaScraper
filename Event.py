import re
import string
import hashlib
import logging


class Event:
    def __init__(self, Date, *args):
        if len(args) == 6:
            self.date = Date
            self.name = args[0]
            self.flyer = args[1].replace(' ', '%20')
            self.web = args[2]
            self.email = args[3]
            self.phone = args[4]
            self.ID = args[5]
            logging.debug('\tFound ' + self.name)
        elif len(args) == 1:
            args = args[0]
            self.date = Date
            self.getInfo(args)
            self.SetID()
            logging.debug('\tFound ' + self.name)
        else:
            logging.ERROR('Event constructor given wrong number of arguments from event' + str(Date) + ', ' + str(args))
            # raise Exception('Event constructor given wrong number of arguments from event' + str(Date) + ', ' + str(args))

    def GetName(self, event):
        eventName = re.findall(r'<h3>.*</h3>', event)
        eventName = str(eventName)
        eventName = eventName[6:len(eventName) - 7]
        self.name = eventName

    def GetFlyer(self, event):
        eventFlyer = re.findall(r'href="/sites/default/files/Site_Files/Race_Flyers/.*?"', event)
        eventFlyer = str(eventFlyer)
        eventFlyer = eventFlyer[8:len(eventFlyer) - 3]
        eventFlyer = 'https://www.coloradocycling.org' + eventFlyer
        self.flyer = eventFlyer.replace(' ', '%20')

    def GetWeb(self, event):
        eventWeb = re.findall(r'href="http://.*?" target="_blank">Promoter Website', event)
        eventWeb = str(eventWeb)
        eventWeb = eventWeb[8:len(eventWeb) - 36]
        self.web = eventWeb

    def GetEmail(self, event):
        eventEmail = re.findall(r'<a href="mailto:.*\.\w{3}">', event)
        eventEmail = str(eventEmail)
        eventEmail = eventEmail[18:len(eventEmail) - 4]
        self.email = eventEmail

    def GetPhone(self, event):
        eventPhone = re.findall(r'<dd>\d{3}\.\d{3}\.\d{4}</dd>', event)
        eventPhone = str(eventPhone)
        eventPhone = eventPhone[6:18]
        self.phone = eventPhone

    def SetID(self):
        eventID = self.date + self.name
        eventID = re.sub(r'\W+', '', eventID)
        eventID = eventID.lower()
        eventID = hashlib.md5(eventID.encode('utf-8')).hexdigest()
        self.ID = eventID

    def getInfo(self, event):
        self.GetName(event)
        self.GetFlyer(event)
        self.GetWeb(event)
        self.GetEmail(event)
        self.GetPhone(event)

    def info(self):
        return self.date + '","' + self.name + '","' + self.flyer + '","' + self.web + '","' + self.email + '","' + self.phone + '","' + self.ID
