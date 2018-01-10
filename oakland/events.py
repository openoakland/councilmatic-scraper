import datetime

from legistar.events import LegistarEventsScraper
from pupa.scrape import Event, Organization
from .util import *

import pickle

class OaklandEventScraper(LegistarEventsScraper):
  TIMEZONE = "US/Pacific"
  EVENTSPAGE = "https://oakland.legistar.com/Calendar.aspx"
  BASE_URL = "http://www2.oaklandnet.com/"

  def scrape(self):
    cutoff_year = self.now().year - 1
    index = 0

    for event, agenda in self.events(since=cutoff_year):
      print("###scrape - event:", event)
      print("###scrape - event['Meeting Location']:", event['Meeting Location'])
      print("###scrape - agenda:", agenda)

      """
      _agenda = None
      if agenda is not None:
        _agenda = [x for x in agenda]
        
      event_agenda = {'event': event, 'agenda': _agenda}
      pickle.dump(event_agenda, open("oakland/tests/data/event_agenda/event_agenda_%d.p" % index, "wb" ) )
      """

      index += 1      
      yield self._process_event_agenda(event, agenda)      

      """
      # debugging only
      if index < 30:
        yield self._process_event_agenda(event, agenda)
      else:
        raise StopIteration()
      """

  def _process_event_agenda(self, event, agenda):
    #event_name = event['Name'].replace('*', '')
    event_name = self._parse_event_name(event['Name'])
      
    event_date = self._parse_meeting_date(event['Meeting Date'], event['iCalendar']['url'])
    event_location = self._parse_meeting_location(event['Meeting Location'])
    
    status=self._parse_meeting_status(event_name, event_date, event['Meeting Time'])
    ocd_event = Event(name=event_name,
                      start_date=event_date,
                      # description=event['Meeting\xa0Topic'], # Appears no description is available in Oakland Legistar
                      location_name=event_location,
                      status=status)

    if event["Meeting Details"] != 'Not\xa0available' and event["Meeting Details"] != 'Meeting\xa0details':
      ocd_event.add_source(event["Meeting Details"]['url'], note='web')
    else:
      ocd_event.add_source(self.EVENTSPAGE)

    self.addDocs(ocd_event, event, 'Agenda')
    self.addDocs(ocd_event, event, 'Minutes')

    if event['Minutes'] != 'Not\xa0available':      #Adding Minutes
      ocd_event.add_media_link(note=event['Minutes']['label'],
                               url=event['Minutes']['url'],
                               media_type="application/pdf")

    # This code is per documentation; line above is from another city's code
    # #add a pdf of meeting minutes
    # ocd_event.add_media_link(note="Meeting minutes",
    #                 url="http://example.com/hearing/minutes.pdf",
    #                 media_type="application/pdf")

    # add an mpeg video
    if event['Video'] != 'Not\xa0available':
      ocd_event.add_media_link(note=event['Video']['label'],
                               url=event['Video']['url'],
                               media_type="video/mpeg")

    # add participating orgs
    participating_orgs = [parse_org(event_name)]

    # maybe this isn't necessary but leave it in case an event can have multiple committees in the future
    for org in participating_orgs:
      org = org.strip()

      ocd_event.add_committee(name=org)
      ocd_event.validate()

    #add a person
    #ocd_event.add_person(name="Dan Kalb", note="Hearing Chair")

    # #add an agenda item to this event
    # a = ocd_event.add_agenda_item(description="Testimony from concerned citizens")
    
    # #the testimony is about transportation and the environment
    # a.add_subject("Transportation")
    # a.add_subject("Environment")

    # #and includes these two committees
    # a.add_committee("Transportation")
    # a.add_committee("Environment and Natural Resources")
    
    # #these people will be present
    # a.add_person("Jane Brown")
    # a.add_person("Alicia Jones")
    # a.add_person("Fred Green")
    
    # #they'll be discussing this bill
    # a.add_bill("HB101")
    
    # #here's a document that is included
    # a.add_media_link(note="Written version of testimony",
    #                 url="http://example.com/hearing/testimony.pdf",
    #                 media_type="application/pdf")

    print("###scraper - ocd_event:", ocd_event)

    yield ocd_event

  def _parse_event_name(self, raw_event_name):
    return remove_multiple_spaces(raw_event_name.replace('*', ''))
      
  def _parse_meeting_date(self, date_str, ical_url):
    event_date = self.toTime(date_str)
    response = self.get(ical_url, verify=False)
    event_time = self.ical(response.text).subcomponents[0]['DTSTART'].dt
    event_date = event_date.replace(hour=event_time.hour,
                                    minute=event_time.minute)
    return event_date

  def _parse_meeting_location(self, location_str):
    location_str = location_str.split('\n')[0]
    
    if location_str == '':
      # Location is required but some events have no location given.
      location_str = 'UNKNOWN'
      
    return location_str 

  def _parse_meeting_status(self, event_name, event_date, meeting_time_str):
    if 'cancel' in event_name.lower() or meeting_time_str.lower() in ('deferred', 'cancelled'):
      status = 'cancelled'
    elif self.now() < event_date:
      status = 'confirmed'
    else:
      status = 'passed'

    return status

