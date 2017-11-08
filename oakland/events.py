import datetime

from legistar.events import LegistarEventsScraper
from pupa.scrape import Event, Organization

class OaklandEventScraper(LegistarEventsScraper):
  TIMEZONE = "US/Pacific"
  EVENTSPAGE = "https://oakland.legistar.com/Calendar.aspx"
  BASE_URL = "http://www2.oaklandnet.com/"

  def scrape(self):
    current_year= self.now().year
    index = 0

    for event, agenda in self.events(since=current_year):
      index += 1
      print(event)
      print(agenda)

      event_name = event['Name'].replace('*', '')
      event_date = self.__parse_meeting_date(event['Meeting Date'], event['iCalendar']['url'])
      event_location = self.__parse_meeting_location(event['Meeting Location'])
      ocd_event = Event(name=event_name,
                        start_date=event_date,
                        # description=event['Meeting\xa0Topic'], # Appears no description is available in Oakland Legistar
                        location_name=event_location,
                        status=self.__parse_meeting_status(event_name, event_date, event['Meeting Time']))


      if event["Meeting Details"] != 'Not\xa0available' and event["Meeting Details"] != 'Meeting\xa0details':
        ocd_event.add_source(event["Meeting Details"]['url'], note='web')
      else:
        ocd_event.add_source(self.EVENTSPAGE)

      self.addDocs(ocd_event, event, 'Agenda')
      self.addDocs(ocd_event, event, 'Minutes')
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
      participating_orgs = self.__parse_participating_orgs(event_name)
      print("###event_name: %s" % event_name)
      
      for org in participating_orgs:
        print("###org: %s" % org)
        ocd_event.add_committee(name=org)
        ocd_event.validate()

      # #add a person
      # ocd_event.add_person(name="Joe Smith", note="Hearing Chair")

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

      print(ocd_event)

      yield ocd_event

      """
      if index < 5:
        yield ocd_event
      else:
        raise StopIteration()
      """

  def __parse_meeting_date(self, date_str, ical_url):
    event_date = self.toTime(date_str)
    response = self.get(ical_url, verify=False)
    event_time = self.ical(response.text).subcomponents[0]['DTSTART'].dt
    event_date = event_date.replace(hour=event_time.hour,
                                    minute=event_time.minute)
    return event_date

  def __parse_meeting_location(self, location_str):
    return location_str.split('\n')[0]

  def __parse_meeting_status(self, event_name, event_date, meeting_time_str):
    if event_name.lower().find('cancelled') or meeting_time_str.lower() in ('deferred', 'cancelled'):
      status = 'cancelled'
    elif self.now() < event_date:
      status = 'confirmed'
    else:
      status = 'passed'

    return status

  def __parse_participating_orgs(self, event_name):
    orgs = []
    org_str = event_name.replace("Concurrent Meeting of the", '')
    org_tokens = org_str.split('and_the')

    for org_token in org_tokens:      
      # org = None
      org_name = org_token
      org_type = 'committee'

      if org_token == 'City Council':
        org_name = 'Oakland City Council'
        org_type = 'legislature'

      org_name = org_name.replace("- CANCELLED", '')
      orgs.append(org_name)

    return orgs

