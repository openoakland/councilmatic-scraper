from legistar.people import LegistarPersonScraper
import datetime
import re
from inspect import getmembers

from pupa.scrape import Person, Organization

class OaklandPersonScraper(LegistarPersonScraper):
  # This page has a current list of council members but no real info beyond the name and dates.
  # TODO: Need to find a better page to scrape
  MEMBERLIST = 'https://oakland.legistar.com/DepartmentDetail.aspx?ID=16958&GUID=2D327FEC-719C-41C0-B4E7-927B22957C03&R=39695131-3de7-453f-bf97-90e53ac5b592'
  TIMEZONE = "US/Pacific"
  # ALL_MEMBERS = "8:8"

  def scrape(self):
    print('OaklandPersonScraper.scrape')
    print(self.jurisdiction)

    for councilman in self.councilMembers():
      assigned_district=self.__assign_district(councilman['Person Name'])
      start_date = self.toTime(councilman['Start Date']).date()
      end_date = self.toTime(councilman['End Date']).date()
      person = Person(name=councilman['Person Name'],
                district=assigned_district,
                role="Councilmember",
                primary_org="legislature",
                start_date=start_date.isoformat(),
                 end_date=end_date)

      if councilman["E-mail"]:
        person.add_contact_detail(type="email",
                             value=councilman['E-mail']['url'],
                             note='E-mail')

      # Assigning
      website_url = self.MEMBERLIST

      if councilman['Web site']:
        councilman['Web site']['url']

      person.add_link(website_url, note='web site')
      person.add_source(website_url)
      yield person

  # Place holder until we can scrape district info from somewhere
  def __assign_district(self, person_name):
    districts = {
      "Dan Kalb": "Council District 1",
      "Abel J. Guillén": "Council District 2",
      "Lynette Gibson McElhaney": "Council District 3",
      "Annie Campbell Washington": "Council District 4",
      "Noel Gallo": "Council District 5",
      "Desley Brooks": "Council District 6",
      "Larry Reid": "Council District 7",
      "Rebecca Kaplan": "Councilmember At Large"
    }
    return districts.get(person_name)
