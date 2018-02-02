from legistar.people import LegistarPersonScraper
import datetime
import re
from inspect import getmembers

from pupa.scrape import Person, Organization
from .util import *
from .const import ORGANIZATION_NAME

class OaklandPersonScraper(LegistarPersonScraper):
  # This page has a current list of council members but no real info beyond the name and dates.
  # TODO: Need to find a better page to scrape
  #MEMBERLIST = 'https://oakland.legistar.com/DepartmentDetail.aspx?ID=16958&GUID=2D327FEC-719C-41C0-B4E7-927B22957C03&R=39695131-3de7-453f-bf97-90e53ac5b592'
  MEMBERLIST = 'https://oakland.legistar.com/DepartmentDetail.aspx?ID=-1&GUID=15529D0E-EFE8-4C09-817E-CE554309072E&R=1a615ff6-c82c-49b2-8707-fa1d9d53a2b5'
  TIMEZONE = "US/Pacific"
  # ALL_MEMBERS = "8:8"

  def __init__(self, *args, **kwargs):
    super(LegistarPersonScraper, self).__init__(*args, **kwargs)

    self.committee_dict = {}
    self.people_dict = {}
    self.memberships = []

  def scrape(self):
    print('OaklandPersonScraper.scrape')
    print(self.jurisdiction)

    cnt = 0
    for councilman in self.councilMembers():
      print("###scrape - counclman:", councilman)

      department_name = parse_org(councilman.get('Department Name', ''))
      if department_name != '' and department_name not in self.committee_dict:
        source = self.MEMBERLIST if department_name != ORGANIZATION_NAME else 'https://oakland.legistar.com'

        org = create_organization(department_name, source)

        yield org

      person_name = councilman['Person Name']
      if person_name in self.people_dict:
        person = self.people_dict[person_name]
      else:
        assigned_district=self._assign_district(person_name)

        start_date = self._parse_date(councilman['Start Date'])
        end_date = self._parse_date(councilman['End Date'])
        
        person = Person(name=person_name,
                        district=assigned_district,
                        role="Councilmember",
                        primary_org="legislature",
                        start_date = start_date,
                        end_date = end_date)

        if person.name == 'Laurence E. Reid' or person.name == 'Larry Reid':
          person.name = 'Laurence E. Reid'
          person.add_name('Larry Reid')

        self.people_dict[person_name] = person

      start_date = self._parse_date(councilman['Start Date'])
      end_date = self._parse_date(councilman['End Date'])


      # term      
      title = councilman['Title']
      org_classification = get_classification(department_name)
      district=self._assign_district(person_name)

      if department_name != ORGANIZATION_NAME: 
        person.add_term(title, org_classification, start_date=start_date, end_date=end_date, org_name=department_name)
 
      # email
      if 'E-mail' in councilman and councilman['E-mail'] != '':
        if not self._has_contact_detail(person, 'email'):
          person.add_contact_detail(type="email",
                                    value=councilman['E-mail']['url'],
                                    note='E-mail')

      # website
      
      if 'Web Site' in councilman and 'url' in councilman['Web Site']:
        website_url = councilman['Web Site']['url']

        if not self._has_link(person, website_url):
          person.add_link(website_url, note='web site')

        if not self._has_source(person, website_url):
          person.add_source(website_url)

    for person_name, person in self.people_dict.items():
      print("###person", person_name)

      # make sure a person has at least one source
      if len(person.sources) == 0:
        person.add_source(self.MEMBERLIST)
        
      yield person


  def _has_contact_detail(self, person, contact_detail_type):
    for contact_detail in person.contact_details:
      if contact_detail['type'] == contact_detail_type:
        return True

      return False

  def _has_link(self, person, website_url):
    for link in person.links:
      if link['url'] == website_url:
        return True

    return False

  def _has_source(self, person, website_url):
    for sources in person.sources:
      if sources['url'] == website_url:
        return True

    return False
    
  # Place holder until we can scrape district info from somewhere
  def _assign_district(self, person_name):
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

  def _parse_date(self, raw_date):
    if raw_date == '':
      return ''

    raw_date = raw_date.replace('*', '')
    return self.toTime(raw_date).date().isoformat()
