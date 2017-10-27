from __future__ import print_function
import datetime
import logging
from Event import Event


class Schedule:
    def __init__(self):
        self.events = list()

    def addEvent(self, event):
        self.events.append(event)

    def update(self):
        currDate = datetime.datetime.now().strftime("%m.%d.%Y")
        iToDel = list()
        for i in range(0, len(self.events) - 1):
            try:
                eventDate = self.events[i].date
                strCurrDate = (str(currDate[6:10]) + str(currDate[0:2]) + str(currDate[3:5]))
                strEventDate = (str(eventDate[6:10]) + str(eventDate[0:2]) + str(eventDate[3:5]))
                if (int(strEventDate) < int(strCurrDate)):
                    iToDel.append(i)
            except(IndexError):
                logging.ERROR('Index Error from event ' + str(i))
                self.update(log)
            except(AttributeError):
                logging.ERROR("event " + str(i) + " AttributeError")
                del self.events[i]
                self.update(log)
        for i in reversed(iToDel):
            logging.debug('Ignoring ' + self.events[i].name + ' as it happened on ' + self.events[i].date)
            del self.events[i]

    def checkChanges(self, other):
        newEvents = list()
        updatedEvents = list()
        delEvents = list()
        for myEvent in self.events:
            isEvent = False
            isUpdated = False
            for otherEvent in other.events:
                if myEvent.ID == otherEvent.ID:
                    isEvent = True
                    if myEvent.flyer != otherEvent.flyer or myEvent.web != otherEvent.web or myEvent.email != otherEvent.email or myEvent.phone != otherEvent.phone:
                        isUpdated = True
                    break

            if isEvent:
                if isUpdated:
                    logging.info(myEvent.name + ' has been updated')
                    updatedEvents.append(myEvent)
            else:
                logging.info(myEvent.name + ' has been added to the schedule on ' + myEvent.date)
                newEvents.append(myEvent)

        for otherEvent in other.events:
            isThere = False
            for myEvent in self.events:
                if otherEvent.name == myEvent.name and otherEvent.date == myEvent.date:
                    isThere = True
                    break
            if not isThere:
                logging.info(otherEvent.name + ' on ' + otherEvent.date + ' has been removed from the schedule')
                delEvents.append(otherEvent)
        self.newEvents = newEvents
        self.updatedEvents = updatedEvents
        self.delEvents = delEvents

    def save(self):
        with open('Events.csv', 'w') as f:
            for event in self.events:
                logging.debug('Saving ' + event.name)
                print (event.info(), file=f)
