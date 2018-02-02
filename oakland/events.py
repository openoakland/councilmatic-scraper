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
    other_orgs = ''

    location_string = event[u'Meeting Location'] 
      
    event_location = self._parse_meeting_location(event['Meeting Location'])
    response = self.get(event['iCalendar']['url'], verify=False)
      
    event_date = self._parse_meeting_date(event['Meeting Date'], event['iCalendar']['url'])
    event_name = self._parse_event_name(event['Name'])
    status=self._parse_meeting_status(event_name, event_date, event['Meeting Time'])
    description = event.get('Meeting\xa0Topic', '')
      
    e = Event(name=event_name, start_date=event_date, description=description, location_name=event_location, status=status)

    extras = self._parse_extras(event[u'Meeting Location'])
    if extras is not None:
      e.extras = extras
        
    # minutes
    minutes = event.get('Minutes', None)
    if minutes is not None and minutes != 'Not\xa0available':      
      e.add_media_link(note=minutes['label'], url=minutes['url'], media_type="application/pdf")

    # video
    video = event.get('Video', None)
    if video is not None and video != 'Not\xa0available':
      e.add_media_link(note=video['label'], url=video['url'], media_type="video/mpeg")
          
    # multimedia
    multimedia = event.get('Multimedia', None)
    if multimedia is not None and multimedia != 'Not\xa0available' :
      url = multimedia.get('url', None)
        
      if url is not None:
        e.add_media_link(note='Recording', url = url, type="recording", media_type = 'text/html')

    self.addDocs(e, event, 'Agenda')
    self.addDocs(e, event, 'Minutes')

    if event['Name'] == 'City Council Stated Meeting' :
      participating_orgs = ['Oakland City Council']
    elif 'committee' in event['Name'].lower() :
      participating_orgs = [event["Name"]]
    else :
      participating_orgs = []

    if other_orgs : 
      other_orgs = re.sub('Jointl*y with the ', '', other_orgs)
      participating_orgs += re.split(' and the |, the ', other_orgs)
          
    for org in participating_orgs :
      e.add_committee(name=parse_org(org))

    if agenda is not None:
      e.add_source(event["Meeting Details"]['url'], note='web')
                
      for item, _, _ in agenda :
        if item["Name"] :
          agenda_item = e.add_agenda_item(item["Name"])
          if item["File\xa0#"] :
            if item['Action'] :
              note = item['Action']
            else :
              note = 'consideration'
              agenda_item.add_bill(item["File\xa0#"]['label'], note=note)
    else :
      e.add_source(self.EVENTSPAGE, note='web')

    yield e

  def _parse_event_name(self, raw_event_name):
    return remove_multiple_spaces(raw_event_name.replace('*', ''))
      
  def _parse_meeting_date(self, date_str, ical_url):
    event_date = self.toTime(date_str)
    response = self.get(ical_url, verify=False)
    event_time = self.ical(response.text).subcomponents[0]['DTSTART'].dt
    event_date = event_date.replace(hour=event_time.hour, minute=event_time.minute)
    
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

  def _parse_extras(self, meeting_location):
    extras = []

    if '--em--' in meeting_location:
      location_string, note = meeting_location.split('--em--')[:2]
      for each in note.split(' - ') :
        if each.startswith('Join') :
          other_orgs = each
        else :
          extras.append(each)

    if len(extras) > 0:
      return {'location note' : ' '.join(extras)}
    else:
      return None
            
